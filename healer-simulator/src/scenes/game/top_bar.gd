class_name TopBar
extends Control
## Obere Leiste (GDD 7.2): Weltname, Wellen-Anzeige (10 Punkte, Bosswelle mit Totenkopf,
## geschaffte Wellen anklickbar), Schalter Auto-Weiter / Welle wiederholen, Karte und Raids (gesperrt).
## Alles ist als Gruppe mittig ausgerichtet. Im Hardcore-Modus haengt darunter der Regler fuer die Mana-Schwelle.
## Optisch bewusst anders als die untere Leiste: warmes Holz mit Goldkante statt dunklem Violett.

signal wave_clicked(index: int)
signal auto_changed(on: bool)
signal repeat_changed(on: bool)
signal threshold_changed(value: int)

const H := 20
const DOT := 11
const DOT_STEP := 14
const GAP := 14                  # Abstand zwischen den Gruppen (mit Trennstrich)
const BASELINE := 14             # Grundlinie der Schrift: Glyphen liegen mittig in der Leiste
const WOOD_TOP := Color("4a3424")
const WOOD_BOTTOM := Color("2e2018")

var world_n := 1
var wave_count := 10
var current := 1
var unlocked := 1
var done_up_to := 0
var boss_waves: Array = []
var hardcore := false

var _world_text := ""
var _world_x := 0.0
var _dots_x := 0.0
var _dividers: Array = []
var _auto: TopToggle
var _repeat: TopToggle
var _map: LockedIcon
var _raids: LockedIcon
var _hc_row: Control
var _hc_slider: HSlider
var _hc_value: Label
var _hover_dot := -1
var _tex := {}
var _t := 0.0


func _init() -> void:
	position = Vector2.ZERO
	size = Vector2(640, H)
	mouse_filter = Control.MOUSE_FILTER_PASS
	for n in ["wave_locked", "wave_open", "wave_done", "wave_boss_locked", "wave_boss_open", "wave_boss_done", "wave_current"]:
		_tex[n] = Hud.combat_tex(n)
	_auto = TopToggle.new("TOP_AUTO", "TOP_AUTO_TIP")
	_auto.toggled.connect(func(on):
		if on:
			_repeat.set_on(false)
		auto_changed.emit(on))
	add_child(_auto)
	_repeat = TopToggle.new("TOP_REPEAT", "TOP_REPEAT_TIP")
	_repeat.toggled.connect(func(on):
		if on:
			_auto.set_on(false)
		repeat_changed.emit(on))
	add_child(_repeat)
	_map = LockedIcon.new("icon_map", "TOP_MAP_LOCKED", Vector2(16, 16))
	add_child(_map)
	_raids = LockedIcon.new("icon_raid", "TOP_RAIDS_LOCKED", Vector2(16, 16))
	add_child(_raids)
	_build_hc_row()


func _build_hc_row() -> void:
	# Haengt als kleines Holzschild unter der Leiste (nur Hardcore)
	_hc_row = HcPlate.new()
	_hc_row.size = Vector2(196, 15)
	_hc_row.position = Vector2(640 - 196 - 4, H)
	_hc_row.visible = false
	add_child(_hc_row)
	var l := UI.label("TOP_HC_THRESHOLD", "HardcoreLabel")
	l.position = Vector2(5, 2)
	l.size = Vector2(104, 10)
	l.tooltip_text = "TOP_HC_THRESHOLD_TIP"
	l.mouse_filter = Control.MOUSE_FILTER_PASS
	_hc_row.add_child(l)
	_hc_slider = HSlider.new()
	_hc_slider.min_value = 0
	_hc_slider.max_value = 100
	_hc_slider.step = 5
	_hc_slider.focus_mode = Control.FOCUS_NONE
	_hc_slider.position = Vector2(110, 2)
	_hc_slider.size = Vector2(48, 10)
	_hc_slider.tooltip_text = "TOP_HC_THRESHOLD_TIP"
	_hc_slider.value_changed.connect(func(v):
		_hc_value.text = "%d%%" % int(v)
		threshold_changed.emit(int(v)))
	_hc_row.add_child(_hc_slider)
	_hc_value = UI.label("", "", HORIZONTAL_ALIGNMENT_RIGHT)
	_hc_value.position = Vector2(158, 2)
	_hc_value.size = Vector2(34, 10)
	_hc_row.add_child(_hc_value)


