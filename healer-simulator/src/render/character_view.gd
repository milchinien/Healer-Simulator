class_name CharacterView
extends Node2D
## Animierte Pixel-Figur aus 6 Ebenen (Haut, Kleidung, Augen offen/zu, Haare, Helm/Effekte).
## Animationen aus data/characters.json: "idle" (Schleife) und "cast" (einmalig, danach idle).
## Blinzeln: Die Augen-Ebene wird waehrend idle zufaellig kurz ausgeblendet.
## Der Ursprung liegt zwischen den Fuessen; die Figur wird ganzzahlig skaliert (scale = 3 usw.).

signal animation_finished(anim_name: String)

const SHADER := preload("res://src/render/character.gdshader")

@export var show_shadow := true

var appearance := {}
var anim := "idle"
var ghost := false:
	set(v):
		ghost = v
		_update_ghost()

var _rows: Array = []
var _anims: Dictionary = {}
var _sprites := {}
var _materials := {}
var _shadow: Sprite2D
var _frame := -1
var _t := 0.0
var _fs := Vector2i(32, 36)
var _flash_tween: Tween
var _blink_in := 3.0
var _blink_left := 0.0


func _init() -> void:
	var cj := GameData.chars_json()
	_fs = GameData.frame_size()
	_rows = cj.get("layers", ["skin", "outfit", "eyes", "eyes_closed", "hair", "gear"])
	_anims = cj.get("anims", {"idle": {"start": 0, "count": 1, "fps": 1, "loop": true}})
	_shadow = Sprite2D.new()
	_shadow.texture = load("res://assets/gfx/fx/shadow.png")
	add_child(_shadow)
	for row in _rows:
		var s := Sprite2D.new()
		s.centered = false
		s.region_enabled = true
		s.position = Vector2(-_fs.x / 2, -(_fs.y - 1))
		var mat := ShaderMaterial.new()
		mat.shader = SHADER
		mat.set_shader_parameter("swap", row == "skin" or row == "hair")
		mat.set_shader_parameter("c0", GameData.outline_color())
		s.material = mat
		s.visible = row != "eyes_closed"
		_materials[row] = mat
		_sprites[row] = s
		add_child(s)


func _ready() -> void:
	# unterschiedliche Startphase, damit Gruppen nicht synchron atmen
	_t = randf() * 2.0
	_blink_in = randf_range(1.0, 4.0)


func set_appearance(a: Dictionary) -> void:
	appearance = a.duplicate()
	var race: String = a.get("race", "human")
	var klass: String = a.get("class", "priest")
	var style := clampi(int(a.get("hair_style", 0)), 0, GameData.HAIR_STYLE_COUNT - 1)
	var sheet: Texture2D = load("res://assets/gfx/chars/%s_%s_%d.png" % [race, klass, style])
	for row in _rows:
		_sprites[row].texture = sheet
	_apply_ramp("skin", GameData.skin_ramp(race, int(a.get("skin", 0))))
	_apply_ramp("hair", GameData.hair_ramp(race, int(a.get("hair_color", 0))))
	_shadow.visible = show_shadow and not ghost
	_shadow.scale = Vector2(0.7 if race in ["gnome", "dwarf"] else 0.8, 1)
	_frame = -1
	_update_frame()


## Spielt eine Animation ab ("cast" kehrt danach automatisch zu "idle" zurueck).
func play(anim_name: String) -> void:
	if not _anims.has(anim_name):
		return
	anim = anim_name
	_t = 0.0
	_frame = -1
	_blink_left = 0.0
	_update_frame()


func _apply_ramp(row: String, ramp: Array) -> void:
	var m: ShaderMaterial = _materials[row]
	m.set_shader_parameter("c1", Color(ramp[0]))
	m.set_shader_parameter("c2", Color(ramp[1]))
	m.set_shader_parameter("c3", Color(ramp[2]))


func _update_frame() -> void:
	var a: Dictionary = _anims[anim]
	var count := int(a["count"])
	var idx := int(_t * float(a["fps"]))
	if idx >= count:
		if a.get("loop", true):
			idx %= count
		else:
			var finished := anim
			anim = "idle"
			_t = 0.0
			animation_finished.emit(finished)
			_update_frame()
			return
	var f := int(a["start"]) + idx
	if f == _frame:
		return
	_frame = f
	for i in _rows.size():
		_sprites[_rows[i]].region_rect = Rect2(f * _fs.x, i * _fs.y, _fs.x, _fs.y)


func _update_ghost() -> void:
	for row in _rows:
		_materials[row].set_shader_parameter("ghost", 1.0 if ghost else 0.0)
	_shadow.visible = show_shadow and not ghost


## Kurzes Aufleuchten (z. B. nach einer Aenderung in der Charaktererstellung).
func flash(strength := 0.8) -> void:
	if _flash_tween:
		_flash_tween.kill()
	_flash_tween = create_tween()
	_flash_tween.tween_method(_set_flash, strength, 0.0, 0.25)


func _set_flash(v: float) -> void:
	for row in _rows:
		_materials[row].set_shader_parameter("flash", v)


func _process(delta: float) -> void:
	if appearance.is_empty():
		return
	_t += delta
	_update_frame()
	# Blinzeln nur im Ruhezustand
	if anim == "idle" and not ghost:
		if _blink_left > 0.0:
			_blink_left -= delta
		else:
			_blink_in -= delta
			if _blink_in <= 0.0:
				_blink_left = 0.12
				_blink_in = randf_range(2.2, 5.5)
				# gelegentlich doppelt blinzeln
				if randf() < 0.2:
					_blink_in = 0.25
	else:
		_blink_left = 0.0
	var blinking := _blink_left > 0.0
	if _sprites.has("eyes"):
		_sprites["eyes"].visible = not blinking
	if _sprites.has("eyes_closed"):
		_sprites["eyes_closed"].visible = blinking
