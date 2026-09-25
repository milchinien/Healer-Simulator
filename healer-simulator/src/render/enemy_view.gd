class_name EnemyView
extends Node2D
## Animierte Gegnerfigur aus einem Sprite-Sheet (assets/gfx/enemies/<id>.png, eine Zeile Frames).
## Animationen und Framegroesse aus data/enemies_gfx.json. Ursprung zwischen den Fuessen.
## Schleifen-Animationen (idle, cast) laufen weiter; einmalige (attack, hit) kehren zu `base_anim` zurueck.

signal animation_finished(anim_name: String)

static var _meta: Dictionary = {}

var enemy_id := ""
var anim := "idle"
var base_anim := "idle"        # Rueckfall nach einmaligen Animationen (idle, cast oder dead)
var frame_size := Vector2i(32, 32)

var _sprite: Sprite2D
var _shadow: Sprite2D
var _anims := {}
var _t := 0.0
var _frame := -1
var _flash_tween: Tween
var _mat: ShaderMaterial

const FLASH_SHADER := """
shader_type canvas_item;
uniform float flash = 0.0;
uniform vec4 flash_color : source_color = vec4(1.0);
void fragment() {
	vec4 c = texture(TEXTURE, UV);
	c.rgb = mix(c.rgb, flash_color.rgb, flash * c.a);
	COLOR = c * COLOR;
}
"""


static func meta() -> Dictionary:
	if _meta.is_empty():
		var f := FileAccess.open("res://data/enemies_gfx.json", FileAccess.READ)
		if f:
			_meta = JSON.parse_string(f.get_as_text())
	return _meta


func setup(id: String) -> void:
	enemy_id = id
	var m: Dictionary = meta().get(id, {})
	var fs: Array = m.get("frame_size", [32, 32])
	frame_size = Vector2i(int(fs[0]), int(fs[1]))
	_anims = m.get("anims", {"idle": {"start": 0, "count": 1, "fps": 1, "loop": true}})
	_shadow = Sprite2D.new()
	_shadow.texture = load("res://assets/gfx/fx/shadow.png")
	_shadow.scale = Vector2(clampf(frame_size.x / 40.0, 0.5, 1.6), 1)
	add_child(_shadow)
	_sprite = Sprite2D.new()
	_sprite.centered = false
	_sprite.region_enabled = true
	var path := "res://assets/gfx/enemies/%s.png" % id
	if ResourceLoader.exists(path):
		_sprite.texture = load(path)
	_sprite.position = Vector2(-frame_size.x / 2, -(frame_size.y - 1))
	_mat = ShaderMaterial.new()
	var sh := Shader.new()
	sh.code = FLASH_SHADER
	_mat.shader = sh
	_sprite.material = _mat
	add_child(_sprite)
	_t = randf() * 2.0
	_update_frame()


func has_anim(anim_name: String) -> bool:
	return _anims.has(anim_name)


func play(anim_name: String) -> void:
	if not _anims.has(anim_name):
		return
	anim = anim_name
	_t = 0.0
	_frame = -1
	_update_frame()


## Setzt die Grundanimation (idle / cast / dead) und spielt sie sofort.
func set_base(anim_name: String) -> void:
	if not _anims.has(anim_name):
		anim_name = "idle"
	base_anim = anim_name
	play(anim_name)
	_shadow.visible = anim_name != "dead"


func flash(color := Color.WHITE, strength := 0.85) -> void:
	if _flash_tween:
		_flash_tween.kill()
	_mat.set_shader_parameter("flash_color", color)
	_flash_tween = create_tween()
	_flash_tween.tween_method(func(v): _mat.set_shader_parameter("flash", v), strength, 0.0, 0.22)


func _update_frame() -> void:
	var a: Dictionary = _anims.get(anim, _anims.get("idle"))
	var count := int(a["count"])
	var idx := int(_t * float(a["fps"]))
	if idx >= count:
		if a.get("loop", true):
			idx %= count
		else:
			if anim == "dead":
				idx = count - 1
			else:
				var done := anim
				anim = base_anim
				_t = 0.0
				animation_finished.emit(done)
				_update_frame()
				return
	var f := int(a["start"]) + idx
	if f == _frame:
		return
	_frame = f
	_sprite.region_rect = Rect2(f * frame_size.x, 0, frame_size.x, frame_size.y)


func _process(delta: float) -> void:
	if _sprite == null:
		return
	_t += delta
	_update_frame()
