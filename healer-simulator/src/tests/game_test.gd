extends RefCounted
## Tests fuer Kampfregeln und Hauptbildschirm (wird vom Rauchtest aufgerufen).

var t: Node   # der Rauchtest (check, _wait)


func _init(test_node: Node) -> void:
	t = test_node


func check(cond: bool, what: String) -> void:
	t.check(cond, what)


# ---------------------------------------------------------------- Kampfregeln (ohne Szene)
func combat_rules() -> void:
	print("Kampfregeln")
	check(CombatData.xp_to_next(1) == 150 and CombatData.xp_to_next(2) > 150, "EP-Kurve steigt")
	check(CombatData.mob_xp(8, 3, "normal") == 0, "graue Gegner geben keine EP")
	check(CombatData.mob_xp(3, 3, "elite") == 2 * CombatData.mob_xp(3, 3, "normal"), "Elite doppelte EP")
	check(CombatData.spell_rank("lesser_heal", 1) == 1 and CombatData.spell_rank("lesser_heal", 4) == 2, "Zauberraenge nach Level")
	check(CombatData.known_spells(1) == ["lesser_heal", "smite"], "Level 1: zwei Startzauber")
	var c := CharacterFactory.create_player({"name": "Regel"})
	Progression.ensure_spells(c)
	check(c["spells"] == {"lesser_heal": 1, "smite": 1}, "neuer Charakter kennt nur die Startzauber")
	check(c["action_bar"][0] == "lesser_heal" and c["action_bar"][1] == "smite" and c["action_bar"].size() == 12, "Aktionsleiste 12 Plaetze")
	var ups := Progression.add_xp(c, 150 + 265 + 10)
	check(ups == [2, 3] and c["level"] == 3 and c["xp"] == 10, "Level-Up mit Rest-EP")
	check(CombatData.learned_rank(c, "renew") == 0, "Level-Up lernt keine Zauber (nur beim Lehrmeister)")
	# Lehrmeister
	c["gold"] = 5
	check(Progression.learn(c, "renew", 1) == "TRAINER_ERR_GOLD", "Lehrmeister: zu wenig Gold")
	c["gold"] = 100
	check(Progression.learn(c, "lesser_heal", 2) == "TRAINER_ERR_LEVEL", "Lehrmeister: Stufe zu niedrig")
	var price := CombatData.trainer_price(2)
	check(Progression.learn(c, "renew", 1) == "" and int(c["gold"]) == 100 - price and CombatData.learned_rank(c, "renew") == 1,
		"Lehrmeister: Erneuerung R1 gelernt, Gold abgezogen")
	check(c["action_bar"][2] == "renew", "neu gelernter Zauber kommt auf einen freien Platz")
	check(Progression.learn(c, "renew", 1) == "TRAINER_ERR_KNOWN", "Lehrmeister: schon gelernt")
	var old_save := {"level": 5, "action_bar": ["lesser_heal"]}
	Progression.ensure_spells(old_save)
	check(CombatData.learned_rank(old_save, "lesser_heal") == 2 and CombatData.learned_rank(old_save, "sw_pain") == 1,
		"alte Spielstaende behalten alle bisher automatisch bekannten Raenge")
	# Bedrohung: Tank haelt Aggro, Wechsel erst ueber 130 % (Fernkampf)
	var b := Battle.new()
	var p := CombatUnit.make_party(c, "priest", true, 0.25)
	var w := CombatUnit.make_party(c["group"][0], "warrior", false, 0.25)
	w.slot = 10
	b.setup_party([p, w])
	var e := CombatUnit.make_enemy(1, "wolf_young", 1, false)
	b.set_enemies([e])
	b.start_fight()
	check(e.aggro == w, "Gegner greift zu Beginn den Tank an")
	e.threat[w] = 100.0
	e.threat[p] = 125.0
	b._pick_aggro(e)
	check(e.aggro == w, "kein Zielwechsel unter 130 %")
	e.threat[p] = 131.0
	b._pick_aggro(e)
	check(e.aggro == p, "Heiler zieht Aggro ueber 130 %")
	w.gcd = 0.0
	w.target = e
	b._warrior_ai(w)
	check(e.aggro == w, "Krieger spottet den Gegner zurueck")
	var before := w.hp
	b.deal_damage(e, w, 100.0, "physical", false, "test")
	check(before - w.hp < 100.0 and before - w.hp > 50.0, "Ruestung verringert physischen Schaden")
	w.hp = 50.0
	var mana := p.res
	check(b.player_cast("lesser_heal", w) == "", "Geringe Heilung gestartet")
	check(p.is_casting(), "Zauber hat Castzeit")
	check(b.player_cast("lesser_heal", w) in ["ERR_BUSY", ""], "waehrend des Zauberns kein zweiter")
	for i in 60:
		b.step(0.05)
	check(w.hp > 50.0 and p.res < mana, "Heilung angekommen, Mana verbraucht")
	p.res = 0.0
	p.gcd = 0.0
	check(b.player_cast("lesser_heal", w) == "ERR_NO_MANA", "zu wenig Mana")
	b.free()
	# Segen: 3 verschiedene Angebote, Wirkung als +% auf die Werte
	var rng := RandomNumberGenerator.new()
	rng.seed = 5
	var offer := CombatData.roll_boon_offer(rng)
	var keys := offer.map(func(o): return o["target"] + o["stat"])
	check(offer.size() == 3 and keys[0] != keys[1] and keys[1] != keys[2] and keys[0] != keys[2], "Segen: 3 verschiedene Angebote")
	var bc := CharacterFactory.create_player({"name": "Segen"})
	var plain := CombatUnit.make_party(bc, "priest", true, 0.25)
	bc["boons"] = [{"stat": "mana", "target": "player", "pct": 10.0, "rarity": "epic"},
		{"stat": "mana", "target": "player", "pct": 5.0, "rarity": "uncommon"}]
	var blessed := CombatUnit.make_party(bc, "priest", true, 0.25, CombatData.boon_mults(bc, "player"))
	check(is_equal_approx(blessed.res_max, roundf(plain.res_max * 1.15)), "Segen stapeln sich (+10 % und +5 % Mana)")
	# Hardcore: 5-Sekunden-Regel
	var hb := Battle.new()
	hb.hardcore = true
	var hp_ := CombatUnit.make_party(c, "priest", true, 0.25)
	hb.setup_party([hp_])
	hp_.res = 0.0
	hp_.last_mana_spend = 0.0
	hb.time = 0.0
	hb.step(1.0)
	var slow := hp_.res
	hp_.res = 0.0
	hb.time = 10.0
	hb.step(1.0)
	check(hp_.res > slow * 3.0, "Hardcore: volle Regeneration erst nach 5 Sekunden")
	hb.free()


