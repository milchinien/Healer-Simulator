class_name ModalDialog
extends Control
## Modales Fenster: dunkelt den Hintergrund ab, zeigt ein Panel mit Titel in der Mitte.
## ESC schliesst (wenn closable). Inhalt kommt in `body`, Knoepfe in `buttons`.

signal closed

var closable := true
var panel: PanelContainer
var body: VBoxContainer
var buttons: HBoxContainer
var _dim: ColorRect


func _init(title_key: String, width := 260) -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	_dim = ColorRect.new()
	_dim.color = Color(0.02, 0.01, 0.04, 0.72)
	_dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_dim)
	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(center)
	panel = UI.panel()
	panel.custom_minimum_size.x = width
	center.add_child(panel)
	var outer := UI.vbox(5)
	panel.add_child(UI.margin(outer, 4, 3, 4, 4))
	if title_key != "":
		var title := UI.label(title_key, "TitleLabel", HORIZONTAL_ALIGNMENT_CENTER)
		outer.add_child(title)
		outer.add_child(UI.separator())
	body = UI.vbox(4)
	outer.add_child(body)
	buttons = UI.hbox(6)
	buttons.alignment = BoxContainer.ALIGNMENT_CENTER
	outer.add_child(UI.spacer(0, 2))
	outer.add_child(buttons)


func _ready() -> void:
	modulate.a = 0.0
	var tw := create_tween()
	tw.tween_property(self, "modulate:a", 1.0, 0.15)
	Sfx.play("ui_open")


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel") and closable:
		get_viewport().set_input_as_handled()
		close()


func add_button(text_key: String, red := false, width := 70, sound := "ui_click") -> Button:
	var b := UI.button(text_key, width, red, sound)
	buttons.add_child(b)
	return b


func close() -> void:
	Sfx.play("ui_close")
	var tw := create_tween()
	tw.tween_property(self, "modulate:a", 0.0, 0.12)
	await tw.finished
	closed.emit()
	queue_free()
