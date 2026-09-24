extends Control
## Charaktererstellung: Rasse, Geschlecht, Hautfarbe, Frisur, Haarfarbe, Name, Spielmodus.
## Hintergrund und Beschreibung wechseln mit der Rasse. Die Figur aendert sich live.

const STAND := Vector2(320, 288)
const VIEW_SCALE := 4
const BACKDROPS := {
	"human": "human_city", "dwarf": "dwarf_hall", "orc": "orc_steppe", "gnome": "gnome_workshop",
}

var race := "human"
var gender := "male"
var skin := 0
var hair_style := 0
var hair_color := 0
var mode := "normal"

var _backdrop_host: Control
var _backdrop: SceneBackdrop
var _view: CharacterView
var _race_tiles := {}
var _gender_tiles := {}
var _mode_tiles := {}
var _race_title: Label
var _race_lore: Label
var _class_label: Label
var _skin_sel: ArrowSelector
var _style_sel: ArrowSelector
var _hair_sel: ArrowSelector
var _mode_desc: Label
var _name_edit: LineEdit
var _error: Label
var _create_btn: Button
var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_rng.randomize()
	_backdrop_host = Control.new()
	_backdrop_host.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_backdrop_host.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_backdrop_host)
	_view = CharacterView.new()
	_view.scale = Vector2(VIEW_SCALE, VIEW_SCALE)
	_view.position = STAND
	add_child(_view)
	_build_header()
	_build_left()
	_build_right()
	_build_bottom()
	# Test-Vorgaben
	race = str(Router.take_param("race", race))
	gender = str(Router.take_param("gender", gender))
	_set_race(race, false)
	_set_gender(gender, false)
	if str(Router.take_param("mode", "")) == "hardcore":
		_set_mode("hardcore", false)
	if str(Router.take_param("dialog", "")) == "hardcore":
		_ask_hardcore()
	_name_edit.grab_focus.call_deferred()


# ---------------------------------------------------------------- Aufbau
func _build_header() -> void:
	var head := UI.panel("HeaderPanel")
	var hb := UI.hbox(4)
	hb.add_child(UI.label("CREATE_TITLE", "TitleLabel"))
	head.add_child(UI.margin(hb, 6, 0, 6, 1))
	add_child(head)
	head.reset_size()
	head.position = Vector2(roundi((640 - head.get_combined_minimum_size().x) / 2.0), 4)
	var cls_box := UI.hbox(3)
	cls_box.alignment = BoxContainer.ALIGNMENT_CENTER
	cls_box.add_child(UI.texture("res://assets/gfx/icons/spec_holy.png"))
	_class_label = UI.label("", "GoldLabel", HORIZONTAL_ALIGNMENT_CENTER)
	cls_box.add_child(_class_label)
	UI.place(cls_box, Vector2(220, 36), Vector2(200, 10))
	add_child(cls_box)


func _build_left() -> void:
	var panel := UI.panel()
	UI.place(panel, Vector2(6, 6), Vector2(172, 0))
	add_child(panel)
	var v := UI.vbox(4)
	panel.add_child(v)
	v.add_child(UI.section("CREATE_RACE"))
	var grid := GridContainer.new()
	grid.columns = 4
	grid.add_theme_constant_override("h_separation", 2)
	grid.add_theme_constant_override("v_separation", 2)
	for r in GameData.RACES:
		var tile := TileButton.new("res://assets/gfx/icons/race_%s.png" % r, "RACE_%s_SHORT" % r.to_upper(), true, Vector2(37, 34))
		tile.tooltip_text = "RACE_%s" % r.to_upper()
		tile.pressed.connect(func(): _set_race(r))
		grid.add_child(tile)
		_race_tiles[r] = tile
	v.add_child(grid)
	_race_title = UI.label("", "TitleLabel", HORIZONTAL_ALIGNMENT_CENTER)
	v.add_child(_race_title)
	_race_lore = UI.wrap_label("", 152, "HintLabel")
	_race_lore.custom_minimum_size.y = 74
	v.add_child(_race_lore)
	v.add_child(UI.section("CREATE_GENDER"))
	var gh := UI.hbox(4)
	gh.alignment = BoxContainer.ALIGNMENT_CENTER
	for g in GameData.GENDERS:
		var tile := TileButton.new("res://assets/gfx/icons/gender_%s.png" % g, "GENDER_%s" % g.to_upper(), false, Vector2(74, 20))
		tile.pressed.connect(func(): _set_gender(g))
		gh.add_child(tile)
		_gender_tiles[g] = tile
	v.add_child(gh)
	v.add_child(UI.wrap_label("CREATE_GENDER_HINT", 152, "DimLabel"))


