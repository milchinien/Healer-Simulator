class_name SceneBackdrop
extends Control
## Lebendiger Hintergrund: vorgerenderte Ebenen (assets/gfx/bg/<szene>_<ebene>.png) plus animierte
## Elemente aus data/scenes.json ("props"):
##   clouds    - Wolkenband, verformt sich ueber mehrere Frames und zieht seitlich (kachelbar)
##   glow      - additives Licht (Laternen, Fenster, Lichtkegel am Boden), flackert
##   flame     - kleine Laternenflamme (animiert)
##   fire      - Lagerfeuer/Kohlebecken mit Glut, Licht und Funken
##   anim      - beliebiges Spritesheet (Fahnen, Zahnraeder, Windmuehle, Wasserglitzern)
##   beam      - Lichtsaeule (Titel)
##   particles - Gluehwuermchen, Rauch, Dampf, Funken, Blaetter, Voegel, Staub ...

const ADD_MAT := preload("res://src/render/additive.tres")

var scene_name := ""
var meta := {}
var _clouds: Array = []     # [Sprite2D a, Sprite2D b, speed, x(float), frames, fps, h]
var _glows: Array = []      # [Sprite2D, alpha, phase, speed, flicker]
var _anims: Array = []      # [Sprite2D, frames, fps, phase, reverse]
var _beam: Sprite2D
var _time := 0.0

static var _meta_cache := {}


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


static func scene_meta(name: String) -> Dictionary:
	if _meta_cache.is_empty():
		var f := FileAccess.open("res://data/scenes.json", FileAccess.READ)
		_meta_cache = JSON.parse_string(f.get_as_text())
	return _meta_cache.get(name, {})


func setup(name: String) -> void:
	for c in get_children():
		c.queue_free()
	_clouds.clear()
	_glows.clear()
	_anims.clear()
	_beam = null
	scene_name = name
	meta = scene_meta(name)
	var layers: Array = meta.get("layers", ["bg"])
	_add_layer("bg")
	for p in meta.get("props", []):
		match str(p.get("type", "")):
			"clouds":
				_add_clouds(p)
			"glow":
				_add_glow(Vector2(p["x"], p["y"]), load("res://assets/gfx/fx/%s.png" % p["tex"]), float(p.get("alpha", 0.8)),
					float(p.get("flicker", 0.1)), float(p.get("speed", 1.0)))
			"flame":
				_add_flame(Vector2(p["x"], p["y"]))
			"fire":
				_add_fire(Vector2(p["x"], p["y"]))
			"anim":
				_add_anim(p)
			"beam":
				_add_beam(Vector2(p["x"], p["y"]))
			"particles":
				_add_particles(str(p["kind"]), Vector2(p["x"], p["y"]), Vector2(p.get("w", 4), p.get("h", 4)))
	if "fg" in layers:
		_add_layer("fg")


func _add_layer(layer: String) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = load("res://assets/gfx/bg/%s_%s.png" % [scene_name, layer])
	s.centered = false
	add_child(s)
	return s


func _add_clouds(p: Dictionary) -> void:
	var tex: Texture2D = load("res://assets/gfx/bg/%s.png" % p["tex"])
	var frames := int(p.get("frames", 1))
	var h := int(p.get("h", tex.get_height() / frames))
	var pair: Array = []
	for i in 2:
		var s := Sprite2D.new()
		s.texture = tex
		s.centered = false
		s.region_enabled = true
		s.region_rect = Rect2(0, 0, 640, h)
		s.position = Vector2(i * 640, float(p.get("y", 0)))
		add_child(s)
		pair.append(s)
	_clouds.append([pair[0], pair[1], float(p.get("speed", 2.0)), randf() * 640.0, frames, float(p.get("fps", 1.5)), h])


func _add_glow(pos: Vector2, texture: Texture2D, base_alpha: float, flicker := 0.1, speed := 1.0) -> Sprite2D:
	var g := Sprite2D.new()
	g.texture = texture
	g.position = pos
	g.material = ADD_MAT
	g.modulate.a = base_alpha
	add_child(g)
	_glows.append([g, base_alpha, randf() * TAU, randf_range(0.8, 1.2) * speed, flicker])
	return g


func _add_flame(pos: Vector2) -> void:
	var f := Sprite2D.new()
	f.texture = load("res://assets/gfx/fx/lantern_flame.png")
	f.hframes = 6
	f.position = pos + Vector2(0, -1)
	add_child(f)
	_anims.append([f, 6, randf_range(7.0, 10.0), randf() * 6.0, false])


