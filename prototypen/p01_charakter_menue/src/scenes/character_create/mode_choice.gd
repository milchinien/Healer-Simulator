class_name ModeChoice
extends Control
## Grosse Wahl in der Mitte: Normal oder Hardcore (GDD Kapitel 6).
## Hardcore zeigt alle Regeln auf der Karte und verlangt eine Bestaetigung per Haken.

signal chosen(mode: String)

const CARD_W := 232

var mode := "normal"
var _cards := {}
var _confirm: CheckBox
var _create_btn: Button


func _init(preselect_hardcore := false) -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	var dim := ColorRect.new()
	dim.color = Color(0.02, 0.01, 0.04, 0.78)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(center)
	var v := UI.vbox(6)
	center.add_child(v)
	var title := UI.label("MODE_CHOOSE", "TitleLabel", HORIZONTAL_ALIGNMENT_CENTER)
	v.add_child(title)
	var cards := UI.hbox(12)
	cards.alignment = BoxContainer.ALIGNMENT_CENTER
	v.add_child(cards)
	cards.add_child(_card("normal", "res://assets/gfx/icons/mode_normal.png", ["MODE_NORMAL_DESC"]))
	cards.add_child(_card("hardcore", "res://assets/gfx/icons/skull.png",
		["HC_RULE_1", "HC_RULE_2", "HC_RULE_3", "HC_RULE_4", "HC_RULE_5"]))
	_confirm = CheckBox.new()
	_confirm.text = "HC_CONFIRM"
	_confirm.focus_mode = Control.FOCUS_NONE
	_confirm.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	_confirm.toggled.connect(func(_on):
		Sfx.play("ui_toggle")
		_refresh())
	v.add_child(_confirm)
	var buttons := UI.hbox(8)
	buttons.alignment = BoxContainer.ALIGNMENT_CENTER
	v.add_child(buttons)
	var back := UI.button("MODE_BACK", 100, false, "ui_back")
	back.pressed.connect(_close)
	buttons.add_child(back)
	_create_btn = UI.button("CREATE_CREATE", 140, true, "")
	_create_btn.pressed.connect(_on_create)
	buttons.add_child(_create_btn)
	_select("hardcore" if preselect_hardcore else "normal", false)


func _ready() -> void:
	modulate.a = 0.0
	var tw := create_tween()
	tw.tween_property(self, "modulate:a", 1.0, 0.18)
	Sfx.play("ui_open")


func _card(m: String, icon: String, lines: Array) -> TileButton:
	var card := TileButton.new("", "", true, Vector2(CARD_W, 214))
	var v := UI.vbox(3)
	v.mouse_filter = Control.MOUSE_FILTER_IGNORE
	card.add_child(UI.margin(v, 6, 4, 6, 4))
	var ic := UI.texture(icon)
	v.add_child(ic)
	var t := UI.label("MODE_%s" % m.to_upper(), "TitleLabel", HORIZONTAL_ALIGNMENT_CENTER)
	if m == "hardcore":
		t.add_theme_color_override("font_color", UiTheme.HARDCORE)
	v.add_child(t)
	v.add_child(UI.separator())
	for key in lines:
		var h := UI.hbox(3)
		h.mouse_filter = Control.MOUSE_FILTER_IGNORE
		if lines.size() > 1:
			var dot := UI.label("*", "GoldLabel")
			dot.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
			h.add_child(dot)
		var l := UI.wrap_label(key, CARD_W - (34 if lines.size() > 1 else 22), "HintLabel")
		h.add_child(l)
		v.add_child(h)
	card.pressed.connect(func(): _select(m))
	_cards[m] = card
	return card


func _select(m: String, sound := true) -> void:
	mode = m
	if sound:
		Sfx.play("hardcore" if m == "hardcore" else "ui_select")
	for key in _cards:
		_cards[key].selected = key == m
	if m != "hardcore":
		_confirm.button_pressed = false
	_refresh()


func _refresh() -> void:
	_confirm.visible = mode == "hardcore"
	_create_btn.disabled = mode == "hardcore" and not _confirm.button_pressed
	_create_btn.text = "CREATE_CREATE"


func _on_create() -> void:
	if _create_btn.disabled:
		Sfx.play("ui_error")
		return
	chosen.emit(mode)
	queue_free()


func _close() -> void:
	Sfx.play("ui_close")
	queue_free()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		_close()
