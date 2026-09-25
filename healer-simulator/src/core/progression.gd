class_name Progression
extends RefCounted
## Fortschritt eines Charakters (Speicherdaten): EP und Level fuer Spieler und Mitglieder,
## Zauber und Aktionsleiste, Wellenfortschritt, Normal-/Hardcore-Regeln nach einer Welle.

const BAR_SIZE := 12


## Fuegt EP hinzu und gibt die neu erreichten Level zurueck (leer = kein Level-Up).
static func add_xp(entity: Dictionary, amount: int) -> Array:
	var ups: Array = []
	var max_level := int(CombatData.g("max_level", 60))
	if amount <= 0 or int(entity.get("level", 1)) >= max_level:
		return ups
	entity["xp"] = int(entity.get("xp", 0)) + amount
	while int(entity["level"]) < max_level and int(entity["xp"]) >= CombatData.xp_to_next(int(entity["level"])):
		entity["xp"] = int(entity["xp"]) - CombatData.xp_to_next(int(entity["level"]))
		entity["level"] = int(entity["level"]) + 1
		ups.append(int(entity["level"]))
	if int(entity["level"]) >= max_level:
		entity["xp"] = 0
	return ups


## Zauber und Aktionsleiste sicherstellen (auch fuer aeltere Spielstaende):
## - neue Charaktere kennen die Startzauber (Level-1-Raenge),
## - Spielstaende aus der Zeit vor dem Lehrmeister behalten alle Raenge, die sie bis dahin automatisch hatten.
static func ensure_spells(c: Dictionary) -> void:
	if not c.has("spells"):
		if c.has("action_bar"):
			var known := {}
			for id in CombatData.known_spells(int(c.get("level", 1))):
				known[id] = CombatData.spell_rank(id, int(c.get("level", 1)))
			c["spells"] = known
		else:
			c["spells"] = CombatData.start_spells()
	var bar: Array = c.get("action_bar", [])
	var fresh := bar.is_empty()
	while bar.size() < BAR_SIZE:
		bar.append("")
	c["action_bar"] = bar
	if fresh:
		for id in CombatData.bal()["spell_order"]:
			if CombatData.learned_rank(c, id) > 0:
				place_on_bar(c, id)


## Legt einen Zauber auf den ersten freien Platz der Aktionsleiste (falls noch nicht drauf).
## Neue Raenge brauchen das nicht: der Platz speichert nur die Zauber-ID, es gilt immer der hoechste Rang.
static func place_on_bar(c: Dictionary, id: String) -> bool:
	var bar: Array = c["action_bar"]
	if id in bar:
		return false
	var free := bar.find("")
	if free == -1:
		return false
	bar[free] = id
	return true


## Lehrmeister: einen Rang lernen. Gibt "" zurueck oder einen Fehlerschluessel.
static func learn(c: Dictionary, id: String, rank: int) -> String:
	for e in CombatData.trainer_entries(c):
		if e["id"] == id and e["rank"] == rank:
			match e["status"]:
				"learned":
					return "TRAINER_ERR_KNOWN"
				"level":
					return "TRAINER_ERR_LEVEL"
				"previous":
					return "TRAINER_ERR_PREVIOUS"
			if int(c.get("gold", 0)) < int(e["price"]):
				return "TRAINER_ERR_GOLD"
			c["gold"] = int(c["gold"]) - int(e["price"])
			var spells: Dictionary = c["spells"]
			spells[id] = rank
			if rank == 1:
				# Neu gelernte Zauber kommen auf einen freien Platz (ziehen geht jederzeit ueber das Zauberbuch)
				place_on_bar(c, id)
			return ""
	return "TRAINER_ERR_KNOWN"


## Anzahl und Gesamtpreis aller jetzt lernbaren Raenge (in Reihenfolge lernbar).
static func learnable_summary(c: Dictionary) -> Dictionary:
	var count := 0
	var price := 0
	var sim := {"level": c.get("level", 1), "spells": c.get("spells", {}).duplicate()}
	var progressed := true
	while progressed:
		progressed = false
		for e in CombatData.trainer_entries(sim):
			if e["status"] == "learnable":
				sim["spells"][e["id"]] = e["rank"]
				count += 1
				price += int(e["price"])
				progressed = true
	return {"count": count, "price": price}


## Welle als geschafft markieren. Gibt true zurueck, wenn es der erste Abschluss war (Quest).
static func mark_wave_done(c: Dictionary, world_n: int, wave_n: int) -> bool:
	var first := false
	if world_n > int(c.get("highest_world", 1)):
		c["highest_world"] = world_n
		c["highest_wave"] = 0
	if world_n == int(c.get("highest_world", 1)) and wave_n > int(c.get("highest_wave", 0)):
		c["highest_wave"] = wave_n
		first = true
	return first


## Hoechste freigeschaltete Welle der Welt (Welle n+1 erst nach Sieg in Welle n).
static func unlocked_wave(c: Dictionary, world_n: int) -> int:
	var count := CombatData.wave_count(world_n)
	if world_n < int(c.get("highest_world", 1)):
		return count
	return mini(count, int(c.get("highest_wave", 0)) + 1)


static func wave_done(c: Dictionary, world_n: int, wave_n: int) -> bool:
	if world_n < int(c.get("highest_world", 1)):
		return true
	return world_n == int(c.get("highest_world", 1)) and wave_n <= int(c.get("highest_wave", 0))


## Freier Krieger, wenn die Gruppe (ohne Spieler) leer ist (GDD Kapitel 6).
static func ensure_group(c: Dictionary) -> bool:
	if c.get("group", []).is_empty():
		var rng := RandomNumberGenerator.new()
		rng.randomize()
		c["group"] = [CharacterFactory.create_member("warrior", 1, rng)]
		return true
	return false
