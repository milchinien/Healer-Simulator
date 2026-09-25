extends Control
## Hauptbildschirm (GDD Kapitel 7): ein Bildschirm fuer alles. Schlachtfeld mit Gruppe und Gegnern,
## obere Leiste mit Wellen, NPC-Leiste (gesperrt), Ziel- und Boss-Fenster, Gruppenfenster,
## Spieler-HP/Mana, Aktionsleiste, Mikromenue (gesperrt). Steuert den Wellenablauf mit
## Normal- und Hardcore-Regeln, EP/Gold/Level und speichert nach jeder Welle.

enum Phase { READY, FIGHT, TRAINING, RESULT }

## Positionen der unteren Leiste kommen aus data/hud_layout.json (erzeugt mit werkzeuge/pixelart/hud_art.py),
## damit alle Elemente genau in ihren gravierten Fassungen sitzen.
static var HL: Dictionary = {}
const FRAME_GAP := 4
const MICRO := [
	["micro_character", "MICRO_CHARACTER"], ["micro_spellbook", "MICRO_SPELLBOOK"], ["micro_talents", "MICRO_TALENTS"],
	["micro_bags", "MICRO_BAGS"], ["micro_group", "MICRO_GROUP"], ["micro_cards", "MICRO_CARDS"],
	["micro_map", "MICRO_MAP"], ["micro_raids", "MICRO_RAIDS"], ["micro_options", "MICRO_OPTIONS"], ["micro_meter", "MICRO_METER"],
]

var c: Dictionary = {}
var hardcore := false
var world_n := 1
var wave_n := 1
var phase := Phase.READY

var battle: Battle
var field: Battlefield
var player: CombatUnit
var friendly_target: CombatUnit
var enemy_target: CombatUnit
var hover_unit: CombatUnit

var _top: TopBar
var _frames := {}                  # CombatUnit -> UnitFrame
var _frame_box: Control
var _mana_bar: ManaBar
var _trainer_btn: NpcButton
var _windows: Array = []           # offene Fenster (Lehrmeister, Zauberbuch), oberstes zuletzt
var _xp_bar: XpBar
var _cast_bar: CastBar
var _bar: ActionBar
var _friendly_tf: TargetFrame
var _enemy_tf: TargetFrame
var _boss: BossFrame
var _gold: Label
var _center: VBoxContainer
var _quest_title: Label
var _quest_text: Label
var _start_btn: Button
var _train_btn: Button
var _status: Label
var _train_end: Button
var _error: Label
var _banner: Label
var _banner_sub: Label

var _countdown := -1.0
var _wait_mana := false
var _popups := 0
var _wave_xp := 0                  # EP des Spielers in dieser Welle (nur Anzeige)
var _xp_acc := {}                  # CombatUnit -> angesammelte Bruchteile aus Heilung/Schaden
var _pending_gold := 0
var _died := {}                    # CombatUnit -> true (in dieser Welle gestorben)
var _training_snapshot := {}
var _playtime_acc := 0.0
var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	_rng.randomize()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	_load_character()
	battle = Battle.new()
	battle.hardcore = hardcore
	battle.world_n = world_n
	add_child(battle)
	battle.event.connect(_on_event)
	battle.finished.connect(_on_finished)
	field = Battlefield.new()
	add_child(field)
	_build_hud()
	_build_party()
	_load_wave(wave_n)
	_after_wave_setup(false)
	_offer_boons()
	_apply_test_args()


## Test-/Screenshot-Argumente: char=<Name>, wave=<n>, autostart=1, training=1
func _apply_test_args() -> void:
	var args := Settings.user_args
	if args.has("wave"):
		_load_wave(int(args["wave"]))
	if args.has("autostart"):
		_start_wave.call_deferred()
	if args.get("window", "") == "trainer":
		toggle_trainer.call_deferred()
	elif args.get("window", "") == "spellbook":
		toggle_spellbook.call_deferred()
	if args.has("xp_gain"):
		# EP fuer alle nach kurzer Zeit (Screenshot des Level-Ups)
		get_tree().create_timer(float(args.get("xp_at", "1.0"))).timeout.connect(func():
			for u in battle.party:
				_give_xp(u, int(args["xp_gain"])))
	if args.has("cast"):
		# Zauber nach kurzer Zeit auf den Tank wirken (Screenshot des Castbalkens)
		get_tree().create_timer(float(args.get("cast_at", "1.0"))).timeout.connect(func():
			_set_friendly(battle.party[battle.party.size() - 1])
			var i: int = c["action_bar"].find(args["cast"])
			_use_slot(i, false))
	elif args.has("training"):
		_start_training.call_deferred()


# ================================================================ Charakter laden
func _load_character() -> void:
	var id := str(Router.take_param("id", ""))
	if Settings.user_args.has("char"):
		for ch in SaveGame.list():
			if ch["name"] == Settings.user_args["char"]:
				id = ch["id"]
	if id == "" or SaveGame.get_character(id).is_empty():
		id = SaveGame.last_selected
	c = SaveGame.get_character(id)
	if c.is_empty():
		# Kein Charakter (nur beim direkten Testen der Szene): voruebergehenden anlegen
		c = CharacterFactory.create_player({"name": "Test"})
	hardcore = c.get("mode", "normal") == "hardcore"
	world_n = clampi(int(c.get("world", 1)), 1, 10)
	if not CombatData.has_world(world_n):
		world_n = 1
	c["world"] = world_n
	wave_n = clampi(int(c.get("wave", 1)), 1, Progression.unlocked_wave(c, world_n))
	c["wave"] = wave_n
	if not c.has("auto_continue"):
		c["auto_continue"] = false
	if not c.has("repeat_wave"):
		c["repeat_wave"] = false
	if not c.has("hc_threshold"):
		c["hc_threshold"] = int(CombatData.g("hardcore_mana_threshold_default", 80))
	if Progression.ensure_group(c):
		_save()
	Progression.ensure_spells(c)


func _save() -> void:
	if c.has("id") and not SaveGame.get_character(c["id"]).is_empty():
		c["playtime"] = float(c.get("playtime", 0.0)) + _playtime_acc
		_playtime_acc = 0.0
		SaveGame.save_character(c)


func _weak() -> float:
	return float(CombatData.g("revive_weakness", 0.25))


# ================================================================ Oberflaeche
static func hud_layout() -> Dictionary:
	if HL.is_empty():
		var f := FileAccess.open("res://data/hud_layout.json", FileAccess.READ)
		HL = JSON.parse_string(f.get_as_text())
	return HL


