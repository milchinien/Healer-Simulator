extends Control
## Charaktererstellung in zwei Schritten (wie im neueren WoW):
##   Schritt 1: Rasse (Liste untereinander) + Geschlecht, rechts die Rassen-Beschreibung
##   Schritt 2: Aussehen (Hautfarbe, Frisur, Haarfarbe)
## Der Name steht in beiden Schritten unten. "Erstellen" oeffnet die grosse Modus-Wahl
## (Normal / Hardcore) in der Mitte.

const STAND := Vector2(320, 286)
const VIEW_SCALE := 4
const BACKDROPS := {
	"human": "human_city", "dwarf": "dwarf_hall", "orc": "orc_steppe", "gnome": "gnome_workshop",
}
const PANEL_W := 196

var race := "human"
var gender := "male"
var skin := 0
var hair_style := 0
var hair_color := 0
var step := 1

var _backdrop_host: Control
var _backdrop: SceneBackdrop
var _view: CharacterView
var _step_label: Label
var _class_label: Label
# Schritt 1
var _step1: Array[Control] = []
var _race_rows := {}
var _gender_tiles := {}
var _race_title: Label
var _race_lore: Label
# Schritt 2
var _step2: Array[Control] = []
var _skin_sel: ArrowSelector
var _style_sel: ArrowSelector
var _hair_sel: ArrowSelector
var _summary_icon: TextureRect
var _summary_text: Label
# unten
var _name_edit: LineEdit
var _error: Label
var _back_btn: Button
var _next_btn: Button
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
	_build_step1()
	_build_step2()
	_build_bottom()
	# Test-Vorgaben
	race = str(Router.take_param("race", race))
	gender = str(Router.take_param("gender", gender))
	_set_race(race, false)
	_set_gender(gender, false)
	_show_step(int(Router.take_param("step", 1)), false)
	match str(Router.take_param("dialog", "")):
		"mode", "hardcore":
			_name_edit.text = "Testheld"
			_open_mode_choice(str(Router.take_param("mode", "")) == "hardcore")
	_name_edit.grab_focus.call_deferred()


# ---------------------------------------------------------------- Aufbau
func _build_header() -> void:
	var head := UI.panel("HeaderPanel")
	head.add_child(UI.margin(UI.label("CREATE_TITLE", "GoldLabel"), 10, 1, 10, 1))
	add_child(head)
	head.reset_size()
	head.position = Vector2(roundi((640 - head.get_combined_minimum_size().x) / 2.0), 4)
	_step_label = UI.label("", "DimLabel", HORIZONTAL_ALIGNMENT_CENTER)
	UI.place(_step_label, Vector2(204, 24), Vector2(232, 10))
	add_child(_step_label)
	var cls_box := UI.hbox(3)
	cls_box.alignment = BoxContainer.ALIGNMENT_CENTER
	cls_box.add_child(UI.texture("res://assets/gfx/icons/spec_holy.png"))
	_class_label = UI.label("", "GoldLabel", HORIZONTAL_ALIGNMENT_CENTER)
	cls_box.add_child(_class_label)
	UI.place(cls_box, Vector2(204, 36), Vector2(232, 10))
	add_child(cls_box)


func _build_step1() -> void:
	# Links: Rassenliste untereinander + Geschlecht
	var left := UI.panel()
	UI.place(left, Vector2(6, 6), Vector2(PANEL_W, 0))
	add_child(left)
	_step1.append(left)
	var v := UI.vbox(3)
	left.add_child(v)
	v.add_child(UI.section("CREATE_RACE"))
	for r in GameData.RACES:
		var row := TileButton.new("res://assets/gfx/icons/race_%s.png" % r, "RACE_%s" % r.to_upper(), false, Vector2(PANEL_W - 18, 24))
		row.set_align_left()
		row.pressed.connect(func(): _set_race(r))
		v.add_child(row)
		_race_rows[r] = row
	v.add_child(UI.spacer(0, 3))
	v.add_child(UI.section("CREATE_GENDER"))
	var gh := UI.hbox(4)
	gh.alignment = BoxContainer.ALIGNMENT_CENTER
	for g in GameData.GENDERS:
		var tile := TileButton.new("res://assets/gfx/icons/gender_%s.png" % g, "GENDER_%s" % g.to_upper(), false, Vector2(87, 20))
		tile.pressed.connect(func(): _set_gender(g))
		gh.add_child(tile)
		_gender_tiles[g] = tile
	v.add_child(gh)
	v.add_child(UI.wrap_label("CREATE_GENDER_HINT", PANEL_W - 18, "DimLabel"))

	# Rechts: Beschreibung der Rasse
	var right := UI.panel()
	UI.place(right, Vector2(640 - 6 - PANEL_W, 6), Vector2(PANEL_W, 0))
	add_child(right)
	_step1.append(right)
	var rv := UI.vbox(3)
	right.add_child(rv)
	_race_title = UI.label("", "TitleLabel", HORIZONTAL_ALIGNMENT_CENTER)
	rv.add_child(_race_title)
	rv.add_child(UI.separator())
	_race_lore = UI.wrap_label("", PANEL_W - 18, "HintLabel")
	rv.add_child(_race_lore)


