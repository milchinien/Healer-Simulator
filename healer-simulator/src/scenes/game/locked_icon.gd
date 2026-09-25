class_name LockedIcon
extends Control
## Sichtbares, aber gesperrtes Element (noch nicht gebaut): gedimmtes Symbol mit Schloss und Tooltip.

var _icon: Texture2D
var _lock: Texture2D
var _hover := false


func _init(icon: String, tip_key: String, box := Vector2(16, 16)) -> void:
	_icon = Hud.combat_tex(icon)
	_lock = Hud.combat_tex("lock")
	tooltip_text = tip_key
	size = box
	custom_minimum_size = box
	mouse_filter = Control.MOUSE_FILTER_STOP
	mouse_entered.connect(func():
		_hover = true
		queue_redraw())
	mouse_exited.connect(func():
		_hover = false
		queue_redraw())


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		accept_event()
		Sfx.play("ui_error")


func _draw() -> void:
	if _hover:
		draw_rect(Rect2(Vector2.ZERO, size), Color(1, 1, 1, 0.08))
	if _icon:
		var p := ((size - _icon.get_size()) / 2.0).floor()
		draw_texture(_icon, p, Color(0.62, 0.58, 0.68, 0.8))
	if _lock:
		draw_texture(_lock, Vector2(size.x - _lock.get_width(), size.y - _lock.get_height()))