func _build_hud() -> void:
	var hl := hud_layout()
	# Gravierte Steinsaeule links (NPC-Leiste) und verzierte untere Leiste
	var col: Dictionary = hl["column"]
	var left := UI.texture("res://assets/gfx/hud/left_column.png")
	left.stretch_mode = TextureRect.STRETCH_KEEP
	left.position = Vector2(col["x"], col["y"])
	add_child(left)
	_build_npc_bar()
	var pan: Dictionary = hl["panel"]
	var bottom := UI.texture("res://assets/gfx/hud/bottom_panel.png")
	bottom.stretch_mode = TextureRect.STRETCH_KEEP
	bottom.position = Vector2(pan["x"], pan["y"])
	add_child(bottom)

	_top = TopBar.new()
	add_child(_top)
	_top.setup(world_n, CombatData.wave_count(world_n), hardcore, bool(c["auto_continue"]), bool(c["repeat_wave"]), int(c["hc_threshold"]))
	_top.wave_clicked.connect(_on_wave_clicked)
	_top.auto_changed.connect(func(on):
		c["auto_continue"] = on
		if on:
			c["repeat_wave"] = false
		_save()
		_after_wave_setup(false))
	_top.repeat_changed.connect(func(on):
		c["repeat_wave"] = on
		if on:
			c["auto_continue"] = false
		_save()
		_after_wave_setup(false))
	_top.threshold_changed.connect(func(v):
		c["hc_threshold"] = v)

	_friendly_tf = TargetFrame.new(false, 130)
	_friendly_tf.position = Vector2(50, TopBar.H + 4)
	add_child(_friendly_tf)
	_enemy_tf = TargetFrame.new(true, 238)
	_enemy_tf.position = Vector2(184, TopBar.H + 4)
	add_child(_enemy_tf)
	_boss = BossFrame.new()
	_boss.position = Vector2(426, TopBar.H + (18 if hardcore else 4))
	add_child(_boss)

	_frame_box = Control.new()
	_frame_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_frame_box)

	var xl: Dictionary = hl["xp"]
	_xp_bar = XpBar.new(float(xl["w"]), float(xl["h"]))
	_xp_bar.position = Vector2(xl["x"], xl["y"])
	_xp_bar.character = c
	add_child(_xp_bar)

	var cb: Dictionary = hl["cast"]
	_cast_bar = CastBar.new(int(cb["w"]), int(cb["h"]))
	_cast_bar.position = Vector2(cb["x"], cb["y"])
	add_child(_cast_bar)

	# Mana-Rinne, Aktionsleiste und Mikromenue in ihren Fassungen
	var mn: Dictionary = hl["mana"]
	_mana_bar = ManaBar.new(float(mn["w"]), float(mn["h"]))
	_mana_bar.position = Vector2(mn["x"], mn["y"])
	_mana_bar.character = c
	add_child(_mana_bar)
	var ab: Dictionary = hl["bar"]
	_bar = ActionBar.new(int(ab["slot"]), int(ab["gap"]))
	_bar.battle = battle
	_bar.position = Vector2(ab["x"], ab["y"])
	_bar.slot_pressed.connect(func(i): _use_slot(i, false))
	_bar.bar_changed.connect(func(list):
		c["action_bar"] = list
		_save())
	add_child(_bar)
	_bar.set_spells(c["action_bar"])

	var mi: Dictionary = hl["micro"]
	var cell := int(mi["cell"])
	var micro := GridContainer.new()
	micro.columns = int(mi["cols"])
	micro.add_theme_constant_override("h_separation", 0)
	micro.add_theme_constant_override("v_separation", 0)
	micro.position = Vector2(mi["x"], mi["y"])
	for m in MICRO:
		if m[0] == "micro_spellbook":
			# Zauberbuch (Taste P)
			var sb := UI.icon_button("res://assets/gfx/combat/micro_spellbook.png", "MICRO_SPELLBOOK_OPEN")
			sb.theme_type_variation = "FlatButton"
			sb.custom_minimum_size = Vector2(cell, cell)
			sb.pressed.connect(toggle_spellbook)
			micro.add_child(sb)
		elif m[0] == "micro_options":
			# Optionen gibt es schon: oeffnet das Optionsfenster
			var b := UI.icon_button("res://assets/gfx/combat/micro_options.png", m[1])
			b.icon = Hud.combat_tex("micro_options")
			b.theme_type_variation = "FlatButton"
			b.custom_minimum_size = Vector2(cell, cell)
			b.pressed.connect(func(): add_child(OptionsDialog.new()))
			micro.add_child(b)
		else:
			micro.add_child(LockedIcon.new(m[0], m[1], Vector2(cell, cell)))
	add_child(micro)

	_build_center()

	_error = UI.label("", "ErrorLabel", HORIZONTAL_ALIGNMENT_CENTER)
	_error.position = Vector2(170, 60)
	_error.size = Vector2(340, 10)
	add_child(_error)
	_banner = UI.label("", "TitleLabel", HORIZONTAL_ALIGNMENT_CENTER)
	_banner.position = Vector2(0, 88)
	_banner.size = Vector2(640, 20)
	_banner.modulate.a = 0.0
	add_child(_banner)
	_banner_sub = UI.label("", "", HORIZONTAL_ALIGNMENT_CENTER)
	_banner_sub.position = Vector2(0, 110)
	_banner_sub.size = Vector2(640, 10)
	_banner_sub.modulate.a = 0.0
	add_child(_banner_sub)


func _build_npc_bar() -> void:
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 6)
	box.position = Vector2(5, TopBar.H + 6)
	_trainer_btn = NpcButton.new("npc_trainer", "NPC_TRAINER")
	_trainer_btn.pressed.connect(toggle_trainer)
	box.add_child(_trainer_btn)
	for n in [["npc_blacksmith", "NPC_BLACKSMITH_LOCKED"], ["npc_weaponmaster", "NPC_WEAPONMASTER_LOCKED"]]:
		box.add_child(LockedIcon.new(n[0], n[1], Vector2(34, 34)))
	add_child(box)
	var coin := UI.texture("res://assets/gfx/icons/coin.png")
	var gold_box: Array = hud_layout()["column"]["gold"]
	coin.position = Vector2(gold_box[0] + 3, gold_box[1] + 2)
	coin.size = Vector2(9, 9)
	coin.stretch_mode = TextureRect.STRETCH_KEEP
	add_child(coin)
	_gold = UI.label("", "GoldLabel")
	_gold.position = Vector2(gold_box[0] + 13, gold_box[1] + 1)
	_gold.size = Vector2(30, 10)
	_gold.tooltip_text = "NPC_GOLD"
	_gold.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_gold)