func _build_step2() -> void:
	# Links: Zusammenfassung
	var left := UI.panel()
	UI.place(left, Vector2(6, 6), Vector2(PANEL_W, 0))
	add_child(left)
	_step2.append(left)
	var v := UI.vbox(4)
	left.add_child(v)
	v.add_child(UI.section("CREATE_SUMMARY"))
	var h := UI.hbox(5)
	_summary_icon = UI.texture("res://assets/gfx/icons/race_human.png")
	h.add_child(_summary_icon)
	_summary_text = UI.label("")
	_summary_text.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	h.add_child(_summary_text)
	v.add_child(h)
	v.add_child(UI.wrap_label("CREATE_SUMMARY_HINT", PANEL_W - 18, "DimLabel"))

	# Rechts: Aussehen
	var right := UI.panel()
	UI.place(right, Vector2(640 - 6 - PANEL_W, 6), Vector2(PANEL_W, 0))
	add_child(right)
	_step2.append(right)
	var rv := UI.vbox(4)
	right.add_child(rv)
	rv.add_child(UI.section("CREATE_APPEARANCE"))
	rv.add_child(UI.label("CREATE_SKIN", "", HORIZONTAL_ALIGNMENT_CENTER))
	_skin_sel = ArrowSelector.new(GameData.SKIN_COUNT, 120)
	_skin_sel.changed.connect(func(i):
		skin = i
		_refresh_view(true))
	rv.add_child(_skin_sel)
	rv.add_child(UI.label("CREATE_HAIRSTYLE", "", HORIZONTAL_ALIGNMENT_CENTER))
	_style_sel = ArrowSelector.new(GameData.HAIR_STYLE_COUNT, 120)
	_style_sel.changed.connect(func(i):
		hair_style = i
		_refresh_view(true))
	rv.add_child(_style_sel)
	rv.add_child(UI.label("CREATE_HAIRCOLOR", "", HORIZONTAL_ALIGNMENT_CENTER))
	_hair_sel = ArrowSelector.new(GameData.HAIR_COLOR_COUNT, 120)
	_hair_sel.changed.connect(func(i):
		hair_color = i
		_refresh_view(true))
	rv.add_child(_hair_sel)


func _build_bottom() -> void:
	_error = UI.label("", "ErrorLabel", HORIZONTAL_ALIGNMENT_CENTER)
	UI.place(_error, Vector2(160, 314), Vector2(320, 10))
	add_child(_error)
	var box := UI.panel("PlainPanel")
	add_child(box)
	var h := UI.hbox(4)
	h.alignment = BoxContainer.ALIGNMENT_CENTER
	box.add_child(h)
	var name_lbl := UI.label("CREATE_NAME", "GoldLabel")
	name_lbl.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	h.add_child(name_lbl)
	_name_edit = LineEdit.new()
	_name_edit.placeholder_text = "CREATE_NAME_PLACEHOLDER"
	_name_edit.max_length = GameData.NAME_MAX
	_name_edit.custom_minimum_size = Vector2(120, 16)
	_name_edit.alignment = HORIZONTAL_ALIGNMENT_CENTER
	_name_edit.text_changed.connect(_on_name_changed)
	_name_edit.text_submitted.connect(func(_t): _on_next())
	h.add_child(_name_edit)
	var dice := UI.icon_button("res://assets/gfx/icons/dice.png", "CREATE_DICE_TIP", "ui_dice")
	dice.pressed.connect(_roll_name)
	h.add_child(dice)
	box.reset_size()
	var bs := box.get_combined_minimum_size()
	box.position = Vector2(roundi((640 - bs.x) / 2.0), 356 - bs.y)

	_back_btn = UI.button("CREATE_BACK", 90, false, "ui_back")
	_back_btn.pressed.connect(_on_back)
	add_child(_back_btn)
	UI.pin_bottom(_back_btn, 6, 355, 90)
	_next_btn = UI.button("CREATE_NEXT", 120, true, "ui_click")
	_next_btn.pressed.connect(_on_next)
	add_child(_next_btn)
	UI.pin_bottom_right(_next_btn, 634, 356, 120)


# ---------------------------------------------------------------- Schritte
func _show_step(n: int, sound := true) -> void:
	step = clampi(n, 1, 2)
	for c in _step1:
		c.visible = step == 1
	for c in _step2:
		c.visible = step == 2
	_step_label.text = Loc.t("CREATE_STEP", {"n": step, "title": tr("CREATE_STEP_%d" % step)})
	_next_btn.text = "CREATE_NEXT" if step == 1 else "CREATE_CREATE"
	_back_btn.text = "CREATE_BACK" if step == 1 else "CREATE_BACK_STEP"
	UI.pin_bottom_right(_next_btn, 634, 356, 120)
	if step == 2:
		_update_summary()
	if sound:
		Sfx.play("ui_open")


