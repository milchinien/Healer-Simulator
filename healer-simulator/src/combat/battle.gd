class_name Battle
extends Node
## Echtzeit-Kampf (GDD Kapitel 14): Gruppe links, Gegner rechts, Bedrohung wie WoW,
## Zauber mit Castzeit/GCD, Gegnerfaehigkeiten mit Castbalken, Phasen, Krieger-KI.
##
## Zustaende: IDLE (zwischen den Wellen), FIGHT (Welle laeuft), TRAINING (Trainingspuppe).
## Alles, was die Anzeige wissen muss, wird ueber das Signal `event` gemeldet:
##   {"type": "damage", "unit", "source", "amount", "absorbed", "crit", "school", "ability"}
##   {"type": "heal", "unit", "source", "amount", "overheal", "crit", "spell"}
##   {"type": "cast_start" / "cast_stop" / "cast_done", "unit", "name", "time", "mechanic"}
##   {"type": "attack", "unit", "target"}          Nahkampfschlag (Animation)
##   {"type": "death", "unit"}  {"type": "aura", "unit"}  {"type": "phase", "unit", "phase"}
##   {"type": "error", "key"}   {"type": "taunt", "unit", "target"}  {"type": "ability", "unit", "name"}

signal event(e: Dictionary)
signal finished(victory: bool)

enum State { IDLE, FIGHT, TRAINING }

var state := State.IDLE
var party: Array = []          # CombatUnit, Reihenfolge = Aufstellung von hinten (Spieler) nach vorne (Tank)
var enemies: Array = []
var player: CombatUnit
var hardcore := false
var world_n := 1
var time := 0.0
var rng := RandomNumberGenerator.new()

var _queued := {}              # vorgemerkter Zauber des Spielers {"spell", "target"}
var _training_tick := 0.0


func _ready() -> void:
	rng.randomize()


func _process(delta: float) -> void:
	step(delta)


# ================================================================ Aufbau
func setup_party(units: Array) -> void:
	party = units
	player = null
	for u in party:
		if u.is_player:
			player = u


func set_enemies(units: Array) -> void:
	enemies = units
	for i in enemies.size():
		enemies[i].slot = i


func start_fight() -> void:
	state = State.FIGHT
	_begin_combat()


func start_training(dummy: CombatUnit) -> void:
	set_enemies([dummy])
	state = State.TRAINING
	_training_tick = float(CombatData.g("training_tick", 2.5))
	_begin_combat()


func _begin_combat() -> void:
	for e in enemies:
		e.threat = {}
		for u in party:
			if u.alive:
				# Der Tank zieht die Gegner zu Beginn auf sich
				e.threat[u] = 5.0 if u.is_tank() else 0.0
		e.aggro = null
		e.timers = {}
		for ab in e.data.get("abilities", []):
			var first := float(ab.get("first", ab.get("interval", 2.0) * rng.randf_range(0.3, 0.8)))
			e.timers[ab["id"]] = first
		e.phase = 0
		_pick_aggro(e)
	for u in party:
		u.swing = rng.randf_range(0.2, 0.8)
		u.target = null
		u.done_damage = 0.0
		u.done_healing = 0.0


## Beendet den Kampf sofort (Wechsel der Welle, Trainingsende, Verlassen).
func stop() -> void:
	state = State.IDLE
	for u in party + enemies:
		if u.is_casting():
			u.cast = {}
			event.emit({"type": "cast_stop", "unit": u})
	_queued = {}


func in_combat() -> bool:
	return state != State.IDLE


func alive_enemies() -> Array:
	return enemies.filter(func(e): return e.alive)


func alive_party() -> Array:
	return party.filter(func(u): return u.alive)


func tanks() -> Array:
	return party.filter(func(u): return u.alive and u.is_tank())


# ================================================================ Takt
func step(dt: float) -> void:
	if dt <= 0.0:
		return
	time += dt
	for u in party + enemies:
		_tick_timers(u, dt)
		_tick_auras(u, dt)
		_tick_regen(u, dt)
		if u.is_casting():
			_tick_cast(u, dt)
	if state == State.IDLE:
		_try_queued()
		return
	for u in party:
		if u.alive and not u.is_player:
			_member_ai(u, dt)
	for e in enemies:
		if e.alive:
			_enemy_ai(e, dt)
	if state == State.TRAINING:
		_training_damage(dt)
	_try_queued()
	_check_end()