func _build_center() -> void:
	_center = UI.vbox(3)
	_center.alignment = BoxContainer.ALIGNMENT_CENTER
	_center.position = Vector2(320 - 152, 70)
	_center.custom_minimum_size = Vector2(304, 0)
	_center.size = Vector2(304, 120)
	var panel := UI.panel("PlainPanel")
	var pv := UI.vbox(2)
	panel.add_child(pv)
	_quest_title = UI.label("", "GoldLabel", HORIZONTAL_ALIGNMENT_CENTER)
	pv.add_child(_quest_title)
	_quest_text = UI.wrap_label("", 290, "HintLabel")
	_quest_text.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	pv.add_child(_quest_text)
	_center.add_child(panel)
	var row := UI.hbox(6)
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	_start_btn = UI.button("GAME_START_WAVE", 150, true)
	_start_btn.theme_type_variation = "RedButtonSmall"
	_start_btn.pressed.connect(_start_wave)
	row.add_child(_start_btn)
	_train_btn = UI.button("GAME_TRAINING", 0, false)
	_train_btn.icon = Hud.combat_tex("icon_dummy")
	_train_btn.tooltip_text = "GAME_TRAINING_TIP"
	_train_btn.custom_minimum_size = Vector2(0, 22)
	_train_btn.pressed.connect(_start_training)
	row.add_child(_train_btn)
	_center.add_child(row)
	_status = UI.label("", "GoldLabel", HORIZONTAL_ALIGNMENT_CENTER)
	_center.add_child(_status)
	add_child(_center)
	_train_end = UI.button("GAME_TRAINING_END", 150, true)
	_train_end.theme_type_variation = "RedButtonSmall"
	_train_end.position = Vector2(320 - 75, 64)
	_train_end.visible = false
	_train_end.pressed.connect(_end_training)
	add_child(_train_end)


# ================================================================ Gruppe
func _build_party() -> void:
	var units: Array = []
	player = CombatUnit.make_party(c, "priest", true, _weak(), CombatData.boon_mults(c, "player"))
	player.slot = 0
	units.append(player)
	var members: Array = c.get("group", []).duplicate()
	# Tanks nach vorne, dann Nahkampf, dann Fernkampf
	members.sort_custom(func(a, b): return _front_rank(a) < _front_rank(b))
	for i in members.size():
		var m: Dictionary = members[i]
		var u := CombatUnit.make_party(m, str(m.get("class", "warrior")), false, _weak(), CombatData.boon_mults(c, "group"))
		u.slot = 10 - i
		units.append(u)
	battle.setup_party(units)
	var looks := {}
	for u in units:
		looks[u] = CharacterFactory.appearance_of(u.data, "priest" if u.is_player else u.klass)
	field.add_party(units, looks)
	_mana_bar.unit = player
	_cast_bar.unit = player
	_build_frames(units)
	if friendly_target and not friendly_target in units:
		_set_friendly(null)


func _front_rank(m: Dictionary) -> int:
	var cd := CombatData.class_def(str(m.get("class", "warrior")))
	if cd.get("role", "") == "tank":
		return 0
	return 2 if cd.get("ranged", false) else 1


func _build_frames(units: Array) -> void:
	for ch in _frame_box.get_children():
		ch.queue_free()
	_frames.clear()
	# Reihenfolge im Gruppenfenster: Spieler zuerst, dann wie in der Aufstellung von vorne
	var order: Array = units.duplicate()
	order.sort_custom(func(a, b): return (0 if a.is_player else 1) < (0 if b.is_player else 1) or \
		(a.is_player == b.is_player and a.slot > b.slot))
	# Rahmen so breit wie moeglich, damit das Gruppenfenster die Leiste fuellt
	var tray: Dictionary = hud_layout()["tray"]
	var fw := clampi(int((float(tray["w"]) - 4 - (order.size() - 1) * FRAME_GAP) / order.size()), UnitFrame.W, UnitFrame.W_MAX)
	var total := order.size() * fw + (order.size() - 1) * FRAME_GAP
	var x := 320 - total / 2
	for u in order:
		var f := UnitFrame.new(u, fw)
		f.position = Vector2(x, float(tray["y"]))
		f.clicked.connect(func(unit): _set_friendly(unit))
		f.hovered.connect(func(unit, inside):
			if inside:
				hover_unit = unit
			elif hover_unit == unit:
				hover_unit = null)
		_frame_box.add_child(f)
		_frames[u] = f
		x += fw + FRAME_GAP


# ================================================================ Wellen
func _load_wave(n: int) -> void:
	wave_n = clampi(n, 1, CombatData.wave_count(world_n))
	c["wave"] = wave_n
	var wd := CombatData.wave(world_n, wave_n)
	var foes: Array = []
	for id in wd.get("enemies", []):
		foes.append(CombatUnit.make_enemy(world_n, id, int(wd.get("level", 1)), hardcore))
	battle.set_enemies(foes)
	field.set_background(str(wd.get("bg", "gruenhain_day")))
	field.set_enemies(foes)
	_set_enemy(null)
	var boss: CombatUnit = null
	for e in foes:
		if e.type == "boss":
			boss = e
	_boss.show_unit(boss)
	_refresh_top()
	var key := "QUEST_%d_%d" % [world_n, wave_n]
	_quest_title.text = Loc.t("TOP_WAVE_TITLE", {"n": wave_n, "name": tr(key + "_NAME")})
	_quest_text.text = key + "_TEXT"


func _refresh_top() -> void:
	var done := int(c.get("highest_wave", 0)) if world_n == int(c.get("highest_world", 1)) else CombatData.wave_count(world_n)
	_top.set_progress(wave_n, Progression.unlocked_wave(c, world_n), done)


