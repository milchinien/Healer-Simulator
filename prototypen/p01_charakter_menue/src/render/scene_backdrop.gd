class_name SceneBackdrop
extends Control
## Lebendiger Hintergrund aus den vorgerenderten Ebenen (assets/gfx/bg/<szene>_<ebene>.png)
## plus Effekte aus data/scenes.json: ziehende Wolken, flackernde Lichter, Feuer, Partikel.

const ADD_MAT := preload("res://src/render/additive.tres")

## Partikel-Stimmung je Szene
const AMBIENCE := {
	"title": ["fireflies", "stars_twinkle"],
	"charselect": ["motes"],
	"human_city": ["leaves"],
	"dwarf_hall": ["embers"],
	"orc_steppe": ["dust"],
	"gnome_workshop": ["motes_teal"],
	"loading_gruenhain": ["fireflies_day"],
}

var scene_name := ""
var meta := {}
var _clouds: Array[Sprite2D] = []
var _cloud_speed := 3.0
var _glows: Array = []   # [Sprite2D, basis_alpha, phase, speed]
var _fires: Array[Sprite2D] = []
var _fire_t := 0.0
var _time := 0.0
var _beam: Sprite2D

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
	_fires.clear()
	_beam = null
	scene_name = name
	meta = scene_meta(name)
	var layers: Array = meta.get("layers", ["bg"])
	_add_layer("bg")
	if "clouds" in layers:
		for i in 2:
			var s := _add_layer("clouds")
			s.position.x = i * 640
			_clouds.append(s)
	if name == "title":
		_add_beam(meta.get("beam", [320, 180]))
	for p in meta.get("lights", []):
		_add_glow(Vector2(p[0], p[1]), _glow_tex_for(name), 0.75)
	for p in meta.get("fires", []):
		_add_fire(Vector2(p[0], p[1]))
	if "fg" in layers:
		_add_layer("fg")
	for kind in AMBIENCE.get(name, []):
		_add_particles(kind)


func _glow_tex_for(name: String) -> Texture2D:
	match name:
		"gnome_workshop":
			return load("res://assets/gfx/fx/glow_warm.png")
		"title":
			return load("res://assets/gfx/fx/glow_warm.png")
		_:
			return load("res://assets/gfx/fx/glow_warm.png")


func _add_layer(layer: String) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = load("res://assets/gfx/bg/%s_%s.png" % [scene_name, layer])
	s.centered = false
	add_child(s)
	return s


func _add_glow(pos: Vector2, texture: Texture2D, base_alpha: float) -> Sprite2D:
	var g := Sprite2D.new()
	g.texture = texture
	g.position = pos
	g.material = ADD_MAT
	g.modulate.a = base_alpha
	add_child(g)
	_glows.append([g, base_alpha, randf() * TAU, randf_range(0.7, 1.3)])
	return g


func _add_fire(pos: Vector2) -> void:
	_add_glow(pos + Vector2(0, -6), load("res://assets/gfx/fx/glow_big.png"), 0.6)
	var f := Sprite2D.new()
	f.texture = load("res://assets/gfx/fx/fire.png")
	f.hframes = 6
	f.centered = false
	f.position = pos + Vector2(-7, -19)
	add_child(f)
	_fires.append(f)
	var embers := _make_particles("embers_fire")
	embers.position = pos + Vector2(0, -10)
	add_child(embers)


func _add_beam(p: Array) -> void:
	_beam = Sprite2D.new()
	_beam.texture = load("res://assets/gfx/fx/beam.png")
	_beam.centered = false
	_beam.position = Vector2(p[0] - 20, p[1] - 180)
	_beam.material = ADD_MAT
	_beam.modulate.a = 0.5
	add_child(_beam)
	_add_glow(Vector2(p[0], p[1]), load("res://assets/gfx/fx/glow_warm.png"), 0.9)


func _add_particles(kind: String) -> void:
	var p := _make_particles(kind)
	if p:
		add_child(p)


