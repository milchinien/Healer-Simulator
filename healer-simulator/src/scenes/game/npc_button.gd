class_name NpcButton
extends Control
## Portraet in der NPC-Leiste (klickbar). Zeigt ein goldenes Ausrufezeichen, wenn es etwas Neues gibt
## (Lehrmeister: neue lernbare Zauber).

signal pressed

var attention := false:
	set(v):
		attention = v
		queue_redraw()
var _icon: Texture2D
var _hover := false
var _t := 0.0


func _init(icon: String, tip_key: String, box := Vector2(34, 34)) -> void:
	_icon = Hud.combat_tex(icon)
	tooltip_text = tip_key
	size = box
	custom_minimum_size = box
	mouse_filter = Control.MOUSE_FILTER_STOP
	mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	mouse_entered.connect(func():
		_hover = true
		Sfx.play("ui_hover")
		queue_redraw())
	mouse_exited.connect(func():
		_hover = false
		queue_redraw())


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		accept_event()
		Sfx.play("ui_click")
		pressed.emit()


func _process(delta: float) -> void:
	if attention:
		_t += delta
		queue_redraw()


func _draw() -> void:
	if _icon:
		var p := ((size - _icon.get_size()) / 2.0).floor()
		draw_texture(_icon, p)
		if _hover:
			draw_rect(Rect2(p, _icon.get_size()), Color(1, 0.95, 0.75, 0.12))
			draw_rect(Rect2(p - Vector2(1, 1), _icon.get_size() + Vector2(2, 2)), UiTheme.GOLD, false, 1.0)
	if attention:
		# goldenes Ausrufezeichen oben rechts, leicht huepfend
		var y := -1.0 + roundf(sin(_t * 5.0) * 1.5)
		var r := Rect2(size.x - 9, y, 9, 12)
		draw_rect(r, Color("120e18"))
		draw_rect(r.grow(-1), Color("ffd46b"))
		draw_rect(Rect2(r.position.x + 1, r.position.y + 1, 7, 1), Color("fff2b0"))
		draw_rect(Rect2(r.position.x + 3, r.position.y + 2, 3, 5), Color("2a1606"))
		draw_rect(Rect2(r.position.x + 3, r.position.y + 8, 3, 2), Color("2a1606"))