## Nach einer Welle (oder beim Start): Pause/Countdown fuer die naechste Welle vorbereiten.
func _after_wave_setup(from_result: bool) -> void:
	if phase == Phase.FIGHT or phase == Phase.TRAINING:
		return
	phase = Phase.READY
	_center.visible = true
	if from_result:
		# Questfenster erst einblenden, wenn Sieg-/Level-Banner verblasst sind
		_center.modulate.a = 0.0
		var tw := create_tween()
		tw.tween_interval(2.4)
		tw.tween_property(_center, "modulate:a", 1.0, 0.4)
	else:
		_center.modulate.a = 1.0
	_countdown = -1.0
	_wait_mana = false
	var auto := bool(c.get("auto_continue", false)) or bool(c.get("repeat_wave", false))
	if auto:
		if hardcore:
			_wait_mana = true
		else:
			_countdown = float(CombatData.g("wave_pause", 5.0))
	_update_status()


func _update_status() -> void:
	if _popups > 0 and (_countdown > 0.0 or _wait_mana):
		_status.text = ""
	elif _countdown > 0.0:
		_status.text = Loc.t("GAME_COUNTDOWN", {"s": int(ceil(_countdown))})
	elif _wait_mana:
		_status.text = Loc.t("GAME_WAIT_MANA", {"p": int(c["hc_threshold"])})
	else:
		_status.text = ""


func _start_wave() -> void:
	if phase != Phase.READY or _popups > 0:
		return
	if not player.alive:
		return
	phase = Phase.FIGHT
	_countdown = -1.0
	_wait_mana = false
	_center.visible = false
	_wave_xp = 0
	_pending_gold = 0
	_died = {}
	Sfx.play("wave_start")
	battle.start_fight()
	_show_banner(Loc.t("TOP_WAVE_TITLE", {"n": wave_n, "name": tr("QUEST_%d_%d_NAME" % [world_n, wave_n])}), "", 1.6)


func _on_wave_clicked(i: int) -> void:
	if phase == Phase.FIGHT or phase == Phase.TRAINING:
		_show_error("ERR_IN_COMBAT")
		return
	if i > Progression.unlocked_wave(c, world_n):
		Sfx.play("ui_error")
		return
	Sfx.play("ui_select")
	_load_wave(i)
	_save()
	_after_wave_setup(false)


func _on_finished(victory: bool) -> void:
	phase = Phase.RESULT
	var done_wave := wave_n
	var boss_wave := CombatData.is_boss_wave(world_n, wave_n)
	var fell: Array = []                 # Hardcore: permanent gestorbene Mitglieder
	var lines: Array = []
	if victory:
		Sfx.play("victory")
		var first := Progression.mark_wave_done(c, world_n, wave_n)
		var quest_xp := CombatData.quest_xp(wave_n, boss_wave) if first else 0
		var quest_gold := CombatData.quest_gold(wave_n) if first else 0
		# Tote nach der Welle
		for u in battle.party:
			if not u.alive:
				if hardcore:
					if u.is_player:
						# Gruppe hat gewonnen: der Spieler ueberlebt mit wenig HP und Mana
						u.alive = true
						u.hp = u.max_hp * float(CombatData.g("hardcore_survivor_hp", 0.2))
						u.res = u.res_max * float(CombatData.g("hardcore_survivor_mana", 0.2))
					else:
						fell.append(u)
				else:
					_revive(u, true)
			elif not hardcore:
				_set_weak(u, false)
		# EP und Gold
		var gold := _pending_gold + quest_gold
		c["gold"] = int(c.get("gold", 0)) + gold
		_grant_quest_xp(quest_xp, fell)
		# Hardcore: Gefallene verlassen die Gruppe, ihre Items sind verloren
		for u in fell:
			c["group"] = c["group"].filter(func(m): return m.get("id", "") != u.id)
		var free := Progression.ensure_group(c)
		_store_party_state()
		# Welle weiterschalten
		var next := wave_n
		if not bool(c.get("repeat_wave", false)) and wave_n < CombatData.wave_count(world_n):
			next = wave_n + 1
		c["wave"] = next
		_save()
		if not fell.is_empty() or free:
			_build_party()
		else:
			_refresh_party_stats()
		_load_wave(next)
		_show_banner("GAME_VICTORY", Loc.t("GAME_VICTORY_REWARD", {"xp": _wave_xp, "gold": gold}), 2.6)
		if first:
			_popup_quest(done_wave, quest_xp, quest_gold, boss_wave)
		for u in fell:
			_popup_info("GAME_HC_MEMBER_FELL_TITLE", Loc.t("GAME_HC_MEMBER_FELL", {"name": u.name}))
		if free:
			_popup_info("GAME_FREE_WARRIOR_TITLE", Loc.t("GAME_FREE_WARRIOR", {"name": c["group"][0]["name"]}))
		if first and boss_wave:
			_popup_info("GAME_WORLD_DONE_TITLE", Loc.t("GAME_WORLD_DONE", {"world": tr(Loc.world_name(world_n))}))
		_after_wave_setup(true)
		_offer_boons()
	else:
		Sfx.play("defeat")
		if hardcore:
			c["fallen"] = true
			_store_party_state()
			_save()   # Tod sofort speichern (GDD 26.1)
			_popup_fallen()
			return
		# Normal: alle stehen mit Wiederbelebungsschwaeche wieder auf, eine Welle zurueck
		for u in battle.party:
			_revive(u, not u.alive or _died.has(u))
		c["gold"] = int(c.get("gold", 0)) + _pending_gold
		_store_party_state()
		var back := maxi(1, wave_n - 1)
		c["wave"] = back
		_save()
		_refresh_party_stats()
		_load_wave(back)
		_popup_defeat(back)
		_after_wave_setup(true)
		_offer_boons()


## Normal-Modus: Figur steht wieder auf (voll) und traegt ggf. die Wiederbelebungsschwaeche.
func _revive(u: CombatUnit, weak: bool) -> void:
	u.alive = true
	_set_weak(u, weak)
	u.hp = u.max_hp
	if u.resource == "mana":
		u.res = u.res_max
	if weak:
		battle.apply_aura(u, {"id": "revive_weakness", "icon": "aura_revive_weakness", "kind": "debuff",
			"permanent": true, "name": "AURA_REVIVE_WEAKNESS"})


func _set_weak(u: CombatUnit, weak: bool) -> void:
	u.weakened = weak
	u.data["weakened"] = weak
	if not weak:
		u.auras = u.auras.filter(func(a): return a["id"] != "revive_weakness")
	u.recalc(_weak())
	if not hardcore:
		u.hp = u.max_hp
		if u.resource == "mana":
			u.res = u.res_max


