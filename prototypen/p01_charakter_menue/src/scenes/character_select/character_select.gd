extends Control
## Charakterauswahl im Stil von WoW: Liste rechts, Charakter mit Gruppe in der Mitte,
## "Welt betreten" unten, Loeschen unten rechts, Menue unten links, Charakter-Info oben links.

const STAND := Vector2(226, 294)
const PLAYER_SCALE := 3
const MEMBER_SCALE := 2
## Positionen der Gruppenmitglieder hinter dem Charakter (relativ zum Standpunkt)
const MEMBER_OFFSETS := [Vector2(-44, -9), Vector2(44, -9), Vector2(-76, -16), Vector2(76, -16)]

var _backdrop: SceneBackdrop
var _stage: Node2D
var _player_view: CharacterView
var _member_views: Array[CharacterView] = []
var _spot: Sprite2D
var _list_box: VBoxContainer
var _entries := {}
var _selected_id := ""
var _count_label: Label
var _name_label: Label
var _sub_label: Label
var _enter_btn: Button
var _create_btn: Button
var _delete_btn: Button
var _menu_btn: Button
var _menu_popup: PanelContainer
var _info_panel: PanelContainer
var _info_rows := {}
var _empty_label: Label
var _drop_line: ColorRect
var _t := 0.0


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_backdrop = SceneBackdrop.new()
	add_child(_backdrop)
	_backdrop.setup("charselect")
	_build_stage()
	_build_list()
	_build_bottom()
	_build_info()
	_build_menu()
	SaveGame.roster_changed.connect(_rebuild_list)
	_rebuild_list()
	var wanted: String = Router.take_param("select", "")
	if wanted != "" and not SaveGame.get_character(wanted).is_empty():
		_select(wanted, false)
	elif SaveGame.last_selected != "":
		_select(SaveGame.last_selected, false)
	match str(Router.take_param("dialog", "")):
		"options":
			_open_options()
		"delete":
			_on_delete()
		"menu":
			_toggle_menu()


# ---------------------------------------------------------------- Aufbau
func _build_stage() -> void:
	_spot = Sprite2D.new()
	_spot.texture = load("res://assets/gfx/fx/glow_big.png")
	_spot.material = preload("res://src/render/additive.tres")
	_spot.position = STAND + Vector2(0, -40)
	_spot.scale = Vector2(2, 2)
	_spot.modulate = Color(1, 0.85, 0.6, 0.16)
	add_child(_spot)
	_stage = Node2D.new()
	add_child(_stage)
	for i in MEMBER_OFFSETS.size():
		var mv := CharacterView.new()
		mv.scale = Vector2(MEMBER_SCALE, MEMBER_SCALE)
		mv.position = STAND + MEMBER_OFFSETS[i]
		mv.visible = false
		_member_views.append(mv)
	# weiter hinten stehende zuerst hinzufuegen (Zeichenreihenfolge)
	for i in [3, 2, 1, 0]:
		_stage.add_child(_member_views[i])
	_player_view = CharacterView.new()
	_player_view.scale = Vector2(PLAYER_SCALE, PLAYER_SCALE)
	_player_view.position = STAND
	_stage.add_child(_player_view)

	_name_label = UI.label("", "NameLabel", HORIZONTAL_ALIGNMENT_CENTER)
	UI.place(_name_label, Vector2(STAND.x - 110, 297), Vector2(220, 16))
	add_child(_name_label)
	_sub_label = UI.label("", "", HORIZONTAL_ALIGNMENT_CENTER)
	UI.place(_sub_label, Vector2(STAND.x - 110, 313), Vector2(220, 10))
	add_child(_sub_label)
	_empty_label = UI.wrap_label("SELECT_EMPTY", 220, "HintLabel")
	_empty_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	UI.place(_empty_label, Vector2(STAND.x - 110, 230))
	add_child(_empty_label)