func setup(world: int, count: int, is_hardcore: bool, auto_on: bool, repeat_on: bool, threshold: int) -> void:
	world_n = world
	wave_count = count
	hardcore = is_hardcore
	boss_waves = []
	for i in range(1, count + 1):
		if CombatData.is_boss_wave(world, i):
			boss_waves.append(i)
	var lv: Array = GameData.WORLD_LEVELS.get(world, [1, 1])
	_world_text = "%s (%d-%d)" % [Loc.world_name(world), lv[0], lv[1]]
	_auto.set_on(auto_on)
	_repeat.set_on(repeat_on)
	_hc_row.visible = hardcore
	_hc_slider.set_value_no_signal(threshold)
	_hc_value.text = "%d%%" % threshold
	_layout()


## Ordnet alle Elemente als eine mittig ausgerichtete Gruppe an.
func _layout() -> void:
	var font := UiTheme.font_body
	var world_w := font.get_string_size(_world_text, HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.BODY_SIZE).x
	var dots_w := wave_count * DOT_STEP - (DOT_STEP - DOT)
	var widths := [world_w, dots_w, _auto.width() + 8 + _repeat.width(), 16 + 2 + 16]
	var total := 0.0
	for w in widths:
		total += w
	total += GAP * (widths.size() - 1)
	var x := roundf((640.0 - total) / 2.0)
	_dividers.clear()
	_world_x = x
	x += world_w + GAP
	_dividers.append(x - GAP / 2.0)
	_dots_x = x
	x += dots_w + GAP
	_dividers.append(x - GAP / 2.0)
	_auto.position = Vector2(x, 0)
	x += _auto.width() + 8
	_repeat.position = Vector2(x, 0)
	x += _repeat.width() + GAP
	_dividers.append(x - GAP / 2.0)
	_map.position = Vector2(x, 2)
	_raids.position = Vector2(x + 18, 2)
	queue_redraw()


func _notification(what: int) -> void:
	if what == NOTIFICATION_TRANSLATION_CHANGED and _world_text != "":
		setup(world_n, wave_count, hardcore, _auto.on, _repeat.on, int(_hc_slider.value))
	elif what == NOTIFICATION_MOUSE_EXIT and _hover_dot != -1:
		_hover_dot = -1
		queue_redraw()


func set_progress(cur: int, unl: int, done: int) -> void:
	current = cur
	unlocked = unl
	done_up_to = done
	queue_redraw()


func _dot_rect(i: int) -> Rect2:
	return Rect2(_dots_x + (i - 1) * DOT_STEP, floorf((H - DOT) / 2.0), DOT, DOT)


func _dot_at(pos: Vector2) -> int:
	for i in range(1, wave_count + 1):
		if _dot_rect(i).grow(1).has_point(pos):
			return i
	return -1


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion:
		var d := _dot_at(event.position)
		if d != _hover_dot:
			_hover_dot = d
			tooltip_text = _wave_tooltip(d)
			mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND if d != -1 and d <= unlocked else Control.CURSOR_ARROW
			queue_redraw()
	elif event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var d := _dot_at(event.position)
		if d != -1:
			accept_event()
			wave_clicked.emit(d)


func _make_custom_tooltip(for_text: String) -> Object:
	if for_text == "" or not for_text.begins_with("[wave]"):
		return null
	var l := RichTextLabel.new()
	l.bbcode_enabled = true
	l.fit_content = true
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size = Vector2(220, 0)
	l.text = for_text.substr(6)
	return l


func _wave_tooltip(i: int) -> String:
	if i < 1:
		return ""
	var key := "QUEST_%d_%d" % [world_n, i]
	var status := "TOP_WAVE_LOCKED"
	if i <= done_up_to:
		status = "TOP_WAVE_DONE"
	elif i <= unlocked:
		status = "TOP_WAVE_OPEN"
	var lines := [
		"[color=#ffd46b]%s[/color]" % Loc.t("TOP_WAVE_TITLE", {"n": i, "name": tr(key + "_NAME")}),
		"[color=#9a90a8]%s[/color]" % Loc.t("TOP_WAVE_LEVEL", {"level": int(CombatData.wave(world_n, i).get("level", 1))}),
		tr(key + "_TEXT"),
		"[color=%s]%s[/color]" % ["#8ff08a" if i <= done_up_to else "#c8bfd6", tr(status)],
	]
	return "[wave]" + "\n".join(lines)


func _process(delta: float) -> void:
	_t += delta
	queue_redraw()