func _tick_timers(u: CombatUnit, dt: float) -> void:
	u.gcd = maxf(0.0, u.gcd - dt)
	for k in u.cooldowns.keys():
		u.cooldowns[k] = maxf(0.0, u.cooldowns[k] - dt)


func _tick_regen(u: CombatUnit, dt: float) -> void:
	if not u.alive:
		return
	# HP-Regeneration (Wert "hp_reg", z. B. Priester-Grundwert und Segen)
	var hreg := u.stat("hp_reg")
	if hreg > 0.0 and u.hp < u.max_hp:
		u.hp = minf(u.max_hp, u.hp + hreg * dt)
	match u.resource:
		"mana":
			var reg := u.stat("mana_reg")
			if hardcore and time - u.last_mana_spend < float(CombatData.g("hardcore_five_second_rule", 5.0)):
				reg *= float(CombatData.g("hardcore_regen_in_5s", 0.2))
			u.res = minf(u.res_max, u.res + reg * dt)
		"rage":
			if state == State.IDLE:
				u.res = maxf(0.0, u.res - float(CombatData.class_def(u.klass).get("rage_decay_out_of_combat", 3.0)) * dt)
	# Hardcore: Gruppenmitglieder regenerieren ausserhalb des Kampfes langsam selbst
	if hardcore and state == State.IDLE and not u.is_player and u.side == "party":
		var pct := float(CombatData.g("hardcore_member_regen_pct", 0.015))
		u.hp = minf(u.max_hp, u.hp + u.max_hp * pct * dt)
		if u.resource == "mana":
			u.res = minf(u.res_max, u.res + u.res_max * pct * dt)


# ================================================================ Auren (HoT, DoT, Buffs)
## aura: {id, icon, kind ("buff"/"debuff"), duration, tick, per_tick, school, source, mods, dispel}
func apply_aura(u: CombatUnit, aura: Dictionary) -> void:
	var a := aura.duplicate()
	a["remaining"] = float(a.get("duration", 0.0))
	a["tick_left"] = float(a.get("tick", 0.0))
	for i in u.auras.size():
		if u.auras[i]["id"] == a["id"]:
			# gleiche Aura wird erneuert, nicht gestapelt
			u.auras[i] = a
			event.emit({"type": "aura", "unit": u})
			return
	u.auras.append(a)
	event.emit({"type": "aura", "unit": u})


func remove_aura(u: CombatUnit, aura_id: String) -> void:
	for i in u.auras.size():
		if u.auras[i]["id"] == aura_id:
			u.auras.remove_at(i)
			event.emit({"type": "aura", "unit": u})
			return


func _tick_auras(u: CombatUnit, dt: float) -> void:
	if u.auras.is_empty():
		return
	var changed := false
	for a in u.auras.duplicate():
		if a.get("permanent", false):
			continue
		a["remaining"] -= dt
		if float(a.get("tick", 0.0)) > 0.0:
			a["tick_left"] -= dt
			while a["tick_left"] <= 0.0 and a["remaining"] > -0.05:
				a["tick_left"] += float(a["tick"])
				_aura_tick(u, a)
				if not u.alive:
					return
		if a["remaining"] <= 0.0:
			u.auras.erase(a)
			changed = true
	if changed:
		event.emit({"type": "aura", "unit": u})


func _aura_tick(u: CombatUnit, a: Dictionary) -> void:
	var src: CombatUnit = a.get("source")
	if a["kind"] == "buff" and float(a.get("per_tick", 0.0)) > 0.0:
		heal(src, u, float(a["per_tick"]), false, str(a["id"]))
	elif a["kind"] == "debuff" and float(a.get("per_tick", 0.0)) > 0.0:
		deal_damage(src, u, float(a["per_tick"]), str(a.get("school", "magic")), false, str(a["id"]), false)


# ================================================================ Schaden und Heilung
func reduction(target: CombatUnit, school: String, attacker_level: int) -> float:
	if school == "true":
		return 0.0
	var v := target.stat("armor") if school == "physical" else target.stat("resist")
	var k := float(CombatData.g("armor_k_base", 80)) + float(CombatData.g("armor_k_per_level", 20)) * attacker_level
	return minf(float(CombatData.g("reduction_cap", 0.75)), v / (v + k))


