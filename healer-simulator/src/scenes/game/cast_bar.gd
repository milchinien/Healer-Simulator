class_name CastBar
extends Control
## Castbalken: eigener Zauber (ueber dem Gruppenfenster) bzw. Boss-Faehigkeit (am Boss-Balken).
## Zeigt Name und Restzeit; bei Abbruch kurz "Unterbrochen".

var unit: CombatUnit
var _label: Label
var _time: Label
var _fade := 0.0
var _fade_text := ""
var _fade_color := Color.WHITE


func _init(width := 180, height := 11) -> void:
	custom_minimum_size = Vector2(width, height)
	size = custom_minimum_size
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_label = UI.label("", "", HORIZONTAL_ALIGNMENT_CENTER)
	_label.size = Vector2(width, 10)
	_label.position = Vector2(0, height / 2.0 - 5)
	add_child(_label)
	_time = UI.label("", "DimLabel", HORIZONTAL_ALIGNMENT_RIGHT)
	_time.size = Vector2(44, 10)
	_time.position = Vector2(width - 46, height / 2.0 - 5)
	add_child(_time)


func show_stop(text_key: String, col := Color("ff6a50")) -> void:
	_fade = 0.7
	_fade_text = text_key
	_fade_color = col


func show_done() -> void:
	_fade = 0.35
	_fade_text = ""
	_fade_color = Color("fff0b0")


func _process(delta: float) -> void:
	_fade = maxf(0.0, _fade - delta)
	var casting := unit != null and unit.is_casting()
	visible = casting or _fade > 0.0
	if casting:
		_label.text = unit.cast.get("name", "")
		_label.add_theme_color_override("font_color", Color("fbf7ee"))
		_time.text = Hud.format_time(float(unit.cast["left"]))
		modulate.a = 1.0
	elif _fade > 0.0:
		if _fade_text != "":
			_label.text = _fade_text
		_label.add_theme_color_override("font_color", _fade_color)
		_time.text = ""
		modulate.a = minf(1.0, _fade * 3.0)
	queue_redraw()


func _draw() -> void:
	var r := Rect2(Vector2.ZERO, size)
	if unit != null and unit.is_casting():
		var frac := 1.0 - float(unit.cast["left"]) / maxf(0.01, float(unit.cast["total"]))
		var col := Hud.CAST
		if unit.side == "enemy":
			col = UnitFigure.CAST_COLORS.get(str(unit.cast["ability"].get("mechanic", "")), Hud.CAST)
		Hud.bar(self, r, frac, col)
	else:
		Hud.bar(self, r, 1.0, _fade_color.darkened(0.2) if _fade_text == "" else Color("8a2a24"))
