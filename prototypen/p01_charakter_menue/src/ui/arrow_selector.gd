class_name ArrowSelector
extends HBoxContainer
## Auswahl mit Pfeilen links/rechts:  <  Anzeige  >
## Anzeige ist entweder Text (value_texts) oder Farbfelder (swatches).

signal changed(index: int)

var index := 0
var count := 1
var value_texts: Array = []          # Uebersetzungsschluessel oder fertige Texte je Index
var swatches: Array = []             # Farben je Index (optional)
var wrap := true

var _left: TextureButton
var _right: TextureButton
var _value: Label
var _swatch_box: HBoxContainer
var _swatch_rects: Array = []


func _init(p_count := 1, width := 60) -> void:
	count = p_count
	add_theme_constant_override("separation", 3)
	alignment = BoxContainer.ALIGNMENT_CENTER
	_left = _arrow("left")
	add_child(_left)
	var mid := CenterContainer.new()
	mid.custom_minimum_size = Vector2(width, 11)
	mid.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(mid)
	var stack := VBoxContainer.new()
	stack.mouse_filter = Control.MOUSE_FILTER_IGNORE
	stack.alignment = BoxContainer.ALIGNMENT_CENTER
	mid.add_child(stack)
	_value = UI.label("", "", HORIZONTAL_ALIGNMENT_CENTER)
	stack.add_child(_value)
	_swatch_box = HBoxContainer.new()
	_swatch_box.add_theme_constant_override("separation", 1)
	_swatch_box.alignment = BoxContainer.ALIGNMENT_CENTER
	_swatch_box.visible = false
	stack.add_child(_swatch_box)
	_right = _arrow("right")
	add_child(_right)
	_left.pressed.connect(func(): step(-1))
	_right.pressed.connect(func(): step(1))


func _arrow(dir: String) -> TextureButton:
	var b := TextureButton.new()
	b.texture_normal = load("res://assets/gfx/ui/arrow_%s_normal.png" % dir)
	b.texture_hover = load("res://assets/gfx/ui/arrow_%s_hover.png" % dir)
	b.texture_pressed = load("res://assets/gfx/ui/arrow_%s_pressed.png" % dir)
	b.texture_disabled = load("res://assets/gfx/ui/arrow_%s_disabled.png" % dir)
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	b.focus_mode = Control.FOCUS_NONE
	b.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	b.mouse_entered.connect(func(): Sfx.play("ui_hover"))
	return b


## Farbfelder anzeigen (anklickbar) statt Text.
func set_swatches(colors: Array) -> void:
	swatches = colors
	for c in _swatch_box.get_children():
		c.queue_free()
	_swatch_rects.clear()
	for i in colors.size():
		var frame := TextureRect.new()
		frame.texture = load("res://assets/gfx/ui/swatch_frame.png")
		frame.mouse_filter = Control.MOUSE_FILTER_STOP
		frame.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
		var fill := ColorRect.new()
		fill.color = colors[i]
		fill.position = Vector2(2, 2)
		fill.size = Vector2(5, 5)
		fill.mouse_filter = Control.MOUSE_FILTER_IGNORE
		frame.add_child(fill)
		var idx := i
		frame.gui_input.connect(func(ev: InputEvent):
			if ev is InputEventMouseButton and ev.pressed and ev.button_index == MOUSE_BUTTON_LEFT:
				set_index(idx, true))
		_swatch_box.add_child(frame)
		_swatch_rects.append(frame)
	_swatch_box.visible = colors.size() > 0
	_value.visible = colors.is_empty()
	_refresh()


func step(d: int) -> void:
	var n := index + d
	if wrap:
		n = posmod(n, count)
	else:
		n = clampi(n, 0, count - 1)
	set_index(n, true)


func set_index(i: int, emit := false) -> void:
	var old := index
	index = clampi(i, 0, count - 1)
	_refresh()
	if emit and old != index:
		Sfx.play("ui_toggle")
		changed.emit(index)


func set_enabled(on: bool) -> void:
	_left.disabled = not on
	_right.disabled = not on
	_value.modulate = Color.WHITE if on else Color(1, 1, 1, 0.45)


func _refresh() -> void:
	if value_texts.size() > index:
		_value.text = str(value_texts[index])
	else:
		_value.text = "%d / %d" % [index + 1, count]
	for i in _swatch_rects.size():
		var sel := i == index
		_swatch_rects[i].texture = load("res://assets/gfx/ui/swatch_frame_sel.png" if sel else "res://assets/gfx/ui/swatch_frame.png")
	if not wrap:
		_left.disabled = index <= 0
		_right.disabled = index >= count - 1
