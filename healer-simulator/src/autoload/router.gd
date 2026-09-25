extends Node
## Szenenwechsel mit Ueberblendung und gemeinsamen Parametern.
## Router.go("character_select", {"select_id": "..."})

const SCENES := {
	"title": "res://src/scenes/title/title.tscn",
	"character_select": "res://src/scenes/character_select/character_select.tscn",
	"character_create": "res://src/scenes/character_create/character_create.tscn",
	"loading": "res://src/scenes/loading/loading.tscn",
	"game": "res://src/scenes/game/game.tscn",
}

## Parameter fuer die naechste Szene (wird von ihr in _ready gelesen)
var params := {}
var current := ""
var busy := false

var _layer: CanvasLayer
var _fade: ColorRect


func _ready() -> void:
	_layer = CanvasLayer.new()
	_layer.layer = 100
	add_child(_layer)
	_fade = ColorRect.new()
	_fade.color = Color("07050b")
	_fade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fade.modulate.a = 0.0
	_layer.add_child(_fade)


func go(scene_key: String, p: Dictionary = {}, fade_out := 0.35, fade_in := 0.45) -> void:
	if busy:
		return
	busy = true
	params = p
	_fade.mouse_filter = Control.MOUSE_FILTER_STOP
	var tw := create_tween()
	tw.tween_property(_fade, "modulate:a", 1.0, fade_out)
	await tw.finished
	current = scene_key
	get_tree().change_scene_to_file(SCENES[scene_key])
	await get_tree().process_frame
	await get_tree().process_frame
	var tw2 := create_tween()
	tw2.tween_property(_fade, "modulate:a", 0.0, fade_in)
	await tw2.finished
	_fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	busy = false


## Sofortiger Wechsel ohne Blende (Start).
func jump(scene_key: String, p: Dictionary = {}) -> void:
	params = p
	current = scene_key
	get_tree().change_scene_to_file.call_deferred(SCENES[scene_key])


func take_param(key: String, default = null):
	var v = params.get(key, default)
	params.erase(key)
	return v