## Quest-EP am Wellenende fuer alle, die noch in der Gruppe sind (Hardcore: Gefallene nicht).
func _grant_quest_xp(quest_xp: int, excluded: Array) -> void:
	for u in battle.party:
		if not u in excluded:
			_give_xp(u, quest_xp)


## EP sofort gutschreiben (Kills und Quests). Ein Level-Up passiert direkt, wie in WoW.
func _give_xp(u: CombatUnit, amount: int) -> void:
	if amount <= 0:
		return
	var d: Dictionary = c if u.is_player else u.data
	var ups := Progression.add_xp(d, amount)
	if u.is_player:
		_wave_xp += amount
	if not ups.is_empty():
		_level_up(u, ups)


## Level-Up: Werte neu berechnen, HP und Mana voll auffuellen (alle Modi), starker Effekt.
func _level_up(u: CombatUnit, ups: Array) -> void:
	var d: Dictionary = c if u.is_player else u.data
	u.level = int(d["level"])
	u.recalc(_weak())
	if u.alive:
		u.hp = u.max_hp
		if u.resource == "mana":
			u.res = u.res_max
	field.level_up_fx(u)
	if u in _frames:
		_frames[u].flash_level_up()
	if u.is_player:
		_show_level_up(ups)
		_screen_flash()
		# pro Level-Up eine Segen-Wahl (erscheint nach der Welle)
		var pend: Array = c.get("boon_pending", [])
		pend.append_array(ups)
		c["boon_pending"] = pend
	else:
		Sfx.play("level_up", 1.12, -3.0)
		field.float_text(u, Loc.t("GAME_MEMBER_LEVEL", {"level": u.level}), Color("ffe08a"), true, -14)


## Aktuelle HP/Ressource in die Speicherdaten (Hardcore: kein Auffuellen zwischen den Wellen).
func _store_party_state() -> void:
	for u in battle.party:
		var d: Dictionary = c if u.is_player else u.data
		d["hp_frac"] = u.hp_frac() if u.alive else 0.0
		d["res_frac"] = u.res_frac()
		d["weakened"] = u.weakened
		d["level"] = u.level


func _refresh_party_stats() -> void:
	for u in battle.party:
		u.target = null


# ================================================================ Trainingspuppe
func _start_training() -> void:
	if phase != Phase.READY or _popups > 0:
		return
	phase = Phase.TRAINING
	_countdown = -1.0
	_wait_mana = false
	_training_snapshot = {}
	for u in battle.party:
		_training_snapshot[u] = {"hp": u.hp, "res": u.res, "alive": u.alive, "auras": u.auras.duplicate(true),
			"cooldowns": u.cooldowns.duplicate()}
		u.immortal = true
	var dummy := CombatUnit.make_enemy(world_n, "training_dummy", maxi(1, player.level), false)
	dummy.name = "ENEMY_TRAINING_DUMMY"
	field.set_enemies([dummy])
	_boss.show_unit(null)
	battle.start_training(dummy)
	_set_enemy(dummy)
	_center.visible = false
	_train_end.visible = true
	Sfx.play("ui_open")


func _end_training() -> void:
	if phase != Phase.TRAINING:
		return
	battle.stop()
	for u in battle.party:
		var s: Dictionary = _training_snapshot.get(u, {})
		u.immortal = false
		if s.is_empty():
			continue
		u.hp = s["hp"]
		u.res = s["res"]
		u.alive = s["alive"]
		u.auras = s["auras"]
		u.cooldowns = s["cooldowns"]
		u.cast = {}
	_train_end.visible = false
	phase = Phase.READY
	Sfx.play("ui_close")
	_load_wave(wave_n)
	_after_wave_setup(false)


# ================================================================ Ziele und Zaubern
func _set_friendly(u: CombatUnit) -> void:
	friendly_target = u
	_friendly_tf.show_unit(u, player.level if player else 1)
	_update_selection()


func _set_enemy(u: CombatUnit) -> void:
	enemy_target = u
	_enemy_tf.show_unit(u, player.level if player else 1)
	_update_selection()


func _update_selection() -> void:
	for u in field.figures:
		field.figures[u].selected = (u == friendly_target or u == enemy_target)
	for u in _frames:
		_frames[u].selected = u == friendly_target


func _next_enemy() -> void:
	var foes := battle.alive_enemies()
	if foes.is_empty():
		return
	foes.sort_custom(func(a, b): return a.slot < b.slot)
	var i := foes.find(enemy_target)
	_set_enemy(foes[(i + 1) % foes.size()])
	Sfx.play("ui_toggle")


func _use_slot(i: int, from_key: bool) -> void:
	var bar: Array = c.get("action_bar", [])
	if i < 0 or i >= bar.size() or bar[i] == "":
		return
	var id: String = bar[i]
	var sp := CombatData.spell(id)
	var t: CombatUnit = null
	var mouse := hover_unit if from_key else null
	if sp.get("target", "") == "enemy":
		if mouse and mouse.side == "enemy":
			t = mouse
		elif enemy_target and enemy_target.alive:
			t = enemy_target
		else:
			# Ohne Ziel: der Gegner, den der Tank angreift
			for tk in battle.tanks():
				if tk.target and tk.target.alive:
					t = tk.target
					break
			if t == null and not battle.alive_enemies().is_empty():
				t = battle.alive_enemies()[0]
			if t:
				_set_enemy(t)
	else:
		if mouse and mouse.side == "party":
			t = mouse
		elif friendly_target:
			t = friendly_target
		else:
			t = player
	var err := battle.player_cast(id, t)
	_bar.flash_slot(i)
	if err != "":
		_show_error(err)


func _show_error(key: String) -> void:
	_error.text = key
	_error.modulate.a = 1.0
	var tw := create_tween()
	tw.tween_interval(0.9)
	tw.tween_property(_error, "modulate:a", 0.0, 0.4)
	Sfx.play("ui_error", 1.0, -6.0)


func _show_banner(text: String, sub: String, hold: float) -> void:
	_banner.text = text
	_banner_sub.text = sub
	for l in [_banner, _banner_sub]:
		l.modulate.a = 0.0
		var tw := create_tween()
		tw.tween_property(l, "modulate:a", 1.0, 0.2)
		tw.tween_interval(hold)
		tw.tween_property(l, "modulate:a", 0.0, 0.5)