func _build_list() -> void:
	var panel := UI.panel()
	UI.place(panel, Vector2(452, 6), Vector2(182, 280))
	add_child(panel)
	var v := UI.vbox(3)
	panel.add_child(v)
	var head := UI.hbox(4)
	head.alignment = BoxContainer.ALIGNMENT_CENTER
	head.add_child(UI.label("SELECT_CHARACTERS", "GoldLabel"))
	_count_label = UI.label("", "DimLabel")
	head.add_child(_count_label)
	v.add_child(head)
	v.add_child(UI.separator())
	var list_holder := Control.new()
	list_holder.size_flags_vertical = Control.SIZE_EXPAND_FILL
	list_holder.mouse_filter = Control.MOUSE_FILTER_PASS
	v.add_child(list_holder)
	_list_box = UI.vbox(2)
	_list_box.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	list_holder.add_child(_list_box)
	_drop_line = ColorRect.new()
	_drop_line.color = UiTheme.GOLD
	_drop_line.size = Vector2(160, 1)
	_drop_line.visible = false
	_drop_line.mouse_filter = Control.MOUSE_FILTER_IGNORE
	list_holder.add_child(_drop_line)

	_create_btn = UI.button("SELECT_CREATE", 182)
	UI.place(_create_btn, Vector2(452, 290), Vector2(182, 17))
	_create_btn.pressed.connect(_on_create)
	add_child(_create_btn)


func _build_bottom() -> void:
	_enter_btn = UI.button("SELECT_ENTER_WORLD", 128, true, "")
	_enter_btn.pressed.connect(_on_enter_world)
	add_child(_enter_btn)
	UI.pin_bottom(_enter_btn, STAND.x - 64, 356, 128)
	_delete_btn = UI.button("SELECT_DELETE", 100, false, "ui_click")
	_delete_btn.icon = load("res://assets/gfx/icons/trash.png")
	_delete_btn.pressed.connect(_on_delete)
	add_child(_delete_btn)
	UI.pin_bottom(_delete_btn, 534, 355, 100)
	_menu_btn = UI.button("SELECT_MENU", 70)
	_menu_btn.icon = load("res://assets/gfx/icons/gear.png")
	_menu_btn.pressed.connect(_toggle_menu)
	add_child(_menu_btn)
	UI.pin_bottom(_menu_btn, 6, 355, 70)


func _build_info() -> void:
	_info_panel = UI.panel()
	UI.place(_info_panel, Vector2(6, 6), Vector2(150, 0))
	add_child(_info_panel)
	var v := UI.vbox(3)
	_info_panel.add_child(v)
	v.add_child(UI.label("SELECT_INFO_TITLE", "GoldLabel", HORIZONTAL_ALIGNMENT_CENTER))
	v.add_child(UI.separator())
	for row in [["mode", "res://assets/gfx/icons/skull_small.png"], ["playtime", "res://assets/gfx/icons/clock.png"],
			["gold", "res://assets/gfx/icons/coin.png"], ["spec", "res://assets/gfx/icons/spec_holy.png"],
			["progress", "res://assets/gfx/icons/flag.png"]]:
		var h := UI.hbox(4)
		var icon := UI.texture(row[1])
		icon.custom_minimum_size = Vector2(9, 9)
		h.add_child(icon)
		var l := UI.label("")
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.custom_minimum_size.x = 120
		h.add_child(l)
		v.add_child(h)
		_info_rows[row[0]] = [icon, l]


func _build_menu() -> void:
	_menu_popup = UI.panel()
	UI.place(_menu_popup, Vector2(6, 282), Vector2(100, 0))
	_menu_popup.visible = false
	add_child(_menu_popup)
	var v := UI.vbox(3)
	_menu_popup.add_child(v)
	var opt := UI.button("SELECT_OPTIONS", 80)
	opt.pressed.connect(func():
		_menu_popup.visible = false
		_open_options())
	v.add_child(opt)
	var quit := UI.button("SELECT_QUIT", 80, false, "ui_back")
	quit.pressed.connect(func(): get_tree().quit())
	v.add_child(quit)