## Fuegt Schaden zu (nach Ruestung/Resistenz, Schild, Schadensreduktion). Gibt den erlittenen Schaden zurueck.
func deal_damage(src: CombatUnit, target: CombatUnit, raw: float, school: String, crit: bool, ability: String, reduce := true) -> float:
	if not target.alive:
		return 0.0
	var lvl := src.level if src else target.level
	var amount := raw
	if reduce:
		amount *= 1.0 - reduction(target, "physical" if school == "physical" else "magic", lvl)
	amount *= target.aura_mult("damage_taken")
	amount = maxf(1.0, roundf(amount))
	# Schilde absorbieren jeden Schaden
	var absorbed := 0.0
	for a in target.auras.duplicate():
		if float(a.get("absorb", 0.0)) > 0.0 and amount > 0.0:
			var take := minf(amount, float(a["absorb"]))
			a["absorb"] -= take
			amount -= take
			absorbed += take
			if a["absorb"] <= 0.0:
				target.auras.erase(a)
				event.emit({"type": "aura", "unit": target})
	var before := target.hp
	target.hp -= amount
	if target.immortal:
		target.hp = maxf(1.0, target.hp)
		if target.side == "enemy":
			target.hp = target.max_hp
	var taken := before - maxf(0.0, target.hp)
	if src:
		src.done_damage += amount
	event.emit({"type": "damage", "unit": target, "source": src, "amount": amount, "absorbed": absorbed,
		"crit": crit, "school": school, "ability": ability})
	# Bedrohung beim getroffenen Gegner, Wut beim Krieger
	if src and src.side == "party" and target.side == "enemy":
		add_threat(target, src, (amount + absorbed) * _threat_mult(src))
		if src.resource == "rage":
			_gain_rage(src, (amount + absorbed) * float(CombatData.class_def(src.klass).get("rage_per_damage_dealt", 0.9)))
	if target.resource == "rage" and target.alive:
		_gain_rage(target, (amount + absorbed) * float(CombatData.class_def(target.klass).get("rage_per_damage_taken", 0.45)))
	if target.hp <= 0.0 and not target.immortal:
		_die(target)
	return taken


func _gain_rage(u: CombatUnit, raw: float) -> void:
	# Umrechnung wie WoW: auf hoeherem Level gibt derselbe Schaden weniger Wut
	var conv := 12.0 / (12.0 + 4.0 * (u.level - 1))
	u.res = minf(u.res_max, u.res + raw * conv)


func heal(src: CombatUnit, target: CombatUnit, raw: float, crit: bool, spell_id: String) -> float:
	if not target.alive:
		return 0.0
	var amount := roundf(raw)
	var missing := target.max_hp - target.hp
	var effective := minf(amount, missing)
	target.hp += effective
	if src:
		src.done_healing += effective
	event.emit({"type": "heal", "unit": target, "source": src, "amount": effective, "overheal": amount - effective,
		"crit": crit, "spell": spell_id})
	# Heilung erzeugt Bedrohung bei allen Gegnern im Kampf (aufgeteilt)
	if src and state == State.FIGHT and effective > 0.0:
		var foes := alive_enemies()
		if foes.size() > 0:
			var per := effective * float(CombatData.g("heal_threat", 0.5)) * _threat_mult(src) / foes.size()
			for e in foes:
				add_threat(e, src, per)
	return effective


func _threat_mult(u: CombatUnit) -> float:
	return float(CombatData.g("tank_threat_multiplier", 1.5)) if u.is_tank() else 1.0


func add_threat(enemy: CombatUnit, u: CombatUnit, amount: float) -> void:
	if not enemy.alive or not u.alive or enemy.type == "dummy":
		return
	enemy.threat[u] = enemy.threat_of(u) + amount


func _roll_crit(u: CombatUnit) -> bool:
	return rng.randf() * 100.0 < u.stat("crit")


func _die(u: CombatUnit) -> void:
	u.hp = 0.0
	u.alive = false
	u.auras.clear()
	if u.is_casting():
		u.cast = {}
		event.emit({"type": "cast_stop", "unit": u})
	if u.side == "party":
		for e in enemies:
			e.threat.erase(u)
			if e.aggro == u:
				e.aggro = null
				_pick_aggro(e)
		if u == player:
			_queued = {}
	event.emit({"type": "death", "unit": u})