# ================================================================ Kampfereignisse
func _on_event(e: Dictionary) -> void:
	var u: CombatUnit = e.get("unit")
	var fig := field.figure_of(u) if u else null
	match e["type"]:
		"damage":
			var amount := int(e["amount"])
			var src: CombatUnit = e.get("source")
			if src and src.side == "party" and u.side == "enemy":
				_share_action_xp(float(e["amount"]), "damage")
			if fig:
				fig.play_hit(Color(1, 0.4, 0.3) if u.side == "party" else Color.WHITE)
			if int(e.get("absorbed", 0)) > 0:
				field.float_text(u, tr("GAME_ABSORBED"), Color("e8f0ff"), false, 8)
			if amount > 0:
				var col := Color("ffe040") if e.get("crit", false) else Color("fbf7ee")
				if u.side == "party":
					col = Color("ff9a8a") if not e.get("crit", false) else Color("ff5a4a")
				field.float_text(u, ("%d" % amount) + ("!" if e.get("crit", false) else ""), col, e.get("crit", false))
			var ab := str(e.get("ability", ""))
			if ab in ["smite"]:
				field.burst(u, "holy")
				Sfx.play("smite_hit")
			elif ab == "sw_pain":
				field.burst(u, "shadow")
				Sfx.play("shadow_hit", _rng.randf_range(0.95, 1.08), -4.0)
			elif ab == "training":
				Sfx.play("hit_physical", 1.1, -10.0)
			elif e.get("school", "") == "magic":
				field.burst(u, "magic")
				Sfx.play("hit_magic", _rng.randf_range(0.95, 1.05))
			else:
				Sfx.play("hit_heavy" if e.get("crit", false) or amount > u.max_hp * 0.2 else "hit_physical", _rng.randf_range(0.92, 1.08))
		"heal":
			var amount := int(e["amount"])
			var hsrc: CombatUnit = e.get("source")
			if hsrc and hsrc.side == "party":
				_share_action_xp(float(e["amount"]), "heal")   # nur echte Heilung, Ueberheilung zaehlt nicht
			if amount > 0:
				field.float_text(u, "+%d" % amount + ("!" if e.get("crit", false) else ""), Color("6af06a"), e.get("crit", false))
			field.burst(u, "hot" if e.get("spell", "") == "renew" else "heal")
			if e.get("spell", "") != "renew":
				Sfx.play("heal_land")
		"spell":
			if fig:
				fig.play_spell()
			if e.get("spell", "") == "renew":
				Sfx.play("hot_apply")
				field.burst(e["target"], "hot")
		"cast_start":
			if fig:
				fig.play_cast_start(str(e.get("anim", "cast")))
			if u.side == "party":
				Sfx.play("cast_holy", 1.0, -6.0)
			else:
				match str(e.get("mechanic", "")):
					"tank_buster":
						Sfx.play("warn_buster")
						_show_banner("", Loc.t("GAME_ANNOUNCE", {"name": tr(u.name), "ability": tr(e["name"])}), 1.2)
					"aoe":
						Sfx.play("warn_aoe")
						_show_banner("", Loc.t("GAME_ANNOUNCE", {"name": tr(u.name), "ability": tr(e["name"])}), 1.2)
					_:
						Sfx.play("cast_enemy", 1.0, -8.0)
		"cast_stop":
			if fig:
				fig.play_cast_end()
			if u == player:
				_cast_bar.show_stop("GAME_CAST_CANCELLED" if e.get("cancelled", false) else "GAME_CAST_FAILED")
		"cast_done":
			if fig:
				fig.play_cast_end()
			if u == player:
				_cast_bar.show_done()
		"attack":
			if fig:
				fig.play_attack(e.get("strong", false))
			Sfx.play("swing", _rng.randf_range(0.9, 1.15), -10.0)
		"death":
			if u.side == "enemy":
				Sfx.play("death_enemy")
				_reward_kill(u)
				if u == enemy_target:
					_set_enemy(null)
			else:
				_died[u] = true
				Sfx.play("death_party")
				field.float_text(u, tr("FRAME_DEAD"), Color("9a90a8"))
		"phase":
			Sfx.play("warn_aoe")
			_show_banner("", Loc.t("GAME_BOSS_PHASE_%s" % u.klass.to_upper(), {"name": tr(u.name)}), 2.0)
		"taunt":
			var tf := field.figure_of(e["target"])
			if tf:
				field.float_text(e["target"], tr("ABILITY_TAUNT"), Color("ffb040"), false, -8)
			Sfx.play("taunt")
		"ability":
			if e.get("name", "") == "ABILITY_THUNDER_CLAP":
				Sfx.play("thunder_clap")
				for foe in battle.alive_enemies():
					field.burst(foe, "hit")
			elif e.get("name", "") == "ABILITY_SHIELD_WALL":
				Sfx.play("shield_wall")
				field.float_text(u, tr("ABILITY_SHIELD_WALL"), Color("8ac8ff"), false, -8)
		"error":
			_show_error(str(e["key"]))


## Heilung und Schaden geben der ganzen Gruppe EP (jede lebende Figur, Grau-Regel je Figur).
func _share_action_xp(points: float, kind: String) -> void:
	if phase != Phase.FIGHT or points <= 0.0:
		return
	var wl := int(CombatData.wave(world_n, wave_n).get("level", 1))
	for u in battle.party:
		if not u.alive:
			continue
		var lvl := int(c["level"]) if u.is_player else int(u.data.get("level", 1))
		var acc := float(_xp_acc.get(u, 0.0)) + CombatData.action_xp(points, kind, lvl, wl)
		var whole := int(acc)
		_xp_acc[u] = acc - whole
		if whole > 0:
			_give_xp(u, whole)


func _reward_kill(e: CombatUnit) -> void:
	if phase != Phase.FIGHT:
		return
	_pending_gold += CombatData.mob_gold(e.level, e.type, _rng)
	var own := CombatData.mob_xp(int(c["level"]), e.level, e.type) if player.alive else 0
	if own > 0:
		field.float_text(e, Loc.t("GAME_XP_FLOAT", {"xp": own}), Color("c8a0ff"), false, -12)
	# Jede lebende Figur bekommt ihre EP sofort (Grau-Regel je nach eigenem Level)
	for u in battle.party:
		if u.alive:
			var lvl := int(c["level"]) if u.is_player else int(u.data.get("level", 1))
			_give_xp(u, CombatData.mob_xp(lvl, e.level, e.type))


# ================================================================ Lehrmeister und Zauberbuch
func _window(id: String) -> GameWindow:
	for w in _windows:
		if w.window_id == id:
			return w
	return null