# ---------------------------------------------------------------- Liste
func _rebuild_list() -> void:
	for c in _list_box.get_children():
		c.queue_free()
	_entries.clear()
	for c in SaveGame.list():
		var e := CharacterListEntry.new(c)
		e.selected.connect(func(id): _select(id))
		e.activated.connect(func(id):
			_select(id, false)
			_on_enter_world())
		e.drop_requested.connect(_on_drop)
		e.drag_hover.connect(_on_drag_hover)
		_list_box.add_child(e)
		_entries[c["id"]] = e
	_count_label.text = "(%d/%d)" % [SaveGame.count(), GameData.MAX_CHARACTERS]
	_menu_popup.position.y = _menu_btn.position.y - _menu_popup.get_combined_minimum_size().y - 2
	_create_btn.disabled = SaveGame.is_full()
	_create_btn.tooltip_text = "SELECT_FULL" if SaveGame.is_full() else ""
	if not _entries.has(_selected_id):
		_selected_id = ""
		if SaveGame.last_selected != "":
			_select(SaveGame.last_selected, false)
		else:
			_show_character({})
	else:
		for id in _entries:
			_entries[id].is_selected = id == _selected_id


func _select(id: String, sound := true) -> void:
	if not _entries.has(id):
		return
	if sound and id != _selected_id:
		Sfx.play("ui_select")
	_selected_id = id
	SaveGame.set_last_selected(id)
	for e_id in _entries:
		_entries[e_id].is_selected = e_id == id
	_show_character(SaveGame.get_character(id))


func _show_character(c: Dictionary) -> void:
	var has := not c.is_empty()
	_player_view.visible = has
	_name_label.visible = has
	_sub_label.visible = has
	_info_panel.visible = has
	_empty_label.visible = not has
	_enter_btn.disabled = not has or bool(c.get("fallen", false))
	_delete_btn.disabled = not has
	for mv in _member_views:
		mv.visible = false
	if not has:
		return
	var fallen := bool(c.get("fallen", false))
	_player_view.set_appearance(CharacterFactory.appearance_of(c))
	_player_view.ghost = fallen
	_player_view.flash(0.5)
	var group: Array = c.get("group", [])
	for i in mini(group.size(), _member_views.size()):
		var mv := _member_views[i]
		mv.visible = true
		mv.set_appearance(CharacterFactory.appearance_of(group[i]))
		mv.ghost = fallen
		mv.modulate = Color(0.82, 0.8, 0.9)
	_name_label.text = c["name"]
	_name_label.theme_type_variation = "NameLabel"
	_name_label.modulate = Color(0.75, 0.8, 0.95, 0.8) if fallen else Color.WHITE
	var cls := Loc.class_name_for("priest", c.get("gender", "male"))
	if fallen:
		_sub_label.text = tr("SELECT_FALLEN_LONG")
		_sub_label.theme_type_variation = "HardcoreLabel"
	else:
		_sub_label.text = Loc.t("SELECT_LEVEL_LINE", {"level": int(c.get("level", 1)), "race": Loc.race_name(c["race"]), "class": cls})
		_sub_label.theme_type_variation = ""
	_update_info(c)


func _update_info(c: Dictionary) -> void:
	var hc: bool = c.get("mode", "normal") == "hardcore"
	var mode_row: Array = _info_rows["mode"]
	mode_row[0].texture = load("res://assets/gfx/icons/skull_small.png" if hc else "res://assets/gfx/icons/check.png")
	mode_row[1].text = "MODE_HARDCORE" if hc else "MODE_NORMAL"
	mode_row[1].theme_type_variation = "HardcoreLabel" if hc else ""
	var secs := int(c.get("playtime", 0.0))
	_info_rows["playtime"][1].text = Loc.t("SELECT_PLAYTIME", {"h": secs / 3600, "m": (secs / 60) % 60})
	_info_rows["gold"][1].text = Loc.t("SELECT_GOLD", {"gold": int(c.get("gold", 0))})
	var spec: String = c.get("spec", "")
	var spec_row: Array = _info_rows["spec"]
	if spec == "":
		spec_row[0].modulate = Color(1, 1, 1, 0.3)
		spec_row[0].texture = load("res://assets/gfx/icons/spec_holy.png")
		spec_row[1].text = "SPEC_NONE"
		spec_row[1].theme_type_variation = "DimLabel"
	else:
		spec_row[0].modulate = Color.WHITE
		spec_row[0].texture = load("res://assets/gfx/icons/spec_%s.png" % spec)
		spec_row[1].text = "SPEC_%s" % spec.to_upper()
		spec_row[1].theme_type_variation = ""
	var hw := int(c.get("highest_world", 1))
	var hwave := int(c.get("highest_wave", 0))
	_info_rows["progress"][1].text = Loc.t("SELECT_PROGRESS", {"world": Loc.world_name(hw), "wave": hwave})