# ================================================================ Zauber des Spielers
func spell_mana(spell_id: String, u: CombatUnit) -> int:
	return int(CombatData.rank_data(spell_id, u.known_rank(spell_id)).get("mana", 0))


func cast_time(u: CombatUnit, spell_id: String) -> float:
	return float(CombatData.spell(spell_id).get("cast", 0.0)) / (1.0 + u.stat("haste") / 100.0)


func gcd_time(u: CombatUnit) -> float:
	return maxf(float(CombatData.g("gcd_min", 1.0)), float(CombatData.g("gcd", 1.5)) / (1.0 + u.stat("haste") / 100.0))


## Prueft, ob ein Ziel fuer den Zauber gueltig ist. Gibt "" oder einen Fehlerschluessel zurueck.
func check_target(spell_id: String, t: CombatUnit) -> String:
	var sp := CombatData.spell(spell_id)
	if t == null:
		return "ERR_NO_TARGET"
	if sp.get("target", "") == "enemy":
		if t.side != "enemy" or state == State.IDLE:
			return "ERR_NO_TARGET"
		if not t.alive:
			return "ERR_TARGET_DEAD"
	else:
		if t.side != "party":
			return "ERR_WRONG_TARGET"
		if not t.alive:
			return "ERR_TARGET_DEAD"
	return ""


## Der Spieler wirkt einen Zauber. Gibt "" zurueck oder einen Fehlerschluessel (Anzeige in Rot).
func player_cast(spell_id: String, t: CombatUnit) -> String:
	if player == null or not player.alive:
		return "ERR_DEAD"
	var rank := player.known_rank(spell_id)
	if rank == 0:
		return "ERR_UNKNOWN_SPELL"
	var err := check_target(spell_id, t)
	if err != "":
		return err
	var window := float(CombatData.g("spell_queue_window", 0.35))
	var busy := maxf(player.gcd, float(player.cast.get("left", 0.0)))
	if player.is_casting() or player.gcd > 0.0:
		if busy <= window:
			_queued = {"spell": spell_id, "target": t}
			return ""
		return "ERR_BUSY" if player.is_casting() else "ERR_NOT_READY"
	if float(player.cooldowns.get(spell_id, 0.0)) > 0.0:
		return "ERR_NOT_READY"
	if player.res < spell_mana(spell_id, player):
		return "ERR_NO_MANA"
	var ct := cast_time(player, spell_id)
	player.gcd = gcd_time(player)
	if ct <= 0.0:
		_finish_spell(player, spell_id, rank, t)
	else:
		player.cast = {"spell": spell_id, "rank": rank, "target": t, "total": ct, "left": ct,
			"name": "SPELL_%s" % spell_id.to_upper()}
		event.emit({"type": "cast_start", "unit": player, "name": player.cast["name"], "time": ct, "spell": spell_id, "target": t})
	return ""


func cancel_player_cast() -> bool:
	_queued = {}
	if player and player.is_casting():
		player.cast = {}
		player.gcd = 0.0
		event.emit({"type": "cast_stop", "unit": player, "cancelled": true})
		return true
	return false


func _try_queued() -> void:
	if _queued.is_empty() or player == null:
		return
	if player.is_casting() or player.gcd > 0.0:
		return
	var q := _queued
	_queued = {}
	var err := player_cast(q["spell"], q["target"])
	if err != "":
		event.emit({"type": "error", "key": err})


func _tick_cast(u: CombatUnit, dt: float) -> void:
	u.cast["left"] -= dt
	if u.cast["left"] > 0.0:
		return
	var c := u.cast
	u.cast = {}
	if u.side == "party":
		var t: CombatUnit = c["target"]
		if check_target(c["spell"], t) != "":
			event.emit({"type": "cast_stop", "unit": u})
			event.emit({"type": "error", "key": "ERR_TARGET_DEAD"})
			return
		if u.res < spell_mana(c["spell"], u):
			event.emit({"type": "cast_stop", "unit": u})
			event.emit({"type": "error", "key": "ERR_NO_MANA"})
			return
		event.emit({"type": "cast_done", "unit": u, "spell": c["spell"]})
		_finish_spell(u, c["spell"], int(c["rank"]), t)
	else:
		event.emit({"type": "cast_done", "unit": u, "ability": c["ability"]["id"]})
		_enemy_ability_hit(u, c["ability"], c.get("target"))


