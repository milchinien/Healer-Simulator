class_name NameGenerator
extends RefCounted
## Erzeugt passende Namen je Rasse und Geschlecht aus Silben.

const PARTS := {
	"human": {
		"male": {"a": ["Al", "Bran", "Ced", "Dar", "Ed", "Gar", "Hal", "Jor", "Lu", "Mar", "Os", "Ro", "Tho", "Wil", "Ben", "Kas"],
			"b": ["ric", "wen", "an", "ius", "mund", "ton", "ard", "win", "ren", "den", "vin", "mar", "ek", "las"]},
		"female": {"a": ["A", "Bri", "Ce", "Eli", "Ga", "Is", "Je", "Li", "Ma", "Ro", "Se", "Tha", "Vi", "Ela", "Mi", "Ali"],
			"b": ["na", "ra", "wen", "lia", "sa", "ssa", "rin", "belle", "ne", "ra", "ya", "nia", "via", "ria"]},
	},
	"dwarf": {
		"male": {"a": ["Bal", "Dur", "Grim", "Thor", "Mag", "Bor", "Dag", "Bru", "Kaz", "Ham", "Gund", "Rur"],
			"b": ["in", "gar", "grim", "dan", "ek", "rum", "bar", "ni", "dor", "brand", "thum", "ok"]},
		"female": {"a": ["Brun", "Dag", "Hel", "Kat", "Mag", "Thra", "Ing", "Gret", "Hil", "Sig", "Vol", "Ber"],
			"b": ["hild", "na", "ga", "ra", "rid", "da", "trud", "ja", "grun", "dis", "ma", "wyn"]},
	},
	"orc": {
		"male": {"a": ["Grom", "Thr", "Ug", "Kar", "Mog", "Dra", "Gor", "Naz", "Rok", "Zug", "Bol", "Kro"],
			"b": ["ash", "gar", "rok", "ok", "thar", "ug", "mak", "gul", "zag", "rash", "dak", "grim"]},
		"female": {"a": ["Gar", "Sha", "Ug", "Zi", "Mag", "Ro", "Kra", "Dur", "Ag", "Na", "Ya", "Ur"],
			"b": ["ona", "ka", "tha", "ra", "grah", "za", "sha", "ga", "ruk", "gra", "ka", "za"]},
	},
	"gnome": {
		"male": {"a": ["Fiz", "Bix", "Tink", "Gim", "Nob", "Pip", "Zik", "Wob", "Dim", "Sprock", "Tob", "Mek"],
			"b": ["zle", "wick", "bolt", "nob", "sprocket", "pin", "kel", "fuse", "gear", "wiz", "tock", "zik"]},
		"female": {"a": ["Bim", "Fizz", "Tilly", "Pip", "Nix", "Wren", "Zin", "Libby", "Tess", "Dot", "Mimi", "Kiki"],
			"b": ["ble", "a", "wick", "sy", "nia", "kle", "ka", "belle", "fizz", "ette", "li", "ni"]},
	},
}


static func generate(race: String, gender: String, rng: RandomNumberGenerator, taken: Array = []) -> String:
	var parts: Dictionary = PARTS.get(race, PARTS["human"]).get(gender, PARTS["human"]["male"])
	var result := ""
	for attempt in 40:
		var a: String = parts["a"][rng.randi() % parts["a"].size()]
		var b: String = parts["b"][rng.randi() % parts["b"].size()]
		# Doppelte Buchstaben an der Silbengrenze vermeiden
		if a.right(1).to_lower() == b.left(1).to_lower():
			b = b.substr(1)
		result = normalize(a + b)
		if result.length() >= GameData.NAME_MIN and result.length() <= GameData.NAME_MAX \
				and not _is_taken(result, taken):
			return result
	return result


## Erster Buchstabe gross, Rest klein (wie in klassischen MMOs).
static func normalize(name_text: String) -> String:
	var s := name_text.strip_edges()
	if s.is_empty():
		return s
	return s.left(1).to_upper() + s.substr(1).to_lower()


static func _is_taken(n: String, taken: Array) -> bool:
	for t in taken:
		if str(t).to_lower() == n.to_lower():
			return true
	return false


## Prueft einen Namen. Gibt "" zurueck, wenn er gueltig ist, sonst einen Fehlerschluessel.
static func validate(name_text: String, taken: Array) -> String:
	var n := name_text.strip_edges()
	if n.length() < GameData.NAME_MIN:
		return "CREATE_ERR_NAME_SHORT"
	if n.length() > GameData.NAME_MAX:
		return "CREATE_ERR_NAME_LONG"
	var re := RegEx.new()
	re.compile("^[A-Za-zÄÖÜäöüß]+$")
	if re.search(n) == null:
		return "CREATE_ERR_NAME_CHARS"
	if _is_taken(n, taken):
		return "CREATE_ERR_NAME_TAKEN"
	return ""