func _on_next() -> void:
	if Router.busy or _has_overlay():
		return
	if step == 1:
		_show_step(2)
	else:
		if not _validate_name():
			return
		_open_mode_choice(false)


func _on_back() -> void:
	if Router.busy:
		return
	if step == 2:
		_show_step(1)
		return
	if SaveGame.count() == 0:
		Router.go("title")
	else:
		Router.go("character_select")


# ---------------------------------------------------------------- Auswahl
func _set_race(r: String, sound := true) -> void:
	var changed := r != race or _backdrop == null
	race = r
	if sound:
		Sfx.play("ui_select")
	for key in _race_rows:
		_race_rows[key].selected = key == r
	_race_title.text = "RACE_%s" % r.to_upper()
	_race_lore.text = "RACE_%s_LORE" % r.to_upper()
	if changed:
		_swap_backdrop(BACKDROPS[r])
	_update_swatches()
	_refresh_view(false)
	if sound:
		# Auswahl-Pose wie in WoW: kurzer Heilzauber mit Lichtfunken
		_view.play("cast")
		_sparkle(8, -30)


func _set_gender(g: String, sound := true) -> void:
	gender = g
	if sound:
		Sfx.play("ui_select")
	for key in _gender_tiles:
		_gender_tiles[key].selected = key == g
	_class_label.text = Loc.class_name_for("priest", g)
	_update_summary()


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


func _update_summary() -> void:
	if _summary_icon == null:
		return
	_summary_icon.texture = load("res://assets/gfx/icons/race_%s.png" % race)
	_summary_text.text = "%s\n%s" % [tr("RACE_%s" % race.to_upper()), Loc.class_name_for("priest", gender)]


func _refresh_view(flash := false) -> void:
	_view.set_appearance({"race": race, "class": "priest", "skin": skin, "hair_style": hair_style, "hair_color": hair_color})
	if flash:
		_view.flash(0.6)
		_sparkle(4, -20)


func _swap_backdrop(scene_name: String) -> void:
	var old := _backdrop
	_backdrop = SceneBackdrop.new()
	_backdrop_host.add_child(_backdrop)
	_backdrop.setup(scene_name)
	var stand: Array = _backdrop.meta.get("stand", [STAND.x, STAND.y])
	_view.position = Vector2(stand[0], stand[1])
	if old:
		_backdrop.modulate.a = 0.0
		var tw := create_tween()
		tw.tween_property(_backdrop, "modulate:a", 1.0, 0.4)
		tw.tween_callback(old.queue_free)


func _sparkle(count: int, rise: int) -> void:
	for i in count:
		var s := Sprite2D.new()
		s.texture = load("res://assets/gfx/fx/sparkle.png")
		s.material = preload("res://src/render/additive.tres")
		s.position = _view.position + Vector2(_rng.randi_range(-44, 44), _rng.randi_range(-120, -20))
		s.modulate = Color(1, 0.95, 0.7, 0.0)
		add_child(s)
		var tw := create_tween()
		tw.tween_interval(i * 0.05)
		tw.tween_property(s, "modulate:a", 0.95, 0.1)
		tw.tween_property(s, "position:y", s.position.y + rise * 0.4, 0.5)
		tw.parallel().tween_property(s, "modulate:a", 0.0, 0.5)
		tw.tween_callback(s.queue_free)


# ---------------------------------------------------------------- Name
func _on_name_changed(t: String) -> void:
	Sfx.play("ui_type")
	_error.text = ""
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


func _validate_name() -> bool:
	var n := NameGenerator.normalize(_name_edit.text)
	var err := NameGenerator.validate(n, SaveGame.names())
	if err == "" and SaveGame.is_full():
		err = "SELECT_FULL"
	if err != "":
		_error.text = err
		Sfx.play("ui_error")
		_shake(_name_edit.get_parent().get_parent())
		return false
	return true


# ---------------------------------------------------------------- Modus-Wahl + Erstellen
func _open_mode_choice(preselect_hardcore: bool) -> void:
	var mc := ModeChoice.new(preselect_hardcore)
	mc.chosen.connect(_create)
	add_child(mc)


func _create(mode: String) -> void:
	var c := CharacterFactory.create_player({
		"name": NameGenerator.normalize(_name_edit.text), "race": race, "gender": gender, "skin": skin,
		"hair_style": hair_style, "hair_color": hair_color, "mode": mode,
	})
	SaveGame.add_character(c)
	Sfx.play("char_created")
	_view.play("cast")
	_view.flash(1.0)
	_sparkle(10, -40)
	Router.go("character_select", {"select": c["id"]}, 0.8)


func _shake(c: Control) -> void:
	var x := c.position.x
	var tw := create_tween()
	for d in [3, -3, 2, -2, 0]:
		tw.tween_property(c, "position:x", x + d, 0.04)


func _has_overlay() -> bool:
	for c in get_children():
		if c is ModalDialog or c is ModeChoice:
			return true
	return false


func _unhandled_input(event: InputEvent) -> void:
	if _has_overlay() or Router.busy:
		return
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		Sfx.play("ui_back")
		_on_back()
