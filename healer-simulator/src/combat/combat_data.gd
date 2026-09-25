class_name CombatData
extends RefCounted
## Balancing- und Weltdaten (data/balancing.json, data/world_<n>.json) und die Formeln,
## die sich daraus ableiten: Werte pro Level, Zauberraenge, EP-Kurve, Grau-Regel, Gold.

const STATS := ["hp", "hp_reg", "mana", "mana_reg", "armor", "resist", "damage", "heal_power", "crit", "haste"]

static var _bal: Dictionary = {}
static var _worlds: Dictionary = {}


static func bal() -> Dictionary:
	if _bal.is_empty():
		_bal = _load("res://data/balancing.json")
	return _bal


static func world(n: int) -> Dictionary:
	if not _worlds.has(n):
		_worlds[n] = _load("res://data/world_%d.json" % n)
	return _worlds[n]


static func _load(path: String) -> Dictionary:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_error("Daten fehlen: %s" % path)
		return {}
	var d = JSON.parse_string(f.get_as_text())
	return d if d is Dictionary else {}


static func g(key: String, default = 0.0):
	return bal()["general"].get(key, default)


static func has_world(n: int) -> bool:
	return FileAccess.file_exists("res://data/world_%d.json" % n)


static func wave_count(n: int) -> int:
	return world(n).get("waves", []).size()


static func wave(n: int, index: int) -> Dictionary:
	var waves: Array = world(n).get("waves", [])
	return waves[clampi(index - 1, 0, waves.size() - 1)]


static func is_boss_wave(n: int, index: int) -> bool:
	return bool(wave(n, index).get("boss", false))


# ---------------------------------------------------------------- Klassen
static func class_def(klass: String) -> Dictionary:
	return bal()["classes"].get(klass, bal()["classes"]["warrior"])


## Levelbasis aller Werte einer Klasse (GDD 8.2: Levelbasis; Items/Enchantments/Karten folgen spaeter).
static func class_stats(klass: String, level: int) -> Dictionary:
	var cd := class_def(klass)
	var out := {}
	for s in STATS:
		out[s] = float(cd["base"].get(s, 0.0)) + float(cd["per_level"].get(s, 0.0)) * (level - 1)
	out["hp"] = roundf(out["hp"])
	out["mana"] = roundf(out["mana"])
	return out


# ---------------------------------------------------------------- Segen (nach Level-Up)
const RARITY_COLORS := {
	"common": Color("b8b0c0"), "uncommon": Color("5ade5a"), "rare": Color("4a9aff"),
	"epic": Color("b060ff"), "legendary": Color("ff9a2a"), "mythic": Color("ff3a30"),
}


static func boon_cfg() -> Dictionary:
	return bal()["boons"]


## Wuerfelt ein Angebot aus 3 verschiedenen Segen (Werttyp + Ziel + Seltenheit).
static func roll_boon_offer(rng: RandomNumberGenerator) -> Array:
	var cfg := boon_cfg()
	var pool: Array = []
	for st in cfg["player"]:
		pool.append({"target": "player", "stat": st})
	var group_pool: Array = []
	for st in cfg["group"]:
		group_pool.append({"target": "group", "stat": st})
	var out: Array = []
	var guard := 0
	while out.size() < int(cfg["choices"]) and guard < 100:
		guard += 1
		var src: Array = group_pool if rng.randf() < float(cfg["group_weight"]) else pool
		var pick: Dictionary = src[rng.randi() % src.size()].duplicate()
		var dup := false
		for o in out:
			if o["stat"] == pick["stat"] and o["target"] == pick["target"]:
				dup = true
		if dup:
			continue
		var r := _roll_rarity(rng)
		pick["rarity"] = r["id"]
		pick["pct"] = snappedf(float(r["pct"]) * float(cfg[pick["target"]][pick["stat"]]), 0.1)
		out.append(pick)
	return out


static func _roll_rarity(rng: RandomNumberGenerator) -> Dictionary:
	var rs: Array = boon_cfg()["rarities"]
	var total := 0.0
	for r in rs:
		total += float(r["weight"])
	var roll := rng.randf() * total
	for r in rs:
		roll -= float(r["weight"])
		if roll <= 0.0:
			return r
	return rs[0]


## Summe der Segen-Prozente je Wert fuer "player" bzw. "group" (0.12 = +12 %).
static func boon_mults(c: Dictionary, target: String) -> Dictionary:
	var out := {}
	for b in c.get("boons", []):
		if b.get("target", "") == target:
			out[b["stat"]] = float(out.get(b["stat"], 0.0)) + float(b["pct"]) / 100.0
	return out


# ---------------------------------------------------------------- Zauber
static func spell(id: String) -> Dictionary:
	return bal()["spells"].get(id, {})


## Hoechster Rang eines Zaubers, der auf diesem Level bekannt ist (0 = unbekannt).
static func spell_rank(id: String, level: int) -> int:
	var rank := 0
	var ranks: Array = spell(id).get("ranks", [])
	for i in ranks.size():
		if level >= int(ranks[i]["level"]):
			rank = i + 1
	return rank


static func rank_data(id: String, rank: int) -> Dictionary:
	var ranks: Array = spell(id).get("ranks", [])
	if rank < 1 or ranks.is_empty():
		return {}
	return ranks[mini(rank, ranks.size()) - 1]


## Gelernter Rang eines Zaubers laut Speicherdaten (0 = nicht gelernt).
static func learned_rank(c: Dictionary, id: String) -> int:
	return int(c.get("spells", {}).get(id, 0))


