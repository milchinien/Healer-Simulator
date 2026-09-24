class_name CharacterListEntry
extends PanelContainer
## Eintrag in der Charakterliste (rechts). Unterstuetzt Auswahl, Doppelklick und Drag & Drop.

signal selected(id: String)
signal activated(id: String)
signal drop_requested(id: String, target_id: String, after: bool)
signal drag_hover(target: CharacterListEntry, after: bool)

var character_id := ""
var is_selected := false:
	set(v):
		is_selected = v
		_refresh()
var _hover := false
var _name: Label
var _info: Label


func _init(c: Dictionary) -> void:
	character_id = c["id"]
	custom_minimum_size = Vector2(0, 22)
	mouse_filter = Control.MOUSE_FILTER_STOP
	mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	var fallen := bool(c.get("fallen", false))
	var h := UI.hbox(4)
	h.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(h)
	var portrait := UI.texture("res://assets/gfx/icons/race_%s.png" % c["race"])
	portrait.custom_minimum_size = Vector2(18, 18)
	if fallen:
		portrait.modulate = Color(0.55, 0.6, 0.75, 0.8)
	h.add_child(portrait)
	var lines := UI.vbox(0)
	lines.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	lines.alignment = BoxContainer.ALIGNMENT_CENTER
	h.add_child(lines)
	_name = UI.label(c["name"])
	lines.add_child(_name)
	var info_text := Loc.t("SELECT_ENTRY_INFO", {"level": int(c.get("level", 1)), "world": Loc.world_name(int(c.get("world", 1)))})
	if fallen:
		info_text = tr("SELECT_FALLEN")
	_info = UI.label(info_text, "HardcoreLabel" if fallen else "DimLabel")
	_info.clip_text = true
	_info.custom_minimum_size.x = 100
	lines.add_child(_info)
	if c.get("mode", "normal") == "hardcore":
		var skull := UI.texture("res://assets/gfx/icons/skull_small.png")
		skull.tooltip_text = "SELECT_HARDCORE_TIP"
		skull.mouse_filter = Control.MOUSE_FILTER_PASS
		skull.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		if fallen:
			skull.modulate = Color("ff6a50")
		h.add_child(skull)
	mouse_entered.connect(func():
		_hover = true
		if not is_selected:
			Sfx.play("ui_hover")
		_refresh())
	mouse_exited.connect(func():
		_hover = false
		_refresh())
	_refresh()
	_name.theme_type_variation = "DimLabel" if fallen else ""


func _refresh() -> void:
	if is_selected:
		theme_type_variation = "ListEntrySelected"
	elif _hover:
		theme_type_variation = "ListEntryHover"
	else:
		theme_type_variation = "ListEntryNormal"
	if _name and _name.theme_type_variation != "DimLabel":
		_name.theme_type_variation = "GoldLabel" if is_selected else ""


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		if event.double_click:
			activated.emit(character_id)
		else:
			selected.emit(character_id)


# ---------------------------------------------------------------- Drag & Drop
func _get_drag_data(_at_position: Vector2):
	if SaveGame.count() < 2:
		return null
	var preview := PanelContainer.new()
	preview.theme_type_variation = "ListEntrySelected"
	preview.custom_minimum_size = Vector2(size.x, 22)
	preview.modulate.a = 0.85
	var l := UI.label(_name.text, "GoldLabel")
	preview.add_child(UI.margin(l, 22, 0, 2, 0))
	var holder := Control.new()
	holder.add_child(preview)
	preview.position = Vector2(-size.x / 2, -11)
	set_drag_preview(holder)
	Sfx.play("ui_toggle")
	return {"character_id": character_id}


func _can_drop_data(at_position: Vector2, data) -> bool:
	var ok: bool = data is Dictionary and data.has("character_id")
	if ok:
		drag_hover.emit(self, at_position.y > size.y / 2)
	return ok


func _drop_data(at_position: Vector2, data) -> void:
	drop_requested.emit(data["character_id"], character_id, at_position.y > size.y / 2)
