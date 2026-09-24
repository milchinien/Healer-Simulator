class_name OptionsDialog
extends ModalDialog
## Optionen: Anzeige, Audio, Sprache. Aenderungen wirken sofort (Vorschau);
## "Abbrechen" stellt den vorherigen Stand wieder her, "OK" speichert.

var _snapshot := {}
var _pages: Array[Control] = []
var _tabs: TabBar
var _mode_sel: ArrowSelector
var _size_sel: ArrowSelector
var _lang_tiles := {}
var _vol_labels := {}


func _init() -> void:
	super("OPT_TITLE", 340)


func _ready() -> void:
	super()
	_snapshot = Settings.snapshot()
	_tabs = TabBar.new()
	_tabs.focus_mode = Control.FOCUS_NONE
	_tabs.add_tab("OPT_TAB_DISPLAY")
	_tabs.add_tab("OPT_TAB_AUDIO")
	_tabs.add_tab("OPT_TAB_LANGUAGE")
	_tabs.tab_changed.connect(_show_page)
	body.add_child(_tabs)
	var page_host := PanelContainer.new()
	page_host.theme_type_variation = "PlainPanel"
	page_host.custom_minimum_size = Vector2(0, 100)
	body.add_child(page_host)
	var stack := Control.new()
	stack.custom_minimum_size = Vector2(0, 92)
	page_host.add_child(stack)
	for page in [_build_display(), _build_audio(), _build_language()]:
		page.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		stack.add_child(page)
		_pages.append(page)
	_show_page(0)

	var defaults := add_button("OPT_DEFAULTS", false, 90)
	defaults.pressed.connect(_on_defaults)
	var cancel := add_button("OPT_CANCEL", false, 90, "ui_back")
	cancel.pressed.connect(_on_cancel)
	var ok := add_button("OPT_OK", false, 90)
	ok.pressed.connect(_on_ok)


func _show_page(i: int) -> void:
	Sfx.play("ui_toggle")
	for p in _pages.size():
		_pages[p].visible = p == i


func _row(label_key: String, control: Control) -> HBoxContainer:
	var h := UI.hbox(4)
	var l := UI.label(label_key)
	l.custom_minimum_size.x = 118
	l.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	h.add_child(l)
	h.add_child(control)
	return h


func _build_display() -> Control:
	var v := UI.vbox(6)
	_mode_sel = ArrowSelector.new(2, 120)
	_mode_sel.value_texts = ["OPT_WINDOWED", "OPT_FULLSCREEN"]
	_mode_sel.set_index(1 if Settings.fullscreen else 0)
	_mode_sel.changed.connect(func(i):
		Settings.fullscreen = i == 1
		Settings.apply()
		_size_sel.set_enabled(not Settings.fullscreen))
	v.add_child(_row("OPT_DISPLAY_MODE", _mode_sel))
	var max_scale := Settings.max_window_scale()
	var scales := []
	var texts := []
	for s in Settings.SCALES:
		if s <= max_scale:
			scales.append(s)
			texts.append("%d x %d" % [Settings.BASE_W * s, Settings.BASE_H * s])
	_size_sel = ArrowSelector.new(scales.size(), 120)
	_size_sel.value_texts = texts
	_size_sel.wrap = false
	_size_sel.set_index(maxi(0, scales.find(Settings.window_scale)))
	_size_sel.changed.connect(func(i):
		Settings.window_scale = scales[i]
		Settings.apply())
	_size_sel.set_enabled(not Settings.fullscreen)
	v.add_child(_row("OPT_WINDOW_SIZE", _size_sel))
	v.add_child(UI.wrap_label("OPT_DISPLAY_HINT", 310, "DimLabel"))
	return UI.margin(v, 4, 4, 4, 2)


func _build_audio() -> Control:
	var v := UI.vbox(5)
	for entry in [["OPT_VOL_MASTER", "vol_master"], ["OPT_VOL_MUSIC", "vol_music"], ["OPT_VOL_SFX", "vol_sfx"]]:
		var key: String = entry[1]
		var h := UI.hbox(4)
		var slider := HSlider.new()
		slider.min_value = 0
		slider.max_value = 100
		slider.step = 5
		slider.value = float(Settings.get(key)) * 100.0
		slider.custom_minimum_size = Vector2(130, 11)
		slider.focus_mode = Control.FOCUS_NONE
		slider.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
		slider.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		var val := UI.label("%d%%" % int(slider.value), "GoldLabel")
		val.custom_minimum_size.x = 34
		_vol_labels[key] = val
		slider.value_changed.connect(func(value: float):
			Settings.set(key, value / 100.0)
			Settings.apply()
			val.text = "%d%%" % int(value)
			if key != "vol_music":
				Sfx.play("ui_toggle"))
		h.add_child(slider)
		h.add_child(val)
		v.add_child(_row(entry[0], h))
	v.add_child(UI.wrap_label("OPT_AUDIO_HINT", 310, "DimLabel"))
	return UI.margin(v, 4, 4, 4, 2)


func _build_language() -> Control:
	var v := UI.vbox(6)
	var h := UI.hbox(8)
	h.alignment = BoxContainer.ALIGNMENT_CENTER
	for lang in Loc.LANGUAGES:
		var tile := TileButton.new("", Loc.LANGUAGE_NAMES[lang], true, Vector2(90, 24))
		tile.selected = Settings.language == lang
		tile.pressed.connect(func(): _set_language(lang))
		_lang_tiles[lang] = tile
		h.add_child(tile)
	v.add_child(UI.spacer(0, 4))
	v.add_child(h)
	v.add_child(UI.wrap_label("OPT_LANGUAGE_HINT", 310, "DimLabel"))
	return UI.margin(v, 4, 4, 4, 2)


func _set_language(lang: String) -> void:
	Sfx.play("ui_select")
	Settings.language = lang
	Settings.apply()
	for l in _lang_tiles:
		_lang_tiles[l].selected = l == lang


func _on_defaults() -> void:
	Settings.reset_defaults()
	_mode_sel.set_index(0)
	_size_sel.set_index(0)
	_size_sel.set_enabled(true)
	for key in _vol_labels:
		var slider: HSlider = _vol_labels[key].get_parent().get_child(0)
		slider.set_value_no_signal(float(Settings.get(key)) * 100.0)
		_vol_labels[key].text = "%d%%" % int(slider.value)


func _on_cancel() -> void:
	Settings.restore(_snapshot)
	close()


func _on_ok() -> void:
	Settings.save_settings()
	close()


func close() -> void:
	if not is_queued_for_deletion():
		super()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		_on_cancel()
