extends SceneBackdrop
## Background-only art preview. Run market_preview.tscn directly (F6).

func _ready() -> void:
	setup(str(Settings.user_args.get("background", "charselect")))
	if Settings.user_args.has("shot"):
		var shooter := preload("res://src/scenes/boot/screenshot.gd").new()
		get_tree().root.add_child.call_deferred(shooter)
