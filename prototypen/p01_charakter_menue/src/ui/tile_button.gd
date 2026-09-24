class_name TileButton
extends PanelContainer
## Auswahl-Kachel mit Icon und optionalem Text (Rasse, Geschlecht, Spielmodus, Sprache ...).
## Zustaende: normal / hover / selected (per Theme-Variante TileNormal/TileHover/TileSelected).

signal pressed

var selected := false:
	set(v):
		selected = v
		_refresh()
var disabled := false:
	set(v):
		disabled = v
		modulate = Color(1, 1, 1, 0.45) if v else Color.WHITE
		mouse_default_cursor_shape = Control.CURSOR_ARROW if v else Control.CURSOR_POINTING_HAND

var _hover := false
var _box: BoxContainer
var _label: Label


func _init(icon_path := "", text_key := "", vertical := true, min_size := Vector2(24, 24)) -> void:
	custom_minimum_size = min_size
	mouse_filter = Control.MOUSE_FILTER_STOP
	mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	_box = VBoxContainer.new() if vertical else HBoxContainer.new()
	_box.alignment = BoxContainer.ALIGNMENT_CENTER
	_box.add_theme_constant_override("separation", 2)
	_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_box)
	if icon_path != "":
		var icon := UI.texture(icon_path)
		_box.add_child(icon)
	if text_key != "":
		_label = UI.label(text_key, "", HORIZONTAL_ALIGNMENT_CENTER)
		_box.add_child(_label)
	mouse_entered.connect(func():
		_hover = true
		if not disabled and not selected:
			Sfx.play("ui_hover")
		_refresh())
	mouse_exited.connect(func():
		_hover = false
		_refresh())
	_refresh()


func _gui_input(event: InputEvent) -> void:
	if disabled:
		return
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		accept_event()
		pressed.emit()


func set_text(text_key: String) -> void:
	if _label:
		_label.text = text_key


func _refresh() -> void:
	if selected:
		theme_type_variation = "TileSelected"
	elif _hover and not disabled:
		theme_type_variation = "TileHover"
	else:
		theme_type_variation = "TileNormal"
	if _label:
		_label.theme_type_variation = "GoldLabel" if selected else ""