func _open_window(w: GameWindow) -> void:
	_windows.append(w)
	w.closed.connect(func(): _windows.erase(w))
	add_child(w)
	# Fenster liegen ueber dem HUD, aber unter Pop-ups und Menue
	for ch in get_children():
		if ch is ModalDialog:
			move_child(ch, get_child_count() - 1)


func toggle_trainer() -> void:
	var w := _window("trainer")
	if w:
		w.close()
		return
	# Lehrmeister und Zauberbuch teilen sich den Platz links
	if _window("spellbook"):
		_window("spellbook").close()
	var t := TrainerWindow.new(c, player)
	t.learned.connect(_on_learned)
	_open_window(t)


func toggle_spellbook() -> void:
	var w := _window("spellbook")
	if w:
		w.close()
		return
	if _window("trainer"):
		_window("trainer").close()
	_open_window(SpellbookWindow.new(c, player))


func _on_learned(_id: String, _rank: int) -> void:
	_bar.set_spells(c["action_bar"])
	var sb := _window("spellbook")
	if sb:
		sb.refresh()
	_save()


# ================================================================ Segen nach Level-Up
var _boon_open := false


## Zeigt die naechste offene Segen-Wahl (nicht waehrend eines Kampfes). Das Angebot wird gespeichert,
## damit es sich durch Neustarten nicht neu wuerfeln laesst.
func _offer_boons() -> void:
	if _boon_open or phase == Phase.FIGHT or phase == Phase.TRAINING or bool(c.get("fallen", false)):
		return
	var pend: Array = c.get("boon_pending", [])
	if pend.is_empty():
		return
	if c.get("boon_offer", []).is_empty():
		c["boon_offer"] = CombatData.roll_boon_offer(_rng)
		_save()
	_boon_open = true
	var d := BoonDialog.new(int(pend[0]), c["boon_offer"], c)
	d.chosen.connect(_apply_boon)
	d.closed.connect(func():
		_boon_open = false
		_offer_boons.call_deferred())
	_open_popup(d)


func _apply_boon(b: Dictionary) -> void:
	var boons: Array = c.get("boons", [])
	boons.append({"stat": b["stat"], "target": b["target"], "pct": float(b["pct"]), "rarity": b["rarity"]})
	c["boons"] = boons
	var pend: Array = c.get("boon_pending", [])
	if not pend.is_empty():
		pend.remove_at(0)
	c["boon_pending"] = pend
	c["boon_offer"] = []
	# Werte sofort neu berechnen (HP/Mana bleiben anteilig)
	for u in battle.party:
		if u.is_player == (b["target"] == "player"):
			u.mults = CombatData.boon_mults(c, b["target"])
			u.recalc(_weak())
			field.burst(u, "heal")
	_store_party_state()
	_save()


# ================================================================ Pop-ups
func _open_popup(d: ModalDialog) -> void:
	_popups += 1
	d.closed.connect(func():
		_popups -= 1
		_update_status())
	add_child(d)
	_update_status()


func _popup_quest(n: int, xp: int, gold: int, boss: bool) -> void:
	var key := "QUEST_%d_%d" % [world_n, n]
	var d := ModalDialog.new("GAME_QUEST_DONE", 280)
	d.body.add_child(UI.label(tr(key + "_NAME"), "GoldLabel", HORIZONTAL_ALIGNMENT_CENTER))
	var done := UI.wrap_label(key + "_DONE", 264, "HintLabel")
	done.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	d.body.add_child(done)
	d.body.add_child(UI.separator())
	d.body.add_child(UI.label("GAME_REWARD", "DimLabel", HORIZONTAL_ALIGNMENT_CENTER))
	d.body.add_child(UI.label(Loc.t("GAME_REWARD_LINE", {"xp": xp, "gold": gold}), "", HORIZONTAL_ALIGNMENT_CENTER))
	var ok := d.add_button("GAME_OK", true, 90)
	ok.pressed.connect(d.close)
	Sfx.play("quest_done")
	_open_popup(d)


func _popup_info(title_key: String, text: String) -> void:
	var d := ModalDialog.new(title_key, 280)
	var l := UI.wrap_label(text, 264)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	d.body.add_child(l)
	var ok := d.add_button("GAME_OK", true, 90)
	ok.pressed.connect(d.close)
	_open_popup(d)


func _popup_defeat(back: int) -> void:
	var d := ModalDialog.new("GAME_DEFEAT_TITLE", 280)
	var l := UI.wrap_label(Loc.t("GAME_DEFEAT_TEXT", {"n": back}), 264)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	d.body.add_child(l)
	var l2 := UI.wrap_label("GAME_DEFEAT_WEAKNESS", 264, "DimLabel")
	l2.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	d.body.add_child(l2)
	var ok := d.add_button("GAME_OK", true, 90)
	ok.pressed.connect(d.close)
	_open_popup(d)


func _popup_fallen() -> void:
	var d := ModalDialog.new("GAME_FALLEN_TITLE", 290)
	d.closable = false
	var skull := UI.texture("res://assets/gfx/icons/skull.png")
	d.body.add_child(skull)
	var l := UI.wrap_label(Loc.t("GAME_FALLEN_TEXT", {"name": c.get("name", ""), "level": c.get("level", 1)}), 274)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	d.body.add_child(l)
	var ok := d.add_button("GAME_TO_SELECT", true, 180)
	ok.theme_type_variation = "RedButtonSmall"
	ok.pressed.connect(func(): _leave("character_select"))
	Sfx.play("hardcore")
	_open_popup(d)


func _show_level_up(levels: Array) -> void:
	Sfx.play("level_up")
	var level: int = levels[levels.size() - 1]
	var before := CombatData.class_stats("priest", int(levels[0]) - 1)
	var after := CombatData.class_stats("priest", level)
	var parts: Array = []
	for k in ["hp", "mana", "heal_power"]:
		parts.append(Loc.t("STAT_GAIN_%s" % k.to_upper(), {"v": int(round(after[k] - before[k]))}))
	var new_spells: Array = []
	for id in CombatData.bal()["spell_order"]:
		for r in CombatData.spell(id).get("ranks", []).size():
			if int(CombatData.spell(id)["ranks"][r]["level"]) in levels:
				new_spells.append("%s %s" % [tr("SPELL_%s" % id.to_upper()), Loc.t("SPELL_RANK", {"r": r + 1})])
	var sub := "  ".join(parts)
	if not new_spells.is_empty():
		sub += "   " + Loc.t("GAME_NEW_SPELLS", {"list": ", ".join(new_spells)})
	_show_banner(Loc.t("GAME_LEVEL_UP", {"level": level}), sub, 3.2)
	_xp_bar.flash()


