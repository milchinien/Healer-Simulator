class_name CharacterView
extends Node2D
## Animierte Pixel-Figur aus 4 Ebenen (Haut, Kleidung, Haare, Helm).
## Der Ursprung liegt zwischen den Fuessen; die Figur wird ganzzahlig skaliert (scale = 3 usw.).

const SHADER := preload("res://src/render/character.gdshader")
const ROWS := ["skin", "outfit", "hair", "gear"]

@export var frame_time := 0.3
@export var show_shadow := true

var appearance := {}
var ghost := false:
	set(v):
		ghost = v
		_update_ghost()

var _sprites := {}
var _materials := {}
var _shadow: Sprite2D
var _frame := 0
var _t := 0.0
var _fs := Vector2i(32, 36)
var _flash_tween: Tween


func _init() -> void:
	_fs = GameData.frame_size()
	_shadow = Sprite2D.new()
	_shadow.texture = load("res://assets/gfx/fx/shadow.png")
	_shadow.position = Vector2(0, 0)
	add_child(_shadow)
	for row in ROWS:
		var s := Sprite2D.new()
		s.centered = false
		s.region_enabled = true
		s.position = Vector2(-_fs.x / 2, -(_fs.y - 1))
		var mat := ShaderMaterial.new()
		mat.shader = SHADER
		mat.set_shader_parameter("swap", row == "skin" or row == "hair")
		mat.set_shader_parameter("c0", GameData.outline_color())
		s.material = mat
		_materials[row] = mat
		_sprites[row] = s
		add_child(s)


func _ready() -> void:
	# unterschiedliche Startphase, damit Gruppen nicht synchron atmen
	_t = randf() * frame_time * 4.0


func set_appearance(a: Dictionary) -> void:
	appearance = a.duplicate()
	var race: String = a.get("race", "human")
	var klass: String = a.get("class", "priest")
	var style := clampi(int(a.get("hair_style", 0)), 0, GameData.HAIR_STYLE_COUNT - 1)
	var sheet: Texture2D = load("res://assets/gfx/chars/%s_%s_%d.png" % [race, klass, style])
	for row in ROWS:
		_sprites[row].texture = sheet
	_apply_ramp("skin", GameData.skin_ramp(race, int(a.get("skin", 0))))
	_apply_ramp("hair", GameData.hair_ramp(race, int(a.get("hair_color", 0))))
	_shadow.visible = show_shadow
	_shadow.scale = Vector2(0.7 if race in ["gnome", "dwarf"] else 0.8, 1)
	_update_regions()


func _apply_ramp(row: String, ramp: Array) -> void:
	var m: ShaderMaterial = _materials[row]
	m.set_shader_parameter("c1", Color(ramp[0]))
	m.set_shader_parameter("c2", Color(ramp[1]))
	m.set_shader_parameter("c3", Color(ramp[2]))


func _update_regions() -> void:
	for i in ROWS.size():
		_sprites[ROWS[i]].region_rect = Rect2(_frame * _fs.x, i * _fs.y, _fs.x, _fs.y)


func _update_ghost() -> void:
	for row in ROWS:
		_materials[row].set_shader_parameter("ghost", 1.0 if ghost else 0.0)
	_shadow.visible = show_shadow and not ghost


## Kurzes Aufleuchten (z. B. nach einer Aenderung in der Charaktererstellung).
func flash(strength := 0.8) -> void:
	if _flash_tween:
		_flash_tween.kill()
	_flash_tween = create_tween()
	_flash_tween.tween_method(_set_flash, strength, 0.0, 0.25)


func _set_flash(v: float) -> void:
	for row in ROWS:
		_materials[row].set_shader_parameter("flash", v)


func _process(delta: float) -> void:
	if appearance.is_empty():
		return
	_t += delta
	var f := int(_t / frame_time) % GameData.frame_count()
	if f != _frame:
		_frame = f
		_update_regions()
