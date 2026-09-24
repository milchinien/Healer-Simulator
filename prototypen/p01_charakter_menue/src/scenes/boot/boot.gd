extends Node
## Startpunkt: leitet zum Titelbildschirm weiter.
##
## Entwickler-/Test-Argumente (nach "--" angeben):
##   profile=<name>      eigenes Speicherprofil (user://profiles/<name>/)
##   scene=<key>         direkt eine Szene oeffnen (title, character_select, character_create, loading)
##   demo=1              legt Beispielcharaktere an, falls das Profil leer ist
##   shot=<pfad.png>     nach `frames` Frames einen Screenshot speichern und beenden
##   frames=<n>          Wartezeit fuer den Screenshot (Standard 90)
##   race=, gender=, mode=, dialog=options|delete|hardcore|menu   (Szenen-Vorgaben fuer Tests)


func _ready() -> void:
	var args := Settings.user_args
	if args.has("test"):
		get_tree().root.add_child.call_deferred(preload("res://src/tests/smoke_test.gd").new())
		return
	if args.has("demo") and SaveGame.count() == 0:
		_create_demo_characters()
	if args.has("shot"):
		var shooter := preload("res://src/scenes/boot/screenshot.gd").new()
		get_tree().root.add_child.call_deferred(shooter)
	var scene: String = args.get("scene", "title")
	var params := {}
	for key in ["race", "gender", "mode", "dialog", "select", "step"]:
		if args.has(key):
			params[key] = args[key]
	Router.jump(scene, params)


func _create_demo_characters() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 7
	var demo := [
		{"name": "Aleria", "race": "human", "gender": "female", "skin": 1, "hair_style": 1, "hair_color": 2, "mode": "normal"},
		{"name": "Brokk", "race": "dwarf", "gender": "male", "skin": 0, "hair_style": 0, "hair_color": 0, "mode": "hardcore"},
		{"name": "Grasha", "race": "orc", "gender": "female", "skin": 0, "hair_style": 1, "hair_color": 0, "mode": "normal"},
		{"name": "Fizzle", "race": "gnome", "gender": "male", "skin": 1, "hair_style": 1, "hair_color": 1, "mode": "hardcore"},
	]
	for i in demo.size():
		var c := CharacterFactory.create_player(demo[i])
		c["created"] = int(c["created"]) + i
		match i:
			1:
				c["fallen"] = true
				c["level"] = 14
				c["world"] = 3
				c["highest_world"] = 3
				c["highest_wave"] = 6
				c["spec"] = "discipline"
				c["gold"] = 212
				c["playtime"] = 20000.0
			2:
				c["level"] = 37
				c["world"] = 7
				c["highest_world"] = 7
				c["highest_wave"] = 4
				c["spec"] = "holy"
				c["gold"] = 4820
				c["playtime"] = 181000.0
				# In diesem Prototyp gibt es nur Krieger-Grafiken; weitere Klassen folgen spaeter
				for _k in 3:
					c["group"].append(CharacterFactory.create_member("warrior", 35, rng))
			3:
				c["level"] = 22
				c["world"] = 5
				c["highest_world"] = 5
				c["highest_wave"] = 2
				c["spec"] = "shadow"
				c["gold"] = 960
				c["playtime"] = 64000.0
				c["group"].append(CharacterFactory.create_member("warrior", 21, rng))
		SaveGame.add_character(c)
