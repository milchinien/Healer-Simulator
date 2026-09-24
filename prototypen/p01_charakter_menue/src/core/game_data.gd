class_name GameData
extends RefCounted
## Statische Spieldaten: Rassen, Paletten, Klassen-Rassen-Tabelle, Startwerte.
## Grafikdaten kommen aus data/characters.json (erzeugt vom Grafik-Build).

const RACES := ["human", "dwarf", "orc", "gnome"]
const GENDERS := ["male", "female"]
const MODES := ["normal", "hardcore"]
const SKIN_COUNT := 5
const HAIR_STYLE_COUNT := 3
const HAIR_COLOR_COUNT := 5
const MAX_CHARACTERS := 10
const NAME_MIN := 2
const NAME_MAX := 12
const START_GOLD := 10
const START_WORLD := 1

## Rassen-Wahrscheinlichkeit je Klasse (GDD Kapitel 15.4) in Prozent: Mensch, Zwerg, Orc, Gnom
const CLASS_RACE_WEIGHTS := {
	"warrior": [20, 35, 40, 5],
	"paladin": [35, 45, 15, 5],
	"mage": [40, 5, 10, 45],
	"warlock": [35, 5, 25, 35],
	"hunter": [30, 35, 30, 5],
	"rogue": [45, 5, 10, 40],
	"druid": [45, 15, 30, 10],
	"priest": [40, 30, 10, 20],
}

## Levelbereiche der Welten (GDD Kapitel 16.1) fuer Anzeigen
const WORLD_LEVELS := {
	1: [1, 3], 2: [4, 7], 3: [8, 12], 4: [13, 18], 5: [19, 24],
	6: [25, 30], 7: [31, 37], 8: [38, 44], 9: [45, 52], 10: [53, 60],
}

static var _chars_json: Dictionary = {}


static func chars_json() -> Dictionary:
	if _chars_json.is_empty():
		var f := FileAccess.open("res://data/characters.json", FileAccess.READ)
		_chars_json = JSON.parse_string(f.get_as_text())
	return _chars_json


static func skin_ramp(race: String, index: int) -> Array:
	return chars_json()["skin_palettes"][race][clampi(index, 0, SKIN_COUNT - 1)]


static func hair_ramp(race: String, index: int) -> Array:
	return chars_json()["hair_palettes"][race][clampi(index, 0, HAIR_COLOR_COUNT - 1)]


static func outline_color() -> Color:
	return Color(chars_json()["outline"])


static func frame_size() -> Vector2i:
	var fs: Array = chars_json()["frame_size"]
	return Vector2i(int(fs[0]), int(fs[1]))


static func frame_count() -> int:
	return int(chars_json()["frames"])


static func pick_race_for_class(klass: String, rng: RandomNumberGenerator) -> String:
	var weights: Array = CLASS_RACE_WEIGHTS.get(klass, [25, 25, 25, 25])
	var roll := rng.randi_range(1, 100)
	var acc := 0
	for i in RACES.size():
		acc += int(weights[i])
		if roll <= acc:
			return RACES[i]
	return RACES[0]