# ---------------------------------------------------------------- Hauptbildschirm
func _open_game(c: Dictionary) -> Node:
	Router.params = {"id": c["id"]}
	t.get_tree().change_scene_to_file(Router.SCENES["game"])
	await t._wait(8)
	return t.get_tree().current_scene


func _close_popups(g: Node) -> void:
	# Segen-Wahl laesst sich nicht wegklicken: erste Karte waehlen (auch mehrere nacheinander)
	for round in 6:
		var any := false
		for ch in g.get_children():
			if ch is BoonDialog and not ch.is_queued_for_deletion():
				ch._pick(ch._offer[0])
				any = true
			elif ch is ModalDialog and not ch.is_queued_for_deletion():
				ch.close()
				any = true
		await t._wait(20)
		if not any:
			break


## Beendet die laufende Welle sofort (Sieg: alle Gegner sterben, Niederlage: die ganze Gruppe).
func _force_end(g: Node, victory: bool) -> void:
	var b: Battle = g.battle
	if victory:
		for e in b.enemies:
			b.deal_damage(b.party[1], e, 99999.0, "true", false, "test", false)
	else:
		for u in b.party:
			u.immortal = false
			b.deal_damage(b.enemies[0], u, 99999.0, "true", false, "test", false)
	b.step(0.01)
	await t._wait(3)


