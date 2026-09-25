extends Node
## Balancing-Simulation (headless):  godot --headless --path . -- profile=sim test=combat
## Ein einfacher Bot-Heiler spielt alle Wellen von Welt 1 (Normal und Hardcore) und berichtet
## Dauer, Mana-Verbrauch, niedrigste Tank-HP, Tode und EP-Fortschritt.

const DT := 0.05


func _ready() -> void:
	await get_tree().process_frame
	for mode in ["normal", "hardcore"]:
		for skill in [1.0, 0.6]:
			_run(mode, skill)
	get_tree().quit(0)


func _run(mode: String, skill: float) -> void:
	print("\n=== %s, Bot-Qualitaet %.1f ===" % [mode, skill])
	var c := CharacterFactory.create_player({"name": "Sim", "mode": mode})
	var hardcore := mode == "hardcore"
	var wave := 1
	var tries := 0
	while wave <= CombatData.wave_count(1) and tries < 30:
		tries += 1
		# Der Bot kauft vor jeder Welle alle Raenge (Gold spielt in der Simulation keine Rolle)
		var spells := {}
		for id in CombatData.known_spells(int(c["level"])):
			spells[id] = CombatData.spell_rank(id, int(c["level"]))
		c["spells"] = spells
		var b := Battle.new()
		b.hardcore = hardcore
		b.rng.seed = 1000 + tries
		var units: Array = []
		var p := CombatUnit.make_party(c, "priest", true, 0.25)
		units.append(p)
		for i in c["group"].size():
			var m: Dictionary = c["group"][i]
			var u := CombatUnit.make_party(m, m["class"], false, 0.25)
			u.slot = 10 - i
			units.append(u)
		b.setup_party(units)
		var wd := CombatData.wave(1, wave)
		var foes: Array = []
		for id in wd["enemies"]:
			foes.append(CombatUnit.make_enemy(1, id, int(wd["level"]), hardcore))
		b.set_enemies(foes)
		var result := {"done": false, "win": false}
		b.finished.connect(func(v):
			result["done"] = true
			result["win"] = v)
		var xp := {}
		var wl := int(wd["level"])
		b.event.connect(func(e):
			var src = e.get("source")
			var kind := ""
			if e["type"] == "damage" and src and src.side == "party" and e["unit"].side == "enemy":
				kind = "damage"
			elif e["type"] == "heal" and src and src.side == "party":
				kind = "heal"
			if kind != "":
				for u in b.party:
					if u.alive:
						var lv := int(c["level"]) if u.is_player else int(u.data["level"])
						xp[u] = float(xp.get(u, 0.0)) + CombatData.action_xp(float(e["amount"]), kind, lv, wl)
			if e["type"] == "death" and e["unit"].side == "enemy":
				for u in b.party:
					if u.alive:
						var lvl := int(c["level"]) if u.is_player else int(u.data["level"])
						xp[u] = float(xp.get(u, 0.0)) + CombatData.mob_xp(lvl, e["unit"].level, e["unit"].type))
		b.start_fight()
		var t := 0.0
		var mana_start := p.res
		var min_tank := 1.0
		var tank: CombatUnit = units[1]
		var think := 0.0
		while not result["done"] and t < 300.0:
			b.step(DT)
			t += DT
			think -= DT
			if tank.alive:
				min_tank = minf(min_tank, tank.hp_frac())
			if think <= 0.0:
				think = 0.25 / skill
				_bot(b, p, tank, skill)
		var first := false
		if result["win"]:
			first = Progression.mark_wave_done(c, 1, wave)
		var qxp := CombatData.quest_xp(wave, CombatData.is_boss_wave(1, wave)) if first else 0
		var ups := Progression.add_xp(c, int(xp.get(p, 0)) + qxp)
		for u in units:
			if not u.is_player:
				Progression.add_xp(u.data, int(xp.get(u, 0)) + qxp)
		print("Welle %2d  %s  %5.1fs  Mana %4d/%4d  Tank min %3d%%  Spieler L%d (%d EP)  Krieger L%d  Tote: %s%s" % [
			wave, "SIEG" if result["win"] else "NIEDERLAGE", t, int(mana_start - p.res + 0), int(p.res_max), int(min_tank * 100),
			int(c["level"]), int(c["xp"]), int(c["group"][0]["level"]),
			", ".join(units.filter(func(u): return not u.alive).map(func(u): return u.klass)),
			"  LEVEL-UP " + str(ups) if not ups.is_empty() else ""])
		if hardcore:
			c["hp_frac"] = maxf(0.2, p.hp_frac())
			c["res_frac"] = p.res_frac()
			# Zwischen den Wellen regeneriert der Spieler Mana (hier: bis zur Mana-Schwelle 80 %)
			c["res_frac"] = maxf(c["res_frac"], 0.8)
			c["group"][0]["hp_frac"] = 1.0
		if result["win"]:
			wave += 1
		else:
			wave = maxi(1, wave - 1)


## Einfacher Heiler: Tank unter Schwelle -> Heilung, Erneuerung auf den Tank, sonst Pein bei viel Mana.
func _bot(b: Battle, p: CombatUnit, tank: CombatUnit, skill: float) -> void:
	if not p.alive or p.is_casting() or p.gcd > 0.0:
		return
	var low: CombatUnit = null
	for u in b.party:
		if u.alive and (low == null or u.hp_frac() < low.hp_frac()):
			low = u
	# Angekuendigter Tank-Buster: Tank vorher hochheilen
	if skill >= 1.0 and tank.alive and tank.hp_frac() < 0.95:
		for e in b.alive_enemies():
			if e.is_casting() and e.cast["ability"].get("mechanic", "") == "tank_buster":
				if b.player_cast("lesser_heal", tank) == "":
					return
	if low and low.hp_frac() < 0.35 and CombatData.spell_rank("flash_heal", p.level) > 0:
		if b.player_cast("flash_heal", low) == "":
			return
	if low and low.hp_frac() < 0.6 + 0.1 * skill:
		if b.player_cast("lesser_heal", low) == "":
			return
	if tank.alive and CombatData.spell_rank("renew", p.level) > 0 and not tank.has_aura("renew") and tank.hp_frac() < 0.9:
		if b.player_cast("renew", tank) == "":
			return
	if p.res_frac() > 0.5 and skill >= 1.0:
		var foes := b.alive_enemies()
		if not foes.is_empty():
			if CombatData.spell_rank("sw_pain", p.level) > 0 and not foes[0].has_aura("sw_pain"):
				if b.player_cast("sw_pain", foes[0]) == "":
					return
			b.player_cast("smite", foes[0])