func _add_fire(pos: Vector2) -> void:
	_add_glow(pos + Vector2(0, -8), load("res://assets/gfx/fx/glow_lamp.png"), 0.75, 0.18, 1.5)
	var f := Sprite2D.new()
	f.texture = load("res://assets/gfx/fx/fire.png")
	f.hframes = 8
	f.centered = false
	f.position = pos + Vector2(-8, -21)
	add_child(f)
	_anims.append([f, 8, 11.0, randf() * 8.0, false])
	_add_particles("embers_fire", pos + Vector2(0, -12), Vector2(4, 2))


func _add_anim(p: Dictionary) -> void:
	var s := Sprite2D.new()
	s.texture = load("res://assets/gfx/bg/%s.png" % p["tex"])
	s.hframes = int(p.get("hframes", 1))
	s.vframes = int(p.get("vframes", 1))
	s.centered = false
	s.position = Vector2(p["x"], p["y"])
	if p.get("additive", false):
		s.material = ADD_MAT
	s.modulate.a = float(p.get("alpha", 1.0))
	add_child(s)
	_anims.append([s, s.hframes * s.vframes, float(p.get("fps", 6)), randf() * 8.0, bool(p.get("reverse", false))])


func _add_beam(pos: Vector2) -> void:
	_beam = Sprite2D.new()
	_beam.texture = load("res://assets/gfx/fx/beam.png")
	_beam.centered = false
	_beam.position = Vector2(pos.x - 20, pos.y - 180)
	_beam.material = ADD_MAT
	_beam.modulate.a = 0.5
	add_child(_beam)
	_add_glow(pos, load("res://assets/gfx/fx/glow_lamp.png"), 0.9, 0.08)


# ---------------------------------------------------------------- Partikel
func _add_particles(kind: String, pos: Vector2, extents: Vector2) -> void:
	var p := CPUParticles2D.new()
	p.texture = load("res://assets/gfx/fx/dot.png")
	p.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
	p.emission_rect_extents = extents
	p.position = pos
	p.local_coords = false
	var grad := Gradient.new()
	match kind:
		"fireflies", "fireflies_town", "fireflies_day":
			p.amount = {"fireflies": 26, "fireflies_town": 8, "fireflies_day": 12}[kind]
			p.lifetime = 6.0
			p.gravity = Vector2(0, -1.5)
			p.initial_velocity_min = 2
			p.initial_velocity_max = 7
			p.spread = 180
			p.direction = Vector2(0, -1)
			var c := Color("f4ff9a") if kind != "fireflies_day" else Color("ffffff")
			grad.colors = PackedColorArray([Color(c, 0), Color(c, 1), Color(c, 0.15), Color(c, 1), Color(c, 0)])
			grad.offsets = PackedFloat32Array([0, 0.2, 0.5, 0.75, 1])
			p.preprocess = 6.0
			p.material = ADD_MAT
		"stars_twinkle":
			p.amount = 12
			p.lifetime = 2.5
			p.gravity = Vector2.ZERO
			p.initial_velocity_min = 0
			p.initial_velocity_max = 0
			p.texture = load("res://assets/gfx/fx/sparkle.png")
			grad.colors = PackedColorArray([Color(1, 1, 1, 0), Color(0.85, 0.9, 1, 0.9), Color(1, 1, 1, 0)])
			p.preprocess = 3.0
		"motes", "motes_teal":
			p.amount = 18
			p.lifetime = 7.0
			p.gravity = Vector2(0, -1.5)
			p.initial_velocity_min = 1
			p.initial_velocity_max = 5
			p.spread = 180
			var c2 := Color("ffd9a0") if kind == "motes" else Color("9af0e6")
			grad.colors = PackedColorArray([Color(c2, 0), Color(c2, 0.7), Color(c2, 0)])
			p.preprocess = 7.0
		"leaves":
			p.amount = 10
			p.lifetime = 8.0
			p.gravity = Vector2(4, 9)
			p.initial_velocity_min = 4
			p.initial_velocity_max = 10
			p.direction = Vector2(1, 0.3)
			grad.colors = PackedColorArray([Color("78b85a"), Color("a8d070"), Color(0.5, 0.7, 0.3, 0)])
			p.preprocess = 8.0
		"embers":
			p.amount = 26
			p.lifetime = 4.0
			p.gravity = Vector2(0, -10)
			p.initial_velocity_min = 4
			p.initial_velocity_max = 14
			p.direction = Vector2(0, -1)
			p.spread = 40
			grad.colors = PackedColorArray([Color("fff0a0"), Color("ff9a3a"), Color(0.8, 0.2, 0.1, 0)])
			p.preprocess = 4.0
		"embers_fire":
			p.amount = 8
			p.lifetime = 1.6
			p.gravity = Vector2(0, -18)
			p.initial_velocity_min = 4
			p.initial_velocity_max = 10
			p.direction = Vector2(0, -1)
			p.spread = 30
			grad.colors = PackedColorArray([Color("fff0a0"), Color("ff7a2a"), Color(0.6, 0.1, 0.05, 0)])
			p.preprocess = 2.0
		"dust":
			p.amount = 14
			p.lifetime = 6.0
			p.gravity = Vector2(10, 0)
			p.initial_velocity_min = 40
			p.initial_velocity_max = 90
			p.direction = Vector2(1, -0.05)
			p.spread = 6
			grad.colors = PackedColorArray([Color(0.95, 0.75, 0.5, 0), Color(0.95, 0.75, 0.5, 0.5), Color(0.95, 0.75, 0.5, 0)])
			p.preprocess = 6.0
		"smoke":
			p.amount = 10
			p.lifetime = 5.0
			p.gravity = Vector2(3, -4)
			p.initial_velocity_min = 2
			p.initial_velocity_max = 5
			p.direction = Vector2(0.2, -1)
			p.spread = 12
			p.scale_amount_min = 1.0
			p.scale_amount_max = 2.0
			grad.colors = PackedColorArray([Color(0.55, 0.5, 0.6, 0), Color(0.55, 0.5, 0.62, 0.45), Color(0.45, 0.4, 0.55, 0)])
			p.preprocess = 5.0
		"steam":
			p.amount = 14
			p.lifetime = 2.2
			p.gravity = Vector2(0, -6)
			p.initial_velocity_min = 6
			p.initial_velocity_max = 12
			p.direction = Vector2(0, -1)
			p.spread = 18
			p.scale_amount_min = 1.0
			p.scale_amount_max = 2.5
			grad.colors = PackedColorArray([Color(1, 1, 1, 0), Color(0.9, 0.95, 1, 0.55), Color(1, 1, 1, 0)])
			p.preprocess = 3.0
		"fountain":
			p.amount = 16
			p.lifetime = 0.9
			p.gravity = Vector2(0, 40)
			p.initial_velocity_min = 14
			p.initial_velocity_max = 20
			p.direction = Vector2(0, -1)
			p.spread = 25
			grad.colors = PackedColorArray([Color("d8ecff"), Color("8ab8f0"), Color(0.5, 0.7, 1, 0)])
			p.preprocess = 1.0
		"birds":
			p.amount = 5
			p.lifetime = 16.0
			p.position = Vector2(-20, pos.y)
			p.gravity = Vector2.ZERO
			p.initial_velocity_min = 22
			p.initial_velocity_max = 34
			p.direction = Vector2(1, -0.05)
			p.spread = 4
			p.texture = _bird_texture()
			grad.colors = PackedColorArray([Color("2a3448"), Color("2a3448")])
			p.preprocess = 16.0
		_:
			p.queue_free()
			return
	p.color_ramp = grad
	add_child(p)


