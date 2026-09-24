extends Node
## Automatischer Rauchtest (headless):
##   godot --headless --path . -- profile=smoketest test=1
## Prueft Namensregeln, Speichern/Laden, Reihenfolge, Loeschen und laedt alle Szenen.

var _fails := 0


func _ready() -> void:
	await get_tree().process_frame
	_test_names()
	_test_save_roundtrip()
	await _test_scenes()
	await _test_flows()
	if _fails == 0:
		print("SMOKE OK")
	else:
		print("SMOKE FAILED: %d" % _fails)
	get_tree().quit(1 if _fails > 0 else 0)


func check(cond: bool, what: String) -> void:
	if cond:
		print("  ok   ", what)
	else:
		_fails += 1
		print("  FAIL ", what)


func _test_names() -> void:
	print("Namen")
	check(NameGenerator.validate("A", []) == "CREATE_ERR_NAME_SHORT", "zu kurz")
	check(NameGenerator.validate("Abcdefghijklm", []) == "CREATE_ERR_NAME_LONG", "zu lang")
	check(NameGenerator.validate("Ab1", []) == "CREATE_ERR_NAME_CHARS", "Ziffern verboten")
	check(NameGenerator.validate("Jörg", []) == "", "Umlaute erlaubt")
	check(NameGenerator.validate("aleria", ["Aleria"]) == "CREATE_ERR_NAME_TAKEN", "doppelt (Gross/Klein egal)")
	check(NameGenerator.normalize("aLERIA") == "Aleria", "Schreibweise normalisiert")
	var rng := RandomNumberGenerator.new()
	rng.seed = 1
	for race in GameData.RACES:
		for g in GameData.GENDERS:
			var n := NameGenerator.generate(race, g, rng)
			check(NameGenerator.validate(n, []) == "", "Namensvorschlag %s/%s: %s" % [race, g, n])


func _test_save_roundtrip() -> void:
	print("Speichern")
	for c in SaveGame.list():
		SaveGame.delete_character(c["id"])
	check(SaveGame.count() == 0, "Profil leer")
	var ids := []
	for i in 3:
		var c := CharacterFactory.create_player({"name": "Test%s" % ["a", "b", "c"][i], "race": GameData.RACES[i], "gender": "female",
			"skin": 2, "hair_style": 1, "hair_color": 3, "mode": "hardcore" if i == 1 else "normal"})
		SaveGame.add_character(c)
		ids.append(c["id"])
	check(SaveGame.count() == 3, "3 Charaktere angelegt")
	var first := SaveGame.get_character(ids[0])
	check(first["group"].size() == 1 and first["group"][0]["class"] == "warrior", "Start-Krieger in der Gruppe")
	check(first["gold"] == GameData.START_GOLD and first["level"] == 1, "Startwerte")
	SaveGame.move_character(ids[2], 0)
	SaveGame._load_all()
	var order := SaveGame.list().map(func(c): return c["id"])
	check(order[0] == ids[2], "Reihenfolge gespeichert")
	var loaded := SaveGame.get_character(ids[1])
	check(typeof(loaded["level"]) == TYPE_INT and typeof(loaded["skin"]) == TYPE_INT, "Ganzzahlen nach dem Laden")
	check(loaded["mode"] == "hardcore", "Modus gespeichert")
	SaveGame.delete_character(ids[1])
	SaveGame._load_all()
	check(SaveGame.count() == 2 and SaveGame.get_character(ids[1]).is_empty(), "Loeschen")
	for i in GameData.MAX_CHARACTERS:
		if SaveGame.is_full():
			break
		SaveGame.add_character(CharacterFactory.create_player({"name": "Fill%s" % char(97 + i)}))
	check(SaveGame.is_full() and SaveGame.count() == GameData.MAX_CHARACTERS, "Maximal 10 Charaktere")