func game_flows() -> void:
	print("Hauptbildschirm")
	for ch in SaveGame.list():
		SaveGame.delete_character(ch["id"])
	var c := CharacterFactory.create_player({"name": "Heiler", "race": "dwarf"})
	SaveGame.add_character(c)
	var g = await _open_game(c)
	check(g.battle.party.size() == 2 and g.battle.enemies.size() == 1, "Welle 1: Spieler + Krieger gegen 1 Gegner")
	check(g._bar.spells[0] == "lesser_heal", "Aktionsleiste belegt")
	# Lehrmeister-Fenster und Zauberbuch
	g.toggle_trainer()
	await t._wait(3)
	check(g._window("trainer") != null, "Lehrmeister-Fenster oeffnet")
	g.toggle_spellbook()
	await t._wait(3)
	check(g._window("spellbook") != null and g._window("trainer") == null, "Zauberbuch ersetzt Lehrmeister-Fenster")
	# Drag & Drop: Zauber aus dem Buch auf Platz 6, dann Platz 1 auf Platz 6 ziehen (Tausch)
	var bar: ActionBar = g._bar
	var p6 := Vector2(5 * (bar.slot + bar.gap) + 5, 5)
	bar._drop_data(p6, {"spell": "smite"})
	check(g.c["action_bar"][5] == "smite" and g.c["action_bar"][1] == "", "Zauber auf Platz gezogen (alter Platz frei)")
	bar._drop_data(p6, {"spell": "lesser_heal", "from_slot": 0})
	check(g.c["action_bar"][5] == "lesser_heal" and g.c["action_bar"][0] == "smite", "Plaetze getauscht")
	g._windows[0].close()
	await t._wait(3)
	g._start_wave()
	check(g.phase == g.Phase.FIGHT and g.battle.state == Battle.State.FIGHT, "Welle gestartet")
	# Heilung und Schaden geben der ganzen Gruppe EP (Ueberheilung nicht)
	var w: CombatUnit = g.battle.party[1]
	var xp0 := int(g.c["xp"])
	var wxp0 := int(w.data["xp"])
	w.hp = 20.0
	for i in 5:
		g.battle.heal(g.player, w, 30.0, false, "lesser_heal")
	check(int(g.c["xp"]) > xp0 and int(w.data["xp"]) > wxp0, "Heilung gibt allen EP")
	var xp1 := int(g.c["xp"])
	for i in 5:
		g.battle.heal(g.player, w, 30.0, false, "lesser_heal")
	check(int(g.c["xp"]) == xp1, "Ueberheilung gibt keine EP")
	g.battle.deal_damage(w, g.battle.enemies[0], 60.0, "physical", false, "test", false)
	check(int(g.c["xp"]) > xp1, "Schaden des Kriegers gibt auch dem Spieler EP")
	await _force_end(g, true)
	var saved := SaveGame.get_character(c["id"])
	check(int(saved["highest_wave"]) == 1 and int(saved["wave"]) == 2, "Sieg gespeichert, naechste Welle")
	check(int(saved["xp"]) > 0 and int(saved["gold"]) > GameData.START_GOLD, "EP und Gold erhalten")
	check(g._popups > 0, "Quest-abgeschlossen-Fenster")
	await _close_popups(g)
	g._on_wave_clicked(1)
	check(g.wave_n == 1, "geschaffte Welle anklickbar")
	g._start_wave()
	await _force_end(g, true)
	check(not g.get_children().any(func(ch): return ch is ModalDialog and not ch is BoonDialog), "Wiederholung ohne Quest-Belohnung")
	await _close_popups(g)
	# Niederlage im Normal-Modus: eine Welle zurueck, Wiederbelebungsschwaeche
	g._load_wave(2)
	g._start_wave()
	await _force_end(g, false)
	saved = SaveGame.get_character(c["id"])
	check(int(saved["wave"]) == 1, "Niederlage: eine Welle zurueck")
	check(g.player.alive and g.player.weakened and g.player.has_aura("revive_weakness"), "Wiederbelebungsschwaeche nach dem Tod")
	await _close_popups(g)
	g._start_wave()
	await _force_end(g, true)
	check(not g.player.weakened, "Schwaeche gilt nur fuer die naechste Welle")
	await _close_popups(g)
	await _close_popups(g)
	# Trainingspuppe: niemand stirbt, Werte danach wie vorher
	var hp_before: float = g.player.hp
	g._start_training()
	check(g.phase == g.Phase.TRAINING and g.battle.enemies[0].type == "dummy", "Trainingspuppe steht bereit")
	for i in 200:
		g.battle.step(0.1)
	check(g.player.alive and g.player.hp < hp_before, "Uebungsschaden, aber niemand stirbt")
	g._end_training()
	check(is_equal_approx(g.player.hp, hp_before) and g.phase == g.Phase.READY, "nach der Uebung wiederhergestellt")
	# Hardcore: Mitglied stirbt -> permanent weg, Gratis-Krieger kommt
	var h := CharacterFactory.create_player({"name": "Hart", "mode": "hardcore"})
	SaveGame.add_character(h)
	var old_id: String = h["group"][0]["id"]
	g = await _open_game(h)
	g._start_wave()
	var b: Battle = g.battle
	b.deal_damage(b.enemies[0], b.party[1], 99999.0, "true", false, "test", false)
	b.deal_damage(b.party[0], b.enemies[0], 99999.0, "true", false, "test", false)
	b.step(0.01)
	await t._wait(3)
	saved = SaveGame.get_character(h["id"])
	check(saved["group"].size() == 1 and saved["group"][0]["id"] != old_id and int(saved["group"][0]["level"]) == 1,
		"Hardcore: gefallener Krieger ersetzt durch Gratis-Krieger")
	await _close_popups(g)
	# Hardcore: kein Auffuellen zwischen den Wellen (geschaffte Welle ohne Level-Up)
	g.c["xp"] = 0
	g._load_wave(1)
	g.player.res = g.player.res_max * 0.3
	g._start_wave()
	await _force_end(g, true)
	check(g.player.res_frac() < 0.95, "Hardcore: Mana wird nicht aufgefuellt")
	await _close_popups(g)
	# Level-Up fuellt HP und Mana auf, auch im Hardcore und mitten im Kampf
	g._start_wave()
	g.player.res = g.player.res_max * 0.2
	g.player.hp = g.player.max_hp * 0.5
	var lvl_before: int = g.player.level
	g._give_xp(g.player, CombatData.xp_to_next(lvl_before))
	check(g.player.level == lvl_before + 1 and g.player.hp_frac() > 0.99 and g.player.res_frac() > 0.99,
		"Level-Up sofort, HP und Mana voll (Hardcore, im Kampf)")
	check(g.c.get("boon_pending", []).size() >= 1 and not g._boon_open, "Segen-Wahl wartet bis nach der Welle")
	await _force_end(g, true)
	check(g._boon_open and g.c.get("boon_offer", []).size() == 3, "Segen-Wahl erscheint nach der Welle, Angebot gespeichert")
	var saved_offer: Array = SaveGame.get_character(g.c["id"])["boon_offer"]
	var pick: Dictionary = saved_offer[0]
	var boons_before: int = g.c.get("boons", []).size()
	var mana_before: float = g.player.res_max
	var hp_before2: float = g.player.max_hp
	g._apply_boon(pick)
	check(g.c["boons"].size() == boons_before + 1 and g.c["boon_offer"].is_empty(), "Segen gewaehlt und gespeichert")
	if pick["target"] == "player" and pick["stat"] in ["mana", "hp"]:
		check(g.player.res_max > mana_before or g.player.max_hp > hp_before2, "Segen wirkt sofort auf die Werte")
	await _close_popups(g)
	await _close_popups(g)
	# Hardcore: Niederlage -> Gefallen
	g._start_wave()
	await _force_end(g, false)
	check(bool(SaveGame.get_character(h["id"])["fallen"]), "Hardcore: Niederlage -> Charakter gefallen (sofort gespeichert)")
