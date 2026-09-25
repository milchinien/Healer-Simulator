class_name GameWindow
extends Control
## Fenster ueber dem Hauptbildschirm (GDD 7: Menues als Fenster darueber, der Kampf laeuft weiter).
## Nicht modal: Schlachtfeld und Aktionsleiste bleiben bedienbar. Goldrahmen, Titelplakette, Schliessen-Knopf.
## ESC schliesst das oberste Fenster (Hauptbildschirm).

signal closed

var body: VBoxContainer
var window_id := ""
var _panel: PanelContainer


func _init(id: String, title_key: String, rect: Rect2) -> void:
	window_id = id
	position = rect.position
	size = rect.size
	mouse_filter = Control.MOUSE_FILTER_STOP
	_panel = UI.panel()
	_panel.position = Vector2.ZERO
	_panel.size = rect.size
	_panel.custom_minimum_size = rect.size
	add_child(_panel)
	var outer := UI.vbox(3)
	_panel.add_child(UI.margin(outer, 2, 1, 2, 2))
	var head := Control.new()
	head.custom_minimum_size = Vector2(0, 18)
	outer.add_child(head)
	var title := UI.label(title_key, "TitleLabel", HORIZONTAL_ALIGNMENT_CENTER)
	title.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	head.add_child(title)

	outer.add_child(UI.separator())
	body = UI.vbox(3)
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	outer.add_child(body)
	# Schliessen-Knopf oben rechts im Rahmen
	var x := UI.button("X", 0)
	x.custom_minimum_size = Vector2(15, 15)
	x.size = Vector2(15, 15)
	x.tooltip_text = "WINDOW_CLOSE"
	x.position = Vector2(rect.size.x - 24, 9)
	x.pressed.connect(close)
	add_child(x)


func _ready() -> void:
	modulate.a = 0.0
	var tw := create_tween()
	tw.tween_property(self, "modulate:a", 1.0, 0.12)
	Sfx.play("ui_open")


func close() -> void:
	if is_queued_for_deletion():
		return
	Sfx.play("ui_close")
	closed.emit()
	queue_free()