func _finish_spell(u: CombatUnit, spell_id: String, rank: int, t: CombatUnit) -> void:
	var sp := CombatData.spell(spell_id)
	var rd := CombatData.rank_data(spell_id, rank)
	var cost := float(rd.get("mana", 0))
	u.res -= cost
	if cost > 0.0:
		u.last_mana_spend = time
	if float(sp.get("cd", 0.0)) > 0.0:
		u.cooldowns[spell_id] = float(sp["cd"])
	event.emit({"type": "spell", "unit": u, "target": t, "spell": spell_id, "school": sp.get("school", "holy")})
	var coef := float(sp.get("coef", 0.0))
	match str(sp.get("kind", "")):
		"heal":
			var v := rng.randf_range(float(rd["min"]), float(rd["max"])) + u.stat("heal_power") * coef
			var crit := _roll_crit(u)
			heal(u, t, v * (float(CombatData.g("crit_multiplier", 2.0)) if crit else 1.0), crit, spell_id)
		"damage":
			var v := rng.randf_range(float(rd["min"]), float(rd["max"])) + u.stat("damage") * coef
			var crit := _roll_crit(u)
			deal_damage(u, t, v * (float(CombatData.g("crit_multiplier", 2.0)) if crit else 1.0), "magic", crit, spell_id)
		"hot", "dot":
			var dur := float(sp["duration"])
			var tick := float(sp["tick"]) / (1.0 + u.stat("haste") / 100.0)
			var ticks := maxf(1.0, floorf(dur / tick + 0.001))
			var power := u.stat("heal_power") if sp["kind"] == "hot" else u.stat("damage")
			var per := (float(rd["total"]) + power * coef) / ticks
			apply_aura(t, {"id": sp["aura"], "icon": "aura_%s" % sp["aura"], "kind": "buff" if sp["kind"] == "hot" else "debuff",
				"duration": dur, "tick": tick, "per_tick": per, "school": sp.get("school", "holy"), "source": u,
				"name": "SPELL_%s" % spell_id.to_upper()})
			if sp["kind"] == "hot" and state == State.FIGHT:
				# Das Aufbringen eines HoT erzeugt eine kleine Menge Bedrohung
				for e in alive_enemies():
					add_threat(e, u, 1.0)
			elif sp["kind"] == "dot":
				add_threat(t, u, 2.0)


# ================================================================ Gegner
func _enemy_ai(e: CombatUnit, dt: float) -> void:
	if e.type == "dummy":
		return
	_check_phase(e)
	_pick_aggro(e)
	if e.is_casting():
		return
	for ab in e.data.get("abilities", []):
		if int(ab.get("phase", 0)) > e.phase:
			continue
		var id: String = ab["id"]
		e.timers[id] = float(e.timers.get(id, 0.0)) - dt
		if e.timers[id] > 0.0:
			continue
		if ab["kind"] == "melee":
			if e.aggro == null:
				continue
			e.timers[id] = float(ab.get("interval", 2.0))
			event.emit({"type": "attack", "unit": e, "target": e.aggro})
			_enemy_ability_hit(e, ab, e.aggro)
		elif ab["kind"] == "cast":
			var t: CombatUnit = e.aggro if ab.get("target", "aggro") == "aggro" else null
			if ab.get("target", "aggro") == "aggro" and t == null:
				continue
			e.timers[id] = float(ab.get("cd", ab.get("interval", 3.0)))
			e.cast = {"ability": ab, "target": t, "total": float(ab["cast"]), "left": float(ab["cast"]),
				"name": "ABILITY_%s" % id.to_upper()}
			event.emit({"type": "cast_start", "unit": e, "name": e.cast["name"], "time": float(ab["cast"]),
				"mechanic": ab.get("mechanic", ""), "anim": ab.get("anim", "cast"), "target": t})
			return


func _check_phase(e: CombatUnit) -> void:
	var phases: Array = e.data.get("phases", [])
	while e.phase < phases.size() and e.hp_frac() <= float(phases[e.phase]):
		e.phase += 1
		# Faehigkeiten der neuen Phase starten mit ihrer eigenen Vorlaufzeit
		for ab in e.data.get("abilities", []):
			if int(ab.get("phase", 0)) == e.phase:
				e.timers[ab["id"]] = float(ab.get("first", 3.0))
		event.emit({"type": "phase", "unit": e, "phase": e.phase})


