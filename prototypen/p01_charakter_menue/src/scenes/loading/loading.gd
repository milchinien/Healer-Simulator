extends Control
## Ladebildschirm von Welt 1 (Gruenhain). Die Spielwelt selbst folgt im naechsten Prototyp;
## nach dem Laden fuehrt ESC zurueck zur Charakterauswahl.

const TIPS := 8

var _bar: ProgressBar
var _hint: Label
var _progress := 0.0
var _done := false
var _character_id := ""
var _start_ms := 0


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_character_id = str(Router.take_param("id", ""))
	_start_ms = Time.get_ticks_msec()
	var bd := SceneBackdrop.new()
	add_child(bd)
	bd.setup("loading_gruenhain")

	# Unterer Balken mit Weltname, Tipp und Fortschritt
	var shade := ColorRect.new()
	shade.color = Color(0.03, 0.02, 0.05, 0.72)
	UI.place(shade, Vector2(0, 276), Vector2(640, 84))
	shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(shade)
	var line := ColorRect.new()
	line.color = UiTheme.GOLD_DIM
	UI.place(line, Vector2(0, 276), Vector2(640, 1))
	add_child(line)

	var world := UI.label(Loc.world_name(1), "TitleLabel", HORIZONTAL_ALIGNMENT_CENTER)
	UI.place(world, Vector2(0, 280), Vector2(640, 18))
	add_child(world)
	var lv: Array = GameData.WORLD_LEVELS[1]
	var sub := UI.label(Loc.t("LOADING_LEVELS", {"a": lv[0], "b": lv[1]}), "DimLabel", HORIZONTAL_ALIGNMENT_CENTER)
	UI.place(sub, Vector2(0, 299), Vector2(640, 10))
	add_child(sub)

	_bar = ProgressBar.new()
	_bar.show_percentage = false
	_bar.min_value = 0
	_bar.max_value = 100
	UI.place(_bar, Vector2(120, 312), Vector2(400, 10))
	add_child(_bar)

	var rng := RandomNumberGenerator.new()
	rng.randomize()
	var tip := UI.label(Loc.t("LOADING_TIP", {"tip": tr("TIP_%d" % rng.randi_range(1, TIPS))}), "HintLabel", HORIZONTAL_ALIGNMENT_CENTER)
	tip.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	UI.place(tip, Vector2(40, 326), Vector2(560, 20))
	add_child(tip)

	_hint = UI.label("LOADING_NEXT_PROTOTYPE", "GoldLabel", HORIZONTAL_ALIGNMENT_CENTER)
	UI.place(_hint, Vector2(0, 348), Vector2(640, 10))
	_hint.visible = false
	add_child(_hint)


func _process(delta: float) -> void:
	if _done:
		_hint.modulate.a = 0.45 + 0.55 * (0.5 + 0.5 * sin(Time.get_ticks_msec() / 300.0))
		return
	# Gleichmaessiges Fuellen mit kleinen Pausen (wirkt wie echtes Laden)
	var speed := 38.0 if fmod(_progress, 25.0) > 3.0 else 12.0
	_progress = minf(100.0, _progress + speed * delta)
	_bar.value = _progress
	if _progress >= 100.0:
		_done = true
		_hint.visible = true
		Sfx.play("ui_select")


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel") and not Router.busy:
		get_viewport().set_input_as_handled()
		_add_playtime()
		Sfx.play("ui_back")
		Router.go("character_select", {"select": _character_id})


func _add_playtime() -> void:
	var c := SaveGame.get_character(_character_id)
	if c.is_empty():
		return
	c["playtime"] = float(c.get("playtime", 0.0)) + (Time.get_ticks_msec() - _start_ms) / 1000.0
	SaveGame.save_character(c)
