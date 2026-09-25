extends Node
## Speicherstaende: ein JSON pro Charakter in <base_dir>/characters/ und die Reihenfolge
## der Charakterliste in <base_dir>/roster.json. Wird automatisch gespeichert.

signal roster_changed

var _characters := {}        # id -> Dictionary
var _order: Array = []       # ids in Anzeigereihenfolge
var last_selected := ""


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(_char_dir())
	_load_all()


func _char_dir() -> String:
	return Settings.base_dir + "characters/"


func _roster_path() -> String:
	return Settings.base_dir + "roster.json"


func _load_all() -> void:
	_characters.clear()
	var dir := DirAccess.open(_char_dir())
	if dir:
		for file_name in dir.get_files():
			if not file_name.ends_with(".json"):
				continue
			var f := FileAccess.open(_char_dir() + file_name, FileAccess.READ)
			if f == null:
				continue
			var data = JSON.parse_string(f.get_as_text())
			if data is Dictionary and data.has("id"):
				_characters[data["id"]] = _sanitize(data)
	var order: Array = []
	var roster = _read_json(_roster_path())
	if roster is Dictionary:
		order = roster.get("order", [])
		last_selected = str(roster.get("last_selected", ""))
	# Reihenfolge bereinigen und fehlende Charaktere (nach Erstellzeit) anhaengen
	_order = []
	for id in order:
		if _characters.has(id) and not id in _order:
			_order.append(id)
	var rest: Array = []
	for id in _characters:
		if not id in _order:
			rest.append(_characters[id])
	rest.sort_custom(func(a, b): return int(a.get("created", 0)) < int(b.get("created", 0)))
	for c in rest:
		_order.append(c["id"])
	if not _characters.has(last_selected):
		last_selected = _order[0] if _order.size() > 0 else ""


## JSON kennt nur Kommazahlen - ganzzahlige Felder wieder zu int machen.
const INT_FIELDS := ["version", "skin", "hair_style", "hair_color", "level", "xp", "gold", "created",
	"world", "wave", "highest_world", "highest_wave"]


func _sanitize(c: Dictionary) -> Dictionary:
	for key in INT_FIELDS:
		if c.has(key):
			c[key] = int(c[key])
	for m in c.get("group", []):
		for key in INT_FIELDS:
			if m.has(key):
				m[key] = int(m[key])
	return c


func _read_json(path: String):
	if not FileAccess.file_exists(path):
		return null
	var f := FileAccess.open(path, FileAccess.READ)
	return JSON.parse_string(f.get_as_text()) if f else null


func _write_json(path: String, data) -> void:
	var tmp := path + ".tmp"
	var f := FileAccess.open(tmp, FileAccess.WRITE)
	if f == null:
		push_error("Speichern fehlgeschlagen: %s" % path)
		return
	f.store_string(JSON.stringify(data, "\t"))
	f.close()
	# erst vollstaendig schreiben, dann ersetzen - ein Absturz hinterlaesst keine halbe Datei
	if FileAccess.file_exists(path):
		DirAccess.remove_absolute(path)
	DirAccess.rename_absolute(tmp, path)


func _save_roster() -> void:
	_write_json(_roster_path(), {"order": _order, "last_selected": last_selected})


# ---------------------------------------------------------------- oeffentlich
func count() -> int:
	return _order.size()


func is_full() -> bool:
	return count() >= GameData.MAX_CHARACTERS


func list() -> Array:
	var out: Array = []
	for id in _order:
		out.append(_characters[id])
	return out


func get_character(id: String) -> Dictionary:
	return _characters.get(id, {})


func names() -> Array:
	var out: Array = []
	for id in _order:
		out.append(_characters[id]["name"])
	return out


func add_character(c: Dictionary) -> void:
	_characters[c["id"]] = c
	_order.append(c["id"])
	last_selected = c["id"]
	save_character(c)
	_save_roster()
	roster_changed.emit()


## Liest einen Charakter neu von der Festplatte (verwirft ungespeicherte Aenderungen, z. B. einer abgebrochenen Welle).
func reload_character(id: String) -> Dictionary:
	var data = _read_json(_char_dir() + "%s.json" % id)
	if data is Dictionary and data.has("id"):
		_characters[id] = _sanitize(data)
	return _characters.get(id, {})


func save_character(c: Dictionary) -> void:
	_characters[c["id"]] = c
	_write_json(_char_dir() + "%s.json" % c["id"], c)


func delete_character(id: String) -> void:
	if not _characters.has(id):
		return
	var idx := _order.find(id)
	_characters.erase(id)
	_order.erase(id)
	var path := _char_dir() + "%s.json" % id
	if FileAccess.file_exists(path):
		DirAccess.remove_absolute(path)
	if last_selected == id:
		last_selected = "" if _order.is_empty() else _order[clampi(idx, 0, _order.size() - 1)]
	_save_roster()
	roster_changed.emit()


func move_character(id: String, new_index: int) -> void:
	var old := _order.find(id)
	if old == -1:
		return
	_order.remove_at(old)
	new_index = clampi(new_index, 0, _order.size())
	_order.insert(new_index, id)
	_save_roster()
	roster_changed.emit()


func set_last_selected(id: String) -> void:
	if last_selected != id and _characters.has(id):
		last_selected = id
		_save_roster()