func _build_right() -> void:
	var panel := UI.panel()
	UI.place(panel, Vector2(462, 6), Vector2(172, 0))
	add_child(panel)
	var v := UI.vbox(4)
	panel.add_child(v)
	v.add_child(UI.section("CREATE_APPEARANCE"))
	v.add_child(UI.label("CREATE_SKIN", "", HORIZONTAL_ALIGNMENT_CENTER))
	_skin_sel = ArrowSelector.new(GameData.SKIN_COUNT, 110)
	_skin_sel.changed.connect(func(i):
		skin = i
		_refresh_view(true))
	v.add_child(_skin_sel)
	v.add_child(UI.label("CREATE_HAIRSTYLE", "", HORIZONTAL_ALIGNMENT_CENTER))
	_style_sel = ArrowSelector.new(GameData.HAIR_STYLE_COUNT, 110)
	_style_sel.changed.connect(func(i):
		hair_style = i
		_refresh_view(true))
	v.add_child(_style_sel)
	v.add_child(UI.label("CREATE_HAIRCOLOR", "", HORIZONTAL_ALIGNMENT_CENTER))
	_hair_sel = ArrowSelector.new(GameData.HAIR_COLOR_COUNT, 110)
	_hair_sel.changed.connect(func(i):
		hair_color = i
		_refresh_view(true))
	v.add_child(_hair_sel)
	v.add_child(UI.spacer(0, 2))
	v.add_child(UI.section("CREATE_MODE"))
	var mh := UI.hbox(4)
	mh.alignment = BoxContainer.ALIGNMENT_CENTER
	for m in GameData.MODES:
		var icon := "res://assets/gfx/icons/mode_normal.png" if m == "normal" else "res://assets/gfx/icons/skull.png"
		var tile := TileButton.new(icon, "MODE_%s" % m.to_upper(), true, Vector2(74, 36))
		tile.pressed.connect(func(): _on_mode_tile(m))
		mh.add_child(tile)
		_mode_tiles[m] = tile
	v.add_child(mh)
	_mode_desc = UI.wrap_label("", 152, "HintLabel")
	v.add_child(_mode_desc)


func _build_bottom() -> void:
	var box := UI.panel("PlainPanel")
	add_child(box)
	var v := UI.vbox(2)
	box.add_child(v)
	var h := UI.hbox(3)
	h.alignment = BoxContainer.ALIGNMENT_CENTER
	h.add_child(UI.label("CREATE_NAME", "GoldLabel"))
	_name_edit = LineEdit.new()
	_name_edit.placeholder_text = "CREATE_NAME_PLACEHOLDER"
	_name_edit.max_length = GameData.NAME_MAX
	_name_edit.custom_minimum_size = Vector2(112, 15)
	_name_edit.alignment = HORIZONTAL_ALIGNMENT_CENTER
	_name_edit.text_changed.connect(_on_name_changed)
	_name_edit.text_submitted.connect(func(_t): _on_create())
	h.add_child(_name_edit)
	var dice := UI.icon_button("res://assets/gfx/icons/dice.png", "CREATE_DICE_TIP", "ui_dice")
	dice.pressed.connect(_roll_name)
	h.add_child(dice)
	v.add_child(h)
	_error = UI.label("", "ErrorLabel", HORIZONTAL_ALIGNMENT_CENTER)
	_error.custom_minimum_size.y = 9
	v.add_child(_error)

	_create_btn = UI.button("CREATE_CREATE", 128, true, "")
	_create_btn.pressed.connect(_on_create)
	add_child(_create_btn)
	UI.pin_bottom(_create_btn, 256, 356, 128)
	UI.pin_bottom(box, 214, _create_btn.position.y - 2, 212)
	var back := UI.button("CREATE_BACK", 70, false, "ui_back")
	back.pressed.connect(_on_back)
	add_child(back)
	UI.pin_bottom(back, 6, 355, 70)


# ---------------------------------------------------------------- Auswahl
func _set_race(r: String, sound := true) -> void:
	var changed := r != race or _backdrop == null
	race = r
	if sound:
		Sfx.play("ui_select")
	for key in _race_tiles:
		_race_tiles[key].selected = key == r
	_race_title.text = "RACE_%s" % r.to_upper()
	_race_lore.text = "RACE_%s_LORE" % r.to_upper()
	if changed:
		_swap_backdrop(BACKDROPS[r])
	_update_swatches()
	_refresh_view(sound)


func _set_gender(g: String, sound := true) -> void:
	gender = g
	if sound:
		Sfx.play("ui_select")
	for key in _gender_tiles:
		_gender_tiles[key].selected = key == g
	_class_label.text = Loc.class_name_for("priest", g)
	_refresh_view(false)


func _on_mode_tile(m: String) -> void:
	if m == mode:
		return
	if m == "hardcore":
		_ask_hardcore()
	else:
		_set_mode("normal")


func _ask_hardcore() -> void:
	Sfx.play("hardcore")
	var dlg := HardcoreDialog.new()
	dlg.accepted.connect(func(): _set_mode("hardcore", false))
	add_child(dlg)


