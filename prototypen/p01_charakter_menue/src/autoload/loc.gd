extends Node
## Uebersetzungen (Englisch/Deutsch) aus data/i18n.json.
## Alle Texte im Spiel sind Schluessel (z. B. "SELECT_ENTER_WORLD"); Controls uebersetzen
## sie automatisch, im Code wird tr("KEY") bzw. Loc.t("KEY", {...}) verwendet.

const LANGUAGES := ["en", "de"]
const LANGUAGE_NAMES := {"en": "English", "de": "Deutsch"}


func _enter_tree() -> void:
	var file := FileAccess.open("res://data/i18n.json", FileAccess.READ)
	if file == null:
		push_error("i18n.json fehlt")
		return
	var data: Dictionary = JSON.parse_string(file.get_as_text())
	for lang in LANGUAGES:
		var tr_res := Translation.new()
		tr_res.locale = lang
		for key in data:
			var entry: Dictionary = data[key]
			tr_res.add_message(key, str(entry.get(lang, entry.get("en", key))))
		TranslationServer.add_translation(tr_res)


## Uebersetzt einen Schluessel und setzt Platzhalter {name} ein.
func t(key: String, args: Dictionary = {}) -> String:
	var s := tr(key)
	if not args.is_empty():
		s = s.format(args)
	return s


## Klassenbezeichnung je nach Geschlecht ("Priester"/"Priesterin").
func class_name_for(klass: String, gender: String) -> String:
	return tr("CLASS_%s_%s" % [klass.to_upper(), gender.to_upper()])


func race_name(race: String) -> String:
	return tr("RACE_%s" % race.to_upper())


func world_name(world: int) -> String:
	return tr("WORLD_%d" % world)