func _test_scenes() -> void:
	print("Szenen")
	for key in ["title", "character_select", "character_create", "loading"]:
		get_tree().change_scene_to_file(Router.SCENES[key])
		for i in 20:
			await get_tree().process_frame
		check(get_tree().current_scene != null and get_tree().current_scene.scene_file_path == Router.SCENES[key], "Szene %s" % key)


func _wait(frames := 10) -> void:
	for i in frames:
		await get_tree().process_frame


func _test_flows() -> void:
	print("Ablaeufe")
	for c in SaveGame.list():
		SaveGame.delete_character(c["id"])
	# Charaktererstellung: Rasse/Aussehen waehlen, Namen wuerfeln, erstellen
	Router.params = {}
	get_tree().change_scene_to_file(Router.SCENES["character_create"])
	await _wait()
	var cc := get_tree().current_scene
	cc._set_race("orc")
	cc._set_gender("female")
	cc._skin_sel.step(1)
	cc._hair_sel.set_index(4, true)
	cc._style_sel.step(-1)
	cc._on_create()
	check(SaveGame.count() == 0, "leerer Name wird abgelehnt")
	check(cc._error.text == "CREATE_ERR_NAME_SHORT", "Fehlermeldung fuer leeren Namen")
	cc._roll_name()
	check(cc._name_edit.text.length() >= 2, "Wuerfel schlaegt Namen vor: %s" % cc._name_edit.text)
	cc._on_create()
	check(SaveGame.count() == 1, "Charakter erstellt")
	var made: Dictionary = SaveGame.list()[0]
	check(made["race"] == "orc" and made["gender"] == "female" and made["skin"] == 1 and made["hair_color"] == 4 and made["hair_style"] == 2,
		"Auswahl uebernommen (orc, weiblich, Haut 2, Frisur 3, Haar 5)")
	# Router wechselt mit Blende zur Auswahl
	for i in 120:
		await get_tree().process_frame
		if not Router.busy:
			break
	check(get_tree().current_scene.scene_file_path == Router.SCENES["character_select"], "nach Erstellen in der Charakterauswahl")
	var sel := get_tree().current_scene
	check(sel._selected_id == made["id"], "neuer Charakter ist ausgewaehlt")
	# Zweiten Charakter anlegen und per Drop umsortieren
	var second := CharacterFactory.create_player({"name": "Zweite", "race": "gnome"})
	SaveGame.add_character(second)
	await _wait(3)
	sel._on_drop(second["id"], made["id"], false)
	check(SaveGame.list()[0]["id"] == second["id"], "Drag & Drop sortiert um")
	# Loeschen ueber den Dialog
	sel._select(second["id"])
	sel._on_delete()
	await _wait(3)
	var dlg: DeleteDialog = null
	for ch in sel.get_children():
		if ch is DeleteDialog:
			dlg = ch
	check(dlg != null, "Loeschdialog geoeffnet")
	if dlg:
		check(dlg._delete_btn.disabled, "Loeschen gesperrt ohne Namen")
		dlg._input.text = "zweite"
		dlg._validate()
		check(not dlg._delete_btn.disabled, "Loeschen frei nach Namenseingabe (Gross/Klein egal)")
		dlg._confirm()
		await _wait(20)
		check(SaveGame.count() == 1 and SaveGame.get_character(second["id"]).is_empty(), "Charakter geloescht")
	# Welt betreten -> Ladebildschirm
	sel._select(made["id"])
	sel._on_enter_world()
	for i in 120:
		await get_tree().process_frame
		if not Router.busy:
			break
	check(get_tree().current_scene.scene_file_path == Router.SCENES["loading"], "Welt betreten zeigt den Ladebildschirm")
	# Gefallener Hardcore-Charakter darf nicht betreten werden
	made["fallen"] = true
	SaveGame.save_character(made)
	get_tree().change_scene_to_file(Router.SCENES["character_select"])
	await _wait()
	var sel2 := get_tree().current_scene
	check(sel2._enter_btn.disabled, "Welt betreten gesperrt fuer Gefallene")

