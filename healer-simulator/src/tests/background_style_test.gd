extends Node
## Run background_style_test.tscn with -- profile=background_style_test.

var _failures := 0


func check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		push_error(message)


func _ready() -> void:
	if Settings.base_dir == "user://":
		push_error("Use an isolated profile for this test")
		get_tree().quit(1)
		return
	var original := Settings.snapshot()
	var classic: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/scene_art_overrides.json"))
	var refined: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/scene_art_refined.json"))
	check(classic.size() == 9 and refined.size() == 9, "Both styles must cover all nine environments")
	var backdrop := SceneBackdrop.new()
	add_child(backdrop)
	for name in classic:
		for style in ["classic", "refined"]:
			Settings.background_style = style
			Settings.apply()
			backdrop.setup(name)
			await get_tree().process_frame
			var expected: Dictionary = classic[name] if style == "classic" else refined[name]
			check(backdrop.meta == expected, "Wrong environment metadata: %s/%s" % [name, style])
			check(ResourceLoader.exists(expected["background_texture"]), "Missing texture: %s/%s" % [name, style])
			var viewport: SubViewport = backdrop._render_root
			check(viewport.size == (Vector2i(320, 180) if style == "classic" else Vector2i(640, 360)), "Incorrect render grid")
			var layer: Sprite2D = backdrop._render_root.get_child(0)
			check(layer.texture.resource_path == expected["background_texture"], "Wrong rendered texture")
	Settings.background_style = "refined"
	Settings.apply()
	backdrop.setup("charselect")
	var dialog := OptionsDialog.new()
	add_child(dialog)
	dialog._background_sel.set_index(1, true)
	check(backdrop.meta == classic["charselect"], "Option must update the active background immediately")
	dialog._on_cancel()
	check(Settings.background_style == "refined" and backdrop.meta == refined["charselect"], "Cancel must restore style and visible background")
	await dialog.closed
	await get_tree().process_frame
	dialog = OptionsDialog.new()
	add_child(dialog)
	dialog._background_sel.set_index(1, true)
	dialog._on_ok()
	Settings.background_style = "refined"
	Settings.load_settings()
	check(Settings.background_style == "classic", "OK must persist style across reload")
	await dialog.closed
	await get_tree().process_frame
	dialog = OptionsDialog.new()
	add_child(dialog)
	dialog._on_defaults()
	check(Settings.background_style == "refined" and dialog._background_sel.index == 0, "Defaults must select refined style")
	dialog._on_cancel()
	await dialog.closed
	Settings.restore(original)
	Settings.save_settings()
	backdrop.queue_free()
	await get_tree().process_frame
	print("BACKGROUND STYLE TEST: %d failures; nine scenes, live switch, cancel, save/reload, defaults" % _failures)
	get_tree().quit(0 if _failures == 0 else 1)