func _make_particles(kind: String) -> CPUParticles2D:
	var p := CPUParticles2D.new()
	p.texture = load("res://assets/gfx/fx/dot.png")
	p.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
	p.local_coords = false
	var grad := Gradient.new()
	match kind:
		"fireflies", "fireflies_day":
			p.amount = 22 if kind == "fireflies" else 12
			p.lifetime = 6.0
			p.position = Vector2(320, 300)
			p.emission_rect_extents = Vector2(320, 50)
			p.gravity = Vector2(0, -2)
			p.initial_velocity_min = 2
			p.initial_velocity_max = 8
			p.spread = 180
			p.direction = Vector2(0, -1)
			var c := Color("f4ff9a") if kind == "fireflies" else Color("ffffff")
			grad.colors = PackedColorArray([Color(c, 0), Color(c, 1), Color(c, 0.2), Color(c, 1), Color(c, 0)])
			grad.offsets = PackedFloat32Array([0, 0.2, 0.5, 0.75, 1])
			p.preprocess = 6.0
		"stars_twinkle":
			p.amount = 10
			p.lifetime = 2.5
			p.position = Vector2(320, 90)
			p.emission_rect_extents = Vector2(320, 90)
			p.gravity = Vector2.ZERO
			p.initial_velocity_min = 0
			p.initial_velocity_max = 0
			p.texture = load("res://assets/gfx/fx/sparkle.png")
			grad.colors = PackedColorArray([Color(1, 1, 1, 0), Color(0.85, 0.9, 1, 0.9), Color(1, 1, 1, 0)])
			p.preprocess = 3.0
		"motes", "motes_teal":
			p.amount = 16
			p.lifetime = 7.0
			p.position = Vector2(230, 250)
			p.emission_rect_extents = Vector2(220, 90)
			p.gravity = Vector2(0, -1.5)
			p.initial_velocity_min = 1
			p.initial_velocity_max = 5
			p.spread = 180
			var c2 := Color("ffd9a0") if kind == "motes" else Color("9af0e6")
			grad.colors = PackedColorArray([Color(c2, 0), Color(c2, 0.7), Color(c2, 0)])
			p.preprocess = 7.0
			if kind == "motes_teal":
				p.position = Vector2(320, 200)
				p.emission_rect_extents = Vector2(320, 150)
		"leaves":
			p.amount = 10
			p.lifetime = 8.0
			p.position = Vector2(320, -10)
			p.emission_rect_extents = Vector2(340, 4)
			p.gravity = Vector2(4, 9)
			p.initial_velocity_min = 4
			p.initial_velocity_max = 10
			p.direction = Vector2(1, 0.3)
			grad.colors = PackedColorArray([Color("78b85a"), Color("a8d070"), Color(0.5, 0.7, 0.3, 0)])
			p.preprocess = 8.0
		"embers":
			p.amount = 26
			p.lifetime = 4.0
			p.position = Vector2(320, 250)
			p.emission_rect_extents = Vector2(70, 6)
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
			p.emission_rect_extents = Vector2(4, 2)
			p.gravity = Vector2(0, -18)
			p.initial_velocity_min = 4
			p.initial_velocity_max = 10
			p.direction = Vector2(0, -1)
			p.spread = 30
			grad.colors = PackedColorArray([Color("fff0a0"), Color("ff7a2a"), Color(0.6, 0.1, 0.05, 0)])
			p.preprocess = 2.0
			p.position = Vector2(236, 270)
		"dust":
			p.amount = 14
			p.lifetime = 6.0
			p.position = Vector2(-10, 280)
			p.emission_rect_extents = Vector2(4, 60)
			p.gravity = Vector2(10, 0)
			p.initial_velocity_min = 40
			p.initial_velocity_max = 90
			p.direction = Vector2(1, -0.05)
			p.spread = 6
			grad.colors = PackedColorArray([Color(0.95, 0.75, 0.5, 0), Color(0.95, 0.75, 0.5, 0.5), Color(0.95, 0.75, 0.5, 0)])
			p.preprocess = 6.0
		_:
			return null
	p.color_ramp = grad
	return p


func _process(delta: float) -> void:
	_time += delta
	for s in _clouds:
		s.position.x -= _cloud_speed * delta
		if s.position.x <= -640:
			s.position.x += 1280
	for g in _glows:
		var spr: Sprite2D = g[0]
		var t: float = _time * float(g[3]) + float(g[2])
		spr.modulate.a = clampf(float(g[1]) + 0.08 * sin(t * 7.0) + 0.05 * sin(t * 17.3) + 0.04 * sin(t * 2.1), 0.0, 1.0)
	_fire_t += delta
	var fire_frame := int(_fire_t * 10.0) % 6
	for f in _fires:
		f.frame = fire_frame
	if _beam:
		_beam.modulate.a = 0.4 + 0.12 * sin(_time * 1.3)