func _bird_texture() -> Texture2D:
	var img := Image.create(5, 2, false, Image.FORMAT_RGBA8)
	for pt in [Vector2i(0, 0), Vector2i(1, 1), Vector2i(2, 0), Vector2i(3, 1), Vector2i(4, 0)]:
		img.set_pixelv(pt, Color.WHITE)
	return ImageTexture.create_from_image(img)


# ---------------------------------------------------------------- Ablauf
func _process(delta: float) -> void:
	_time += delta
	for cl in _clouds:
		cl[3] = fmod(float(cl[3]) + float(cl[2]) * delta, 640.0)
		var x := -roundi(float(cl[3]))
		cl[0].position.x = x
		cl[1].position.x = x + 640
		var frame := int(_time * float(cl[5])) % int(cl[4])
		var r := Rect2(0, frame * int(cl[6]), 640, int(cl[6]))
		cl[0].region_rect = r
		cl[1].region_rect = r
	for g in _glows:
		var spr: Sprite2D = g[0]
		var t: float = _time * float(g[3]) + float(g[2])
		var fl: float = float(g[4])
		spr.modulate.a = clampf(float(g[1]) + fl * (0.6 * sin(t * 7.0) + 0.4 * sin(t * 17.3) + 0.3 * sin(t * 2.1)), 0.0, 1.0)
	for a in _anims:
		var s: Sprite2D = a[0]
		var n := int(a[1])
		var f := int(_time * float(a[2]) + float(a[3])) % n
		s.frame = (n - 1 - f) if a[4] else f
	if _beam:
		_beam.modulate.a = 0.4 + 0.12 * sin(_time * 1.3)
