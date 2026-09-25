class_name CharacterFactory
extends RefCounted
## Erzeugt Spielercharaktere und Gruppenmitglieder als Dictionaries (Speicherformat Version 1).
##
## Spielercharakter:
##   id, name, race, gender, skin, hair_style, hair_color, mode ("normal"/"hardcore"), fallen,
##   level, xp, gold, spec ("" / "holy" / "shadow" / "discipline"), created, playtime (Sekunden),
##   world, wave, highest_world, highest_wave, group (Array von Mitgliedern)
## Mitglied:
##   id, name, race, gender, class, level, xp, skin, hair_style, hair_color

const SAVE_VERSION := 1


static func new_id(prefix: String) -> String:
	return "%s_%d_%04d" % [prefix, int(Time.get_unix_time_from_system()), randi() % 10000]


static func create_player(p: Dictionary) -> Dictionary:
	var rng := RandomNumberGenerator.new()
	rng.randomize()
	var character := {
		"version": SAVE_VERSION,
		"id": new_id("c"),
		"name": NameGenerator.normalize(str(p.get("name", ""))),
		"race": p.get("race", "human"),
		"gender": p.get("gender", "male"),
		"skin": int(p.get("skin", 0)),
		"hair_style": int(p.get("hair_style", 0)),
		"hair_color": int(p.get("hair_color", 0)),
		"mode": p.get("mode", "normal"),
		"fallen": false,
		"level": 1,
		"xp": 0,
		"gold": GameData.START_GOLD,
		"spec": "",
		"created": int(Time.get_unix_time_from_system()),
		"playtime": 0.0,
		"world": GameData.START_WORLD,
		"wave": 1,
		"highest_world": GameData.START_WORLD,
		"highest_wave": 0,
		"group": [create_member("warrior", 1, rng)],
		"spells": CombatData.start_spells(),
	}
	return character


static func create_member(klass: String, level: int, rng: RandomNumberGenerator) -> Dictionary:
	var race := GameData.pick_race_for_class(klass, rng)
	var gender: String = GameData.GENDERS[rng.randi() % 2]
	return {
		"id": new_id("m"),
		"name": NameGenerator.generate(race, gender, rng),
		"race": race,
		"gender": gender,
		"class": klass,
		"level": level,
		"xp": 0,
		"skin": rng.randi() % GameData.SKIN_COUNT,
		"hair_style": rng.randi() % GameData.HAIR_STYLE_COUNT,
		"hair_color": rng.randi() % GameData.HAIR_COLOR_COUNT,
	}


## Aussehen-Dictionary fuer CharacterView.
static func appearance_of(c: Dictionary, klass := "priest") -> Dictionary:
	return {
		"race": c.get("race", "human"),
		"class": c.get("class", klass),
		"skin": int(c.get("skin", 0)),
		"hair_style": int(c.get("hair_style", 0)),
		"hair_color": int(c.get("hair_color", 0)),
	}