## Startzauber eines neuen Charakters: alle Raenge mit Level 1 (GDD: Geringe Heilung R1, Heilige Pein R1).
static func start_spells() -> Dictionary:
	var out := {}
	for id in bal()["spell_order"]:
		if spell_rank(id, 1) > 0:
			out[id] = spell_rank(id, 1)
	return out


static func trainer_price(level: int) -> int:
	var t: Dictionary = bal()["trainer"]
	return maxi(int(t["min_price"]), int(t["price_per_level"]) * level)


## Alle Raenge aller Zauber fuer den Lehrmeister, sortiert nach benoetigtem Level.
## status: "learned" / "learnable" / "level" (Level zu niedrig) / "previous" (vorheriger Rang fehlt)
static func trainer_entries(c: Dictionary) -> Array:
	var out: Array = []
	var lvl := int(c.get("level", 1))
	for id in bal()["spell_order"]:
		var ranks: Array = spell(id).get("ranks", [])
		for i in ranks.size():
			var rank := i + 1
			var need := int(ranks[i]["level"])
			var status := "learnable"
			if learned_rank(c, id) >= rank:
				status = "learned"
			elif lvl < need:
				status = "level"
			elif learned_rank(c, id) < rank - 1:
				status = "previous"
			out.append({"id": id, "rank": rank, "level": need, "price": trainer_price(need), "status": status})
	out.sort_custom(func(a, b): return a["level"] < b["level"] or (a["level"] == b["level"] and a["rank"] < b["rank"]))
	return out


## Zauber, die auf diesem Level bekannt sind, in fester Reihenfolge.
static func known_spells(level: int) -> Array:
	var out: Array = []
	for id in bal()["spell_order"]:
		if spell_rank(id, level) > 0:
			out.append(id)
	return out


# ---------------------------------------------------------------- Gegner
static func enemy_def(world_n: int, id: String) -> Dictionary:
	return world(world_n)["enemies"].get(id, {})


static func level_factor(world_n: int, level: int) -> float:
	return 1.0 + float(world(world_n).get("level_scale", 0.25)) * (level - 1)


# ---------------------------------------------------------------- EP und Gold
static func xp_to_next(level: int) -> int:
	var x: Dictionary = bal()["xp"]
	var l := level - 1
	return int(x["base"] + x["linear"] * l + x["quad"] * l * l)


## Null-Differenz-Wert wie WoW (bestimmt, wie schnell EP bei niedrigeren Gegnern sinken).
static func zero_difference(level: int) -> int:
	if level < 8: return 5
	if level < 10: return 6
	if level < 12: return 7
	if level < 16: return 8
	if level < 20: return 9
	if level < 30: return 11
	if level < 40: return 12
	if level < 45: return 13
	if level < 50: return 14
	if level < 55: return 15
	return 16


## Hoechstes Gegnerlevel, das fuer diese Figur grau ist (0 = keins).
static func gray_level(level: int) -> int:
	if level <= 5:
		return 0
	if level <= 39:
		return level - int(level / 10.0) - 5
	return level - int(level / 5.0) - 1


## Farbe des Gegnerlevels aus Sicht einer Figur (grau, gruen, gelb, orange, rot).
static func level_color(own: int, mob: int) -> Color:
	var d := mob - own
	if d >= 5: return Color("ff3a30")
	if d >= 3: return Color("ff8a2a")
	if d >= -2: return Color("ffd84a")
	if mob > gray_level(own): return Color("5ade5a")
	return Color("9a9a9a")


## EP fuer einen getoeteten Gegner (Grau-Regel pro Figur).
static func mob_xp(own: int, mob: int, type: String) -> int:
	var x: Dictionary = bal()["xp"]
	if own >= int(g("max_level", 60)) or mob <= gray_level(own):
		return 0
	var base := float(x["mob_base"]) + float(x["mob_per_level"]) * mob
	var v := base
	if mob > own:
		v *= 1.0 + minf(float(x["higher_level_bonus"]) * (mob - own), float(x["higher_level_bonus_max"]))
	elif mob < own:
		v *= 1.0 - float(own - mob) / zero_difference(own)
	match type:
		"elite": v *= float(x["elite_mult"])
		"boss": v *= float(x["boss_mult"])
	return maxi(0, int(round(v)))


## EP fuer Heilung/Schaden (Gleitkomma, wird im Spiel aufsummiert). kind: "damage" oder "heal".
## Die Grau-Regel wirkt wie bei Gegnern: Stufenabstand zwischen Figur und Wellenlevel.
static func action_xp(points: float, kind: String, own: int, wave_level: int) -> float:
	var x: Dictionary = bal()["xp"]
	var same := float(mob_xp(wave_level, wave_level, "normal"))
	if points <= 0.0 or same <= 0.0:
		return 0.0
	var mult := float(mob_xp(own, wave_level, "normal")) / same
	return points * float(x.get("%s_per_point" % kind, 0.0)) * mult


static func quest_xp(wave_index: int, boss: bool) -> int:
	var x: Dictionary = bal()["xp"]
	return int(x["quest_base"] + x["quest_per_wave"] * wave_index + (x["quest_boss_bonus"] if boss else 0))


static func quest_gold(wave_index: int) -> int:
	var gd: Dictionary = bal()["gold"]
	return int(gd["quest_base"] + gd["quest_per_wave"] * wave_index)


static func mob_gold(level: int, type: String, rng: RandomNumberGenerator) -> int:
	var gd: Dictionary = bal()["gold"]
	var v := rng.randi_range(int(gd["mob_min_per_level"]) * level, int(gd["mob_max_per_level"]) * level)
	match type:
		"elite": v *= int(gd["elite_mult"])
		"boss": v *= int(gd["boss_mult"])
		"dummy": v = 0
	return v
