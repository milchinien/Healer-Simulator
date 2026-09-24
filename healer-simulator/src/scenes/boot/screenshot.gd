extends Node
## Test-Hilfe: speichert nach N Frames ein Bild des Viewports und beendet das Spiel.

var _frames := 90
var _path := ""


func _ready() -> void:
	_path = Settings.user_args.get("shot", "")
	_frames = int(Settings.user_args.get("frames", "90"))
	process_mode = Node.PROCESS_MODE_ALWAYS


func _process(_delta: float) -> void:
	_frames -= 1
	if _frames == 0:
		var img := get_viewport().get_texture().get_image()
		img.save_png(_path)
		print("SCREENSHOT ", _path)
		get_tree().quit()