func _draw() -> void:
	draw_wood(self, Rect2(0, 0, 640, H))
	# Goldkante mit Schatten nach unten: trennt die Leiste klar vom Schlachtfeld
	draw_rect(Rect2(0, H - 2, 640, 1), UiTheme.GOLD_DIM)
	draw_rect(Rect2(0, H - 1, 640, 1), Color("120e18"))
	for dx in _dividers:
		draw_rect(Rect2(roundf(dx), 4, 1, H - 9), Color(0.0, 0.0, 0.0, 0.35))
		draw_rect(Rect2(roundf(dx) + 1, 4, 1, H - 9), Color(1.0, 0.85, 0.55, 0.12))
	Hud.text(self, Vector2(_world_x, BASELINE), _world_text, UiTheme.GOLD)
	for i in range(1, wave_count + 1):
		var boss := i in boss_waves
		var state := "locked"
		if i <= done_up_to:
			state = "done"
		elif i <= unlocked:
			state = "open"
		var tex: Texture2D = _tex.get("wave_%s%s" % ["boss_" if boss else "", state])
		var r := _dot_rect(i)
		if tex:
			draw_texture(tex, r.position)
		else:
			draw_rect(r, Color("ffd46b") if state == "done" else Color("3a3040"))
		if i == current:
			var ring: Texture2D = _tex.get("wave_current")
			var a := 0.75 + 0.25 * sin(_t * 4.0)
			if ring:
				draw_texture(ring, r.position - Vector2(2, 2), Color(1, 1, 1, a))
		if i == _hover_dot and i <= unlocked:
			draw_rect(r.grow(1), Color(1, 1, 1, 0.12))


## Holzflaeche mit Lichtkante oben (obere Leiste und Hardcore-Schild).
static func draw_wood(ci: CanvasItem, r: Rect2) -> void:
	var half := floorf(r.size.y / 2.0)
	ci.draw_rect(Rect2(r.position, Vector2(r.size.x, half)), WOOD_TOP)
	ci.draw_rect(Rect2(r.position + Vector2(0, half), Vector2(r.size.x, r.size.y - half)), WOOD_BOTTOM)
	ci.draw_rect(Rect2(r.position, Vector2(r.size.x, 1)), Color("6a4c34"))


## Schalter der oberen Leiste: Kaestchen und Text exakt auf der Mittellinie der Leiste.
class TopToggle extends Control:
	signal toggled(on: bool)

	var on := false
	var _text_key := ""
	var _hover := false

	func _init(text_key: String, tip_key: String) -> void:
		_text_key = text_key
		tooltip_text = tip_key
		mouse_filter = Control.MOUSE_FILTER_STOP
		mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
		size = Vector2(width(), H)
		mouse_entered.connect(func():
			_hover = true
			Sfx.play("ui_hover")
			queue_redraw())
		mouse_exited.connect(func():
			_hover = false
			queue_redraw())

	func width() -> float:
		return 11 + 4 + UiTheme.font_body.get_string_size(tr(_text_key), HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.BODY_SIZE).x

	func set_on(v: bool) -> void:
		on = v
		queue_redraw()

	func _notification(what: int) -> void:
		if what == NOTIFICATION_TRANSLATION_CHANGED:
			size = Vector2(width(), H)

	func _gui_input(event: InputEvent) -> void:
		if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
			accept_event()
			on = not on
			Sfx.play("ui_toggle")
			queue_redraw()
			toggled.emit(on)

	func _draw() -> void:
		var name := "check_%s%s" % ["on" if on else "off", "_hover" if _hover else ""]
		draw_texture(UiTheme.tex("ui/%s" % name), Vector2(0, floorf((H - 11) / 2.0)))
		Hud.text(self, Vector2(15, BASELINE), tr(_text_key), UiTheme.WHITE if (_hover or on) else UiTheme.CREAM)


## Kleines Holzschild unter der Leiste (Hardcore-Mana-Schwelle).
class HcPlate extends Control:
	func _draw() -> void:
		TopBar.draw_wood(self, Rect2(Vector2.ZERO, size))
		draw_rect(Rect2(0, size.y - 1, size.x, 1), UiTheme.GOLD_DIM)
		draw_rect(Rect2(0, 0, 1, size.y), UiTheme.GOLD_DIM)
		draw_rect(Rect2(size.x - 1, 0, 1, size.y), UiTheme.GOLD_DIM)
