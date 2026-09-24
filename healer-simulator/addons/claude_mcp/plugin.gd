@tool
extends EditorPlugin
## Bruecke fuer den Claude-Code-MCP-Server (~/.claude/godot-mcp/server.py).
##
## Lauscht auf 127.0.0.1:<CLAUDE_MCP_PORT|9877> und erwartet null-byte-terminiertes JSON:
##     {"type": "execute", "code": "<gdscript>"} | {"type": "ping"}
## Antwort (ebenfalls null-byte-terminiert):
##     {"status": "ok", "result": ..., "log": [...]} | {"status": "error", "message": "...", "log": [...]}
##
## `code` ist entweder ein Funktionsrumpf (wird in `func run():` eingebettet) oder ein
## kompletter Klassenrumpf, der selbst `func run():` definiert. Der Rueckgabewert von run()
## wird als JSON zurueckgegeben; `await` ist erlaubt, `plugin` zeigt auf dieses EditorPlugin.

const HOST := "127.0.0.1"
const DEFAULT_PORT := 9877

var _server: TCPServer
var _clients: Array[Dictionary] = []
var _capture := _Capture.new()
var _full_script_re := RegEx.create_from_string("(?m)^func\\s+run\\s*\\(")


class _Capture extends Logger:
	var active := false
	var lines := PackedStringArray()
	var _mutex := Mutex.new()

	func _add(text: String) -> void:
		_mutex.lock()
		if active:
			lines.append(text.strip_edges(false, true))
		_mutex.unlock()

	func begin() -> void:
		_mutex.lock()
		lines = PackedStringArray()
		active = true
		_mutex.unlock()

	func finish() -> PackedStringArray:
		_mutex.lock()
		active = false
		var out := lines
		lines = PackedStringArray()
		_mutex.unlock()
		return out

	func _log_message(message: String, error: bool) -> void:
		_add(("[stderr] " if error else "") + message)

	func _log_error(function: String, file: String, line: int, code: String, rationale: String,
			editor_notify: bool, error_type: int, script_backtraces: Array[ScriptBacktrace]) -> void:
		var kind: String = ["ERROR", "WARNING", "SCRIPT ERROR", "SHADER ERROR"][clampi(error_type, 0, 3)]
		var text := rationale if not rationale.is_empty() else code
		_add("%s: %s (%s:%d in %s)" % [kind, text, file, line, function])


func _enter_tree() -> void:
	OS.add_logger(_capture)
	var port := int(OS.get_environment("CLAUDE_MCP_PORT")) if OS.has_environment("CLAUDE_MCP_PORT") else DEFAULT_PORT
	_server = TCPServer.new()
	var err := _server.listen(port, HOST)
	if err != OK:
		push_error("Claude MCP: kann nicht auf %s:%d lauschen (%s)" % [HOST, port, error_string(err)])
		_server = null
		return
	print("Claude MCP: lauscht auf %s:%d" % [HOST, port])


func _exit_tree() -> void:
	for c in _clients:
		c.peer.disconnect_from_host()
	_clients.clear()
	if _server:
		_server.stop()
		_server = null
	OS.remove_logger(_capture)


func _process(_delta: float) -> void:
	if _server == null:
		return
	while _server.is_connection_available():
		_clients.append({"peer": _server.take_connection(), "buf": PackedByteArray(), "busy": false})

	for c in _clients.duplicate():
		var peer: StreamPeerTCP = c.peer
		peer.poll()
		var status := peer.get_status()
		if status == StreamPeerTCP.STATUS_CONNECTING:
			continue
		if status != StreamPeerTCP.STATUS_CONNECTED:
			_clients.erase(c)
			continue
		var buf: PackedByteArray = c.buf
		var available := peer.get_available_bytes()
		if available > 0:
			var chunk := peer.get_partial_data(available)
			if chunk[0] == OK:
				buf.append_array(chunk[1])
		if c.busy:
			c.buf = buf
			continue
		var end := buf.find(0)
		if end >= 0:
			var message := buf.slice(0, end).get_string_from_utf8()
			c.buf = buf.slice(end + 1)
			c.busy = true
			_serve(c, message)
		else:
			c.buf = buf


func _serve(client: Dictionary, message: String) -> void:
	var response: Dictionary = await _handle(message)
	var peer: StreamPeerTCP = client.peer
	if peer.get_status() == StreamPeerTCP.STATUS_CONNECTED:
		var out := JSON.stringify(response).to_utf8_buffer()
		out.append(0)
		peer.put_data(out)
	client.busy = false


func _handle(message: String) -> Dictionary:
	var request = JSON.parse_string(message)
	if typeof(request) != TYPE_DICTIONARY:
		return {"status": "error", "message": "Ungueltiges JSON"}
	match request.get("type", ""):
		"ping":
			return {"status": "ok", "result": {"godot": Engine.get_version_info().string}}
		"execute":
			return await _execute(str(request.get("code", "")))
	return {"status": "error", "message": "Unbekannter Typ: %s" % request.get("type")}


func _execute(code: String) -> Dictionary:
	var header := "@tool\nextends RefCounted\n\nvar plugin: EditorPlugin\n\n"
	var source := header
	if _full_script_re.search(code):
		source += code
	else:
		var lines := Array(code.split("\n"))
		var indent := "\t"
		if not lines.any(func(l: String) -> bool: return l.begins_with("\t")) \
				and lines.any(func(l: String) -> bool: return l.begins_with(" ")):
			indent = "    "
		source += "func run():\n"
		for line in lines:
			source += indent + line + "\n"

	_capture.begin()
	var script := GDScript.new()
	script.source_code = source
	var err := script.reload()
	if err != OK:
		return {"status": "error", "message": "Kompilierfehler (%s)" % error_string(err), "log": _capture.finish()}

	var instance = script.new()
	instance.plugin = self
	var result = await instance.run()
	var logs := _capture.finish()
	var failed := false
	for line in logs:
		if line.begins_with("SCRIPT ERROR") or line.begins_with("ERROR"):
			failed = true
	return {"status": "error" if failed else "ok", "result": _to_json(result), "log": logs}


func _to_json(value: Variant, depth := 0) -> Variant:
	if depth > 10:
		return str(value)
	match typeof(value):
		TYPE_NIL, TYPE_BOOL, TYPE_INT, TYPE_STRING:
			return value
		TYPE_FLOAT:
			return value if is_finite(value) else str(value)
		TYPE_STRING_NAME, TYPE_NODE_PATH:
			return str(value)
		TYPE_DICTIONARY:
			var d := {}
			for key in value:
				d[str(key)] = _to_json(value[key], depth + 1)
			return d
		TYPE_OBJECT:
			if not is_instance_valid(value):
				return null
			if value is Node:
				return {"node": str(value.get_path()) if value.is_inside_tree() else str(value.name), "class": value.get_class()}
			if value is Resource:
				return {"resource": value.resource_path, "class": value.get_class()}
			return str(value)
	if typeof(value) >= TYPE_ARRAY:
		var a := []
		for item in value:
			a.append(_to_json(item, depth + 1))
		return a
	return var_to_str(value)