func _enemy_ability_hit(e: CombatUnit, ab: Dictionary, t: CombatUnit) -> void:
	if not e.alive:
		return
	var f := CombatData.level_factor(world_n, e.level)
	if hardcore:
		f *= float(CombatData.g("hardcore_enemy_damage", 1.2))
	var school: String = ab.get("school", "physical")
	var targets: Array = []
	if ab.get("target", "aggro") == "all":
		targets = alive_party()
	elif t and t.alive:
		targets = [t]
	elif e.aggro:
		targets = [e.aggro]
	for u in targets:
		var raw := rng.randf_range(float(ab["min"]), float(ab["max"])) * f
		deal_damage(e, u, raw, school, false, str(ab["id"]))


## Waehlt das Angriffsziel nach der Bedrohungsliste (Wechsel erst bei 110 % Nahkampf / 130 % Fernkampf).
func _pick_aggro(e: CombatUnit) -> void:
	if e.type == "dummy":
		e.aggro = null
		return
	var best: CombatUnit = null
	var best_v := -1.0
	for u in party:
		if not u.alive:
			continue
		var v := e.threat_of(u)
		if v > best_v:
			best_v = v
			best = u
	if best == null:
		e.aggro = null
		return
	if e.aggro == null or not e.aggro.alive:
		if best_v <= 0.0:
			# Niemand hat Bedrohung: vorderste Figur (Tank) wird angegriffen
			var front: Array = alive_party()
			front.sort_custom(func(a, b): return a.slot > b.slot)
			best = front[0]
		e.aggro = best
		return
	if e.is_casting() or best == e.aggro:
		return
	var need := float(CombatData.g("aggro_ranged", 1.3)) if best.ranged else float(CombatData.g("aggro_melee", 1.1))
	if best_v > e.threat_of(e.aggro) * need:
		e.aggro = best


# ================================================================ Gruppen-KI (Krieger)
func _member_ai(u: CombatUnit, dt: float) -> void:
	if u.is_casting():
		return
	_choose_target(u)
	if u.target == null:
		return
	match u.klass:
		"warrior":
			_warrior_ai(u)
	# Standardangriff
	var cd := CombatData.class_def(u.klass)
	u.swing -= dt
	if u.swing <= 0.0:
		u.swing = float(cd.get("swing", 2.4)) / (1.0 + u.stat("haste") / 100.0)
		var w: Array = cd.get("weapon", [4, 8])
		var raw := rng.randf_range(float(w[0]), float(w[1])) + u.stat("damage")
		var crit := _roll_crit(u)
		event.emit({"type": "attack", "unit": u, "target": u.target})
		deal_damage(u, u.target, raw * (float(CombatData.g("crit_multiplier", 2.0)) if crit else 1.0), "physical", crit, "auto_attack")


func _choose_target(u: CombatUnit) -> void:
	var foes := alive_enemies()
	if foes.is_empty():
		u.target = null
		return
	if u.target and u.target.alive:
		return
	if not u.is_tank():
		# DPS greifen das Ziel des Tanks an
		for t in tanks():
			if t.target and t.target.alive:
				u.target = t.target
				return
	# Schwaechere Gegner zuerst, damit weniger Schaden auf die Gruppe einprasselt
	foes.sort_custom(func(a, b): return a.max_hp < b.max_hp)
	u.target = foes[0]