# ---------------------------------------------------------------- Drag & Drop
func _on_drag_hover(target: CharacterListEntry, after: bool) -> void:
	_drop_line.visible = true
	_drop_line.size.x = target.size.x
	_drop_line.position = Vector2(target.position.x, target.position.y + (target.size.y + 1 if after else -2))


func _on_drop(id: String, target_id: String, after: bool) -> void:
	_drop_line.visible = false
	if id == target_id:
		return
	var order: Array = []
	for c in SaveGame.list():
		order.append(c["id"])
	order.erase(id)
	var idx := order.find(target_id)
	if after:
		idx += 1
	SaveGame.move_character(id, idx)
	Sfx.play("ui_select")
	_select(id, false)


func _notification(what: int) -> void:
	if what == NOTIFICATION_DRAG_END:
		_drop_line.visible = false


# ---------------------------------------------------------------- Aktionen
func _on_enter_world() -> void:
	if _selected_id == "" or Router.busy:
		return
	var c := SaveGame.get_character(_selected_id)
	if c.is_empty() or bool(c.get("fallen", false)):
		Sfx.play("ui_error")
		return
	Sfx.play("enter_world")
	Router.go("loading", {"id": _selected_id}, 0.6)


func _on_create() -> void:
	if SaveGame.is_full():
		Sfx.play("ui_error")
		return
	Router.go("character_create")


func _on_delete() -> void:
	if _selected_id == "":
		return
	var dlg := DeleteDialog.new(SaveGame.get_character(_selected_id))
	dlg.confirmed.connect(func():
		SaveGame.delete_character(_selected_id)
		Sfx.play("char_deleted"))
	add_child(dlg)


func _toggle_menu() -> void:
	_menu_popup.visible = not _menu_popup.visible
	if _menu_popup.visible:
		Sfx.play("ui_open")


func _open_options() -> void:
	add_child(OptionsDialog.new())


func _has_dialog() -> bool:
	for c in get_children():
		if c is ModalDialog:
			return true
	return false


func _unhandled_input(event: InputEvent) -> void:
	if _has_dialog() or Router.busy:
		return
	if event is InputEventMouseButton and event.pressed and _menu_popup.visible:
		if not _menu_popup.get_global_rect().has_point(event.position) and not _menu_btn.get_global_rect().has_point(event.position):
			_menu_popup.visible = false
	if event.is_action_pressed("ui_cancel"):
		_toggle_menu()
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("ui_accept"):
		_on_enter_world()
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("ui_up") or event.is_action_pressed("ui_down"):
		var ids: Array = []
		for c in SaveGame.list():
			ids.append(c["id"])
		if ids.is_empty():
			return
		var idx := ids.find(_selected_id)
		idx = clampi(idx + (-1 if event.is_action_pressed("ui_up") else 1), 0, ids.size() - 1)
		_select(ids[idx])
		get_viewport().set_input_as_handled()
	elif event is InputEventKey and event.pressed and event.keycode == KEY_DELETE:
		_on_delete()


func _process(delta: float) -> void:
	_t += delta
	_spot.modulate.a = 0.13 + 0.04 * sin(_t * 1.6)