func _set_mode(m: String, sound := true) -> void:
	mode = m
	if sound:
		Sfx.play("ui_select")
	for key in _mode_tiles:
		_mode_tiles[key].selected = key == m
	_mode_desc.text = "MODE_%s_DESC" % m.to_upper()
	_mode_desc.theme_type_variation = "HardcoreLabel" if m == "hardcore" else "HintLabel"


func _update_swatches() -> void:
	var skins := []
	for i in GameData.SKIN_COUNT:
		skins.append(Color(GameData.skin_ramp(race, i)[1]))
	_skin_sel.set_swatches(skins)
	var hairs := []
	for i in GameData.HAIR_COLOR_COUNT:
		hairs.append(Color(GameData.hair_ramp(race, i)[1]))
	_hair_sel.set_swatches(hairs)
	var styles := []
	for i in GameData.HAIR_STYLE_COUNT:
		styles.append(Loc.t("CREATE_STYLE_N", {"n": i + 1}))
	_style_sel.value_texts = styles
	_skin_sel.set_index(skin)
	_style_sel.set_index(hair_style)
	_hair_sel.set_index(hair_color)
	_mode_desc.text = "MODE_%s_DESC" % mode.to_upper()
	for key in _mode_tiles:
		_mode_tiles[key].selected = key == mode


func _refresh_view(flash := false) -> void:
	_view.set_appearance({"race": race, "class": "priest", "skin": skin, "hair_style": hair_style, "hair_color": hair_color})
	if flash:
		_view.flash(0.6)
		_sparkle()


func _swap_backdrop(scene_name: String) -> void:
	var old := _backdrop
	_backdrop = SceneBackdrop.new()
	_backdrop_host.add_child(_backdrop)
	_backdrop.setup(scene_name)
	if old:
		_backdrop.modulate.a = 0.0
		var tw := create_tween()
		tw.tween_property(_backdrop, "modulate:a", 1.0, 0.35)
		tw.tween_callback(old.queue_free)


func _sparkle() -> void:
	for i in 5:
		var s := Sprite2D.new()
		s.texture = load("res://assets/gfx/fx/sparkle.png")
		s.material = preload("res://src/render/additive.tres")
		s.position = STAND + Vector2(_rng.randi_range(-40, 40), _rng.randi_range(-110, -10))
		s.modulate = Color(1, 0.95, 0.7, 0.9)
		add_child(s)
		var tw := create_tween()
		tw.tween_interval(i * 0.04)
		tw.tween_property(s, "position:y", s.position.y - 8, 0.45)
		tw.parallel().tween_property(s, "modulate:a", 0.0, 0.45)
		tw.tween_callback(s.queue_free)


# ---------------------------------------------------------------- Name
func _on_name_changed(t: String) -> void:
	Sfx.play("ui_type")
	_error.text = ""
	# Nur Buchstaben zulassen, waehrend getippt wird
	var re := RegEx.new()
	re.compile("[^A-Za-zÄÖÜäöüß]")
	var cleaned := re.sub(t, "", true)
	if cleaned != t:
		var caret := _name_edit.caret_column
		_name_edit.text = cleaned
		_name_edit.caret_column = maxi(0, caret - (t.length() - cleaned.length()))


func _roll_name() -> void:
	_name_edit.text = NameGenerator.generate(race, gender, _rng, SaveGame.names())
	_name_edit.caret_column = _name_edit.text.length()
	_error.text = ""


# ---------------------------------------------------------------- Erstellen / Zurueck
func _on_create() -> void:
	if Router.busy or _has_dialog():
		return
	var n := NameGenerator.normalize(_name_edit.text)
	var err := NameGenerator.validate(n, SaveGame.names())
	if err == "" and SaveGame.is_full():
		err = "SELECT_FULL"
	if err != "":
		_error.text = err
		Sfx.play("ui_error")
		_shake(_name_edit)
		return
	var c := CharacterFactory.create_player({
		"name": n, "race": race, "gender": gender, "skin": skin, "hair_style": hair_style,
		"hair_color": hair_color, "mode": mode,
	})
	SaveGame.add_character(c)
	Sfx.play("char_created")
	_view.flash(1.0)
	_sparkle()
	Router.go("character_select", {"select": c["id"]}, 0.5)


func _on_back() -> void:
	if Router.busy:
		return
	if SaveGame.count() == 0:
		Router.go("title")
	else:
		Router.go("character_select")


func _shake(c: Control) -> void:
	var x := c.position.x
	var tw := create_tween()
	for d in [3, -3, 2, -2, 0]:
		tw.tween_property(c, "position:x", x + d, 0.04)


func _has_dialog() -> bool:
	for c in get_children():
		if c is ModalDialog:
			return true
	return false


func _unhandled_input(event: InputEvent) -> void:
	if _has_dialog() or Router.busy:
		return
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		Sfx.play("ui_back")
		_on_back()