func _warrior_ai(u: CombatUnit) -> void:
	if u.gcd > 0.0:
		return
	var abil: Dictionary = CombatData.class_def("warrior")["abilities"]
	var foes := alive_enemies()
	# Schildwall bei niedrigen HP
	var sw: Dictionary = abil["shield_wall"]
	if u.hp_frac() < float(sw["hp_below"]) and _ready_ability(u, "shield_wall"):
		u.cooldowns["shield_wall"] = float(sw["cd"])
		apply_aura(u, {"id": "shield_wall", "icon": "aura_shield_wall", "kind": "buff", "duration": float(sw["duration"]),
			"mods": {"damage_taken": 1.0 - float(sw["reduction"])}, "source": u, "name": "ABILITY_SHIELD_WALL"})
		event.emit({"type": "ability", "unit": u, "name": "ABILITY_SHIELD_WALL"})
		return
	# Spott, wenn ein Gegner jemand anderen angreift
	if _ready_ability(u, "taunt"):
		for e in foes:
			if e.aggro and e.aggro != u and not e.aggro.is_tank():
				var top := 0.0
				for k in e.threat:
					top = maxf(top, float(e.threat[k]))
				e.threat[u] = top * 1.1 + 10.0
				e.aggro = u
				u.cooldowns["taunt"] = float(abil["taunt"]["cd"])
				u.gcd = gcd_time(u)
				u.target = e
				event.emit({"type": "taunt", "unit": u, "target": e})
				event.emit({"type": "ability", "unit": u, "name": "ABILITY_TAUNT"})
				return
	# Donnerknall bei mehreren Gegnern
	var tc: Dictionary = abil["thunder_clap"]
	if foes.size() >= int(tc["min_targets"]) and u.res >= float(tc["rage"]) and _ready_ability(u, "thunder_clap"):
		u.res -= float(tc["rage"])
		u.cooldowns["thunder_clap"] = float(tc["cd"])
		u.gcd = gcd_time(u)
		event.emit({"type": "ability", "unit": u, "name": "ABILITY_THUNDER_CLAP", "aoe": true})
		var dmg := float(tc["damage"]) + float(tc["damage_per_level"]) * (u.level - 1)
		for e in foes:
			var dealt := deal_damage(u, e, dmg * rng.randf_range(0.9, 1.1), "physical", false, "thunder_clap")
			add_threat(e, u, dealt * (float(tc["threat_mult"]) - 1.0) * _threat_mult(u))
		return
	# Heldenhafter Stoss
	var hs: Dictionary = abil["heroic_strike"]
	if u.res >= float(hs["rage"]) and u.target:
		u.res -= float(hs["rage"])
		u.gcd = gcd_time(u)
		var w: Array = CombatData.class_def("warrior").get("weapon", [4, 8])
		var raw := rng.randf_range(float(w[0]), float(w[1])) + u.stat("damage") + float(hs["bonus"]) + float(hs["bonus_per_level"]) * (u.level - 1)
		var crit := _roll_crit(u)
		event.emit({"type": "attack", "unit": u, "target": u.target, "strong": true})
		event.emit({"type": "ability", "unit": u, "name": "ABILITY_HEROIC_STRIKE"})
		var t := u.target
		deal_damage(u, t, raw * (float(CombatData.g("crit_multiplier", 2.0)) if crit else 1.0), "physical", crit, "heroic_strike")
		add_threat(t, u, float(hs["threat_bonus"]) * _threat_mult(u))


func _ready_ability(u: CombatUnit, id: String) -> bool:
	return float(u.cooldowns.get(id, 0.0)) <= 0.0


# ================================================================ Trainingspuppe
func _training_damage(dt: float) -> void:
	_training_tick -= dt
	if _training_tick > 0.0:
		return
	_training_tick = float(CombatData.g("training_tick", 2.5))
	var dummy: CombatUnit = enemies[0] if enemies.size() > 0 else null
	var i := 0
	for u in party:
		if not u.alive:
			continue
		var school := "physical" if (i + int(time)) % 2 == 0 else "magic"
		deal_damage(dummy, u, u.max_hp * float(CombatData.g("training_damage_pct", 0.06)), school, false, "training", false)
		i += 1


# ================================================================ Ende
func _check_end() -> void:
	if state != State.FIGHT:
		return
	if alive_enemies().is_empty():
		state = State.IDLE
		_end_casts()
		finished.emit(true)
	elif alive_party().is_empty():
		state = State.IDLE
		_end_casts()
		finished.emit(false)


func _end_casts() -> void:
	for u in party + enemies:
		if u.is_casting():
			u.cast = {}
			event.emit({"type": "cast_stop", "unit": u})
		# Debuffs der Gegner verschwinden mit ihnen, eigene Buffs (z. B. Erneuerung) laufen weiter
		u.auras = u.auras.filter(func(a): return a.get("permanent", false) or (u.side == "party" and a["kind"] == "buff"))
		event.emit({"type": "aura", "unit": u})
	_queued = {}