## Starkes goldenes Aufleuchten des ganzen Bildschirms (eigenes Level-Up).
func _screen_flash() -> void:
	var r := ColorRect.new()
	r.color = Color(1.0, 0.9, 0.55)
	r.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var mat := CanvasItemMaterial.new()
	mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	r.material = mat
	r.modulate.a = 0.0
	add_child(r)
	var tw := create_tween()
	tw.tween_property(r, "modulate:a", 0.85, 0.08)
	tw.tween_property(r, "modulate:a", 0.25, 0.25)
	tw.tween_property(r, "modulate:a", 0.55, 0.12)
	tw.tween_property(r, "modulate:a", 0.0, 0.9).set_ease(Tween.EASE_OUT)
	tw.tween_callback(r.queue_free)


# ================================================================ ESC-Menue
func _open_menu() -> void:
	var d := ModalDialog.new("GAME_MENU", 180)
	d.process_mode = Node.PROCESS_MODE_ALWAYS
	get_tree().paused = true
	for entry in [["GAME_RESUME", "resume"], ["SELECT_OPTIONS", "options"], ["GAME_TO_SELECT", "select"], ["SELECT_QUIT", "quit"]]:
		var b := UI.button(entry[0], 170, entry[1] == "resume")
		if entry[1] == "resume":
			b.theme_type_variation = "RedButtonSmall"
		b.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
		d.body.add_child(b)
		match entry[1]:
			"resume":
				b.pressed.connect(d.close)
			"options":
				b.pressed.connect(func():
					var o := OptionsDialog.new()
					o.process_mode = Node.PROCESS_MODE_ALWAYS
					add_child(o))
			"select":
				b.pressed.connect(func(): _leave("character_select"))
			"quit":
				b.pressed.connect(func(): _leave("quit"))
	if phase == Phase.FIGHT:
		d.body.add_child(UI.wrap_label("GAME_MENU_FIGHT_HINT", 164, "DimLabel"))
	d.closed.connect(func(): get_tree().paused = false)
	add_child(d)


## Verlassen: Eine laufende Welle zaehlt nicht (GDD 26.1) - der Stand vor der Welle bleibt gespeichert.
func _leave(target: String) -> void:
	get_tree().paused = false
	if phase == Phase.TRAINING:
		_end_training()
	battle.stop()
	battle.set_process(false)
	if phase != Phase.FIGHT and phase != Phase.RESULT:
		_store_party_state()
	_save_playtime_only()
	if target == "quit":
		get_tree().quit()
	else:
		Router.go("character_select", {"select": c.get("id", "")})


## Nur die Spielzeit sichern (Kampfstand einer abgebrochenen Welle wird verworfen).
func _save_playtime_only() -> void:
	if not c.has("id") or SaveGame.get_character(c["id"]).is_empty():
		return
	if phase == Phase.FIGHT:
		# Stand von vor der Welle neu laden (EP/Level aus dieser Welle verfallen), nur Spielzeit ergaenzen
		var stored := SaveGame.reload_character(c["id"])
		stored["playtime"] = float(stored.get("playtime", 0.0)) + _playtime_acc
		_playtime_acc = 0.0
		SaveGame.save_character(stored)
	else:
		_save()


# ================================================================ Eingabe
func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if Router.busy:
			return
		var slot := ActionBar.slot_for_key(event)
		if slot != -1:
			get_viewport().set_input_as_handled()
			_use_slot(slot, true)
			return
		match event.physical_keycode:
			KEY_TAB:
				get_viewport().set_input_as_handled()
				_next_enemy()
			KEY_X:
				get_viewport().set_input_as_handled()
				battle.cancel_player_cast()
			KEY_P:
				get_viewport().set_input_as_handled()
				toggle_spellbook()
			KEY_ESCAPE:
				get_viewport().set_input_as_handled()
				if battle.cancel_player_cast():
					return
				if not _windows.is_empty():
					_windows[_windows.size() - 1].close()
					return
				_open_menu()


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion:
		var u := field.pick(event.position)
		for f in field.figures.values():
			f.hovered = f.unit == u
		# Ueber den Rahmen des Gruppenfensters kommt keine Mausbewegung hier an (die melden sich selbst)
		hover_unit = u
		mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND if u else Control.CURSOR_ARROW
	elif event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var u := field.pick(event.position)
		if u == null:
			_set_friendly(null)
			_set_enemy(null)
		elif u.side == "party":
			_set_friendly(u)
			Sfx.play("ui_toggle")
		else:
			_set_enemy(u)
			Sfx.play("ui_toggle")


# ================================================================ Takt
func _process(delta: float) -> void:
	_playtime_acc += delta
	_gold.text = str(int(c.get("gold", 0)))
	_trainer_btn.attention = Progression.learnable_summary(c)["count"] > 0
	# Aggro-Warnung und eingehende Heilung im Gruppenfenster
	for u in _frames:
		var f: UnitFrame = _frames[u]
		var aggro := false
		if not u.is_tank() and u.alive:
			for e in battle.enemies:
				if e.alive and e.aggro == u:
					aggro = true
		f.aggro = aggro
		f.incoming = 0.0
	if player and player.is_casting():
		var sp := CombatData.spell(player.cast["spell"])
		if sp.get("kind", "") == "heal" and player.cast["target"] in _frames:
			var rd := CombatData.rank_data(player.cast["spell"], int(player.cast["rank"]))
			_frames[player.cast["target"]].incoming = (float(rd["min"]) + float(rd["max"])) * 0.5 + player.stat("heal_power") * float(sp.get("coef", 0.0))
	if friendly_target and not friendly_target in _frames:
		_set_friendly(null)
	# Countdown / Mana-Schwelle bis zur naechsten Welle
	if phase == Phase.READY and _popups == 0:
		if _countdown > 0.0:
			_countdown -= delta
			if _countdown <= 0.0:
				_start_wave()
		elif _wait_mana and player.alive and player.res_frac() * 100.0 >= float(c.get("hc_threshold", 80)) - 0.001:
			_start_wave()
		_update_status()
	_start_btn.disabled = phase != Phase.READY or not player.alive
	_train_btn.disabled = phase != Phase.READY
