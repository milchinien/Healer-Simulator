class_name CombatUnit
extends RefCounted
## Eine Figur im Kampf: Spieler, Gruppenmitglied oder Gegner.
## Haelt Lebenspunkte, Ressource, Werte, Auren (Buffs/Debuffs), Bedrohungsliste (Gegner),
## laufenden Zauber und Abklingzeiten. Die Regeln selbst stehen in Battle.

var id := ""
var name := ""
var side := "party"            # "party" oder "enemy"
var klass := ""                # Klasse (priest, warrior) bzw. Gegner-ID (wolf_young ...)
var role := ""                 # tank / dps / heal / enemy
var type := "normal"           # Gegner: normal / elite / boss / dummy
var level := 1
var ranged := false
var is_player := false
var slot := 0                  # Position in der Aufstellung

var stats := {}                # Endwerte (inkl. Segen und Wiederbelebungsschwaeche)
var mults := {}                # Segen: Wert -> Zuschlag (0.12 = +12 %), letzter Multiplikator
var hp := 1.0
var max_hp := 1.0
var resource := "none"         # mana / rage / none
var res := 0.0
var res_max := 0.0
var alive := true
var weakened := false          # Wiederbelebungsschwaeche (naechste Welle)

var auras: Array = []          # Dictionaries, siehe Battle.apply_aura
var threat := {}               # nur Gegner: CombatUnit -> Bedrohung
var aggro: CombatUnit = null   # nur Gegner: aktuelles Angriffsziel
var target: CombatUnit = null  # Mitglieder: aktuelles Angriffsziel
var cast := {}                 # laufender Zauber / angekuendigte Faehigkeit
var cooldowns := {}            # Faehigkeit -> verbleibende Sekunden
var timers := {}               # Gegner: Faehigkeit -> Sekunden bis zur naechsten Nutzung
var gcd := 0.0
var swing := 0.0
var phase := 0
var immortal := false          # Trainingsmodus: faellt nie unter 1 HP
var last_mana_spend := -99.0
var data := {}                 # Gegner-Definition bzw. Speicherdaten des Mitglieds

## Statistik der laufenden Welle (fuer Anzeigen / spaeteres Meter)
var done_damage := 0.0
var done_healing := 0.0


static func make_party(c: Dictionary, klass_id: String, player: bool, weak_mult: float, boon_mults: Dictionary = {}) -> CombatUnit:
	var u := CombatUnit.new()
	u.id = str(c.get("id", ""))
	u.name = str(c.get("name", "?"))
	u.side = "party"
	u.klass = klass_id
	u.is_player = player
	u.level = int(c.get("level", 1))
	var cd := CombatData.class_def(klass_id)
	u.role = str(cd.get("role", "dps"))
	u.ranged = bool(cd.get("ranged", false))
	u.resource = str(cd.get("resource", "mana"))
	u.weakened = bool(c.get("weakened", false))
	u.data = c
	u.mults = boon_mults
	u.stats = u._final_stats(weak_mult)
	u.max_hp = maxf(1.0, roundf(u.stats["hp"]))
	u.hp = u.max_hp * clampf(float(c.get("hp_frac", 1.0)), 0.0, 1.0)
	match u.resource:
		"mana":
			u.res_max = roundf(u.stats["mana"])
			u.res = u.res_max * clampf(float(c.get("res_frac", 1.0)), 0.0, 1.0)
		"rage":
			u.res_max = float(cd.get("rage_max", 100))
			u.res = 0.0
	if u.hp <= 0.0:
		u.hp = 0.0
		u.alive = false
	return u


static func make_enemy(world_n: int, enemy_id: String, level: int, hardcore: bool) -> CombatUnit:
	var def := CombatData.enemy_def(world_n, enemy_id)
	var u := CombatUnit.new()
	u.id = "%s_%d" % [enemy_id, randi() % 100000]
	u.klass = enemy_id
	u.name = "ENEMY_%s" % enemy_id.to_upper()
	u.side = "enemy"
	u.role = "enemy"
	u.type = str(def.get("type", "normal"))
	u.level = level
	u.ranged = bool(def.get("ranged", false))
	u.data = def
	var f := CombatData.level_factor(world_n, level)
	var hp_mult := float(CombatData.g("hardcore_enemy_hp", 1.25)) if hardcore else 1.0
	u.max_hp = roundf(float(def.get("hp", 50)) * f * hp_mult)
	u.hp = u.max_hp
	u.stats = {"armor": 0.0, "resist": 0.0, "crit": 0.0, "damage": 0.0, "haste": 0.0}
	u.immortal = u.type == "dummy"
	return u


## Werte neu berechnen (Level-Up, Wiederbelebungsschwaeche); HP/Mana bleiben anteilig erhalten.
func recalc(weak_mult: float) -> void:
	var hf := hp_frac()
	var rf := res_frac()
	stats = _final_stats(weak_mult)
	max_hp = maxf(1.0, roundf(stats["hp"]))
	hp = max_hp * hf if alive else 0.0
	if resource == "mana":
		res_max = roundf(stats["mana"])
		res = res_max * rf


## Levelbasis x (1 + Segen) x Wiederbelebungsschwaeche (GDD 8.2: Segen wirken wie Karten zuletzt, Debuffs danach).
func _final_stats(weak_mult: float) -> Dictionary:
	var st := CombatData.class_stats(klass, level)
	for k in st:
		st[k] *= 1.0 + float(mults.get(k, 0.0))
		if weakened:
			st[k] *= (1.0 - weak_mult)
	return st


## Rang eines Zaubers: gelernte Raenge aus den Speicherdaten (Spieler), sonst nach Level.
func known_rank(spell_id: String) -> int:
	if data.has("spells"):
		return CombatData.learned_rank(data, spell_id)
	return CombatData.spell_rank(spell_id, level)


func hp_frac() -> float:
	return hp / max_hp if max_hp > 0 else 0.0


func res_frac() -> float:
	return res / res_max if res_max > 0 else 0.0


func is_casting() -> bool:
	return not cast.is_empty()


func stat(key: String) -> float:
	return float(stats.get(key, 0.0))


func has_aura(aura_id: String) -> bool:
	return get_aura(aura_id) != {}


func get_aura(aura_id: String) -> Dictionary:
	for a in auras:
		if a["id"] == aura_id:
			return a
	return {}


## Produkt aller Aura-Modifikatoren eines Typs (z. B. "damage_taken").
func aura_mult(key: String) -> float:
	var m := 1.0
	for a in auras:
		m *= float(a.get("mods", {}).get(key, 1.0))
	return m


## Bedrohung, die dieser Gegner gegenueber einer Figur hat.
func threat_of(u: CombatUnit) -> float:
	return float(threat.get(u, 0.0))


func is_tank() -> bool:
	return role == "tank"
