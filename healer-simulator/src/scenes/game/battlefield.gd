class_name Battlefield
extends Node2D
## Schlachtfeld (GDD Kapitel 3/7.2): Hintergrund der Welt, Figuren auf einer Bodenlinie
## (Gruppe links, Gegner rechts), schwebende Zahlen und kleine Zauber-Effekte.

const GROUND_Y := 226
## Position des Spielers (ganz hinten); Mitglieder siehe party_x()
const PARTY_X := [104]
const ENEMY_X := {
	1: [478], 2: [430, 530], 3: [410, 490, 572], 4: [398, 458, 520, 586], 5: [392, 440, 492, 544, 596],
}

var figures := {}              # CombatUnit -> UnitFigure
var _bg: Sprite2D
var _clouds: Array = []
var _clouds_speed := 0.0
var _lights: Array = []
var _fig_layer: Node2D
var _fx_layer: Node2D
var _text_layer: Node2D
var _bg_name := ""
var _t := 0.0

static var _bg_meta := {}


func _init() -> void:
	_bg = Sprite2D.new()
	_bg.centered = false
	add_child(_bg)
	_fig_layer = Node2D.new()
	_fig_layer.y_sort_enabled = false
	add_child(_fig_layer)
	_fx_layer = Node2D.new()
	add_child(_fx_layer)
	_text_layer = Node2D.new()
	add_child(_text_layer)


static func bg_meta() -> Dictionary:
	if _bg_meta.is_empty() and FileAccess.file_exists("res://data/battle_bg.json"):
		var f := FileAccess.open("res://data/battle_bg.json", FileAccess.READ)
		_bg_meta = JSON.parse_string(f.get_as_text())
	return _bg_meta


func set_background(bg_name: String) -> void:
	if bg_name == _bg_name:
		return
	_bg_name = bg_name
	var path := "res://assets/gfx/battle/%s.png" % bg_name
	_bg.texture = load(path) if ResourceLoader.exists(path) else null
	for c in _clouds:
		c.queue_free()
	_clouds.clear()
	for l in _lights:
		l.queue_free()
	_lights.clear()
	var m: Dictionary = bg_meta().get(bg_name, {})
	var cpath = m.get("clouds")
	if cpath is String and ResourceLoader.exists(cpath):
		var tex: Texture2D = load(cpath)
		for i in 2:
			var s := Sprite2D.new()
			s.texture = tex
			s.centered = false
			s.position = Vector2(i * tex.get_width(), float(m.get("clouds_y", 0)))
			add_child(s)
			move_child(s, 1)
			_clouds.append(s)
		_clouds_speed = float(m.get("clouds_speed", 2.0))
	for l in m.get("lights", []):
		var g := Sprite2D.new()
		g.texture = load("res://assets/gfx/fx/glow_small.png") if float(l.get("r", 8)) < 16 else load("res://assets/gfx/fx/glow_lamp.png")
		g.position = Vector2(float(l["x"]), float(l["y"]))
		g.modulate = Color(str(l.get("color", "#ffc070")))
		var mat := CanvasItemMaterial.new()
		mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
		g.material = mat
		g.set_meta("phase", randf() * TAU)
		add_child(g)
		move_child(g, 1 + _clouds.size())
		_lights.append(g)


# ---------------------------------------------------------------- Figuren
func clear_units(side: String) -> void:
	for u in figures.keys():
		if u.side == side:
			figures[u].queue_free()
			figures.erase(u)


func add_party(units: Array, appearances: Dictionary) -> void:
	clear_units("party")
	for u in units:
		var f := UnitFigure.new()
		_fig_layer.add_child(f)
		f.setup(u, appearances.get(u, {}))
		f.position = Vector2(party_x(u), GROUND_Y)
		figures[u] = f


## Spieler ganz hinten, Mitglieder nach Slot von vorne (Tank, hoechster Slot) nach hinten.
static func party_x(u: CombatUnit) -> float:
	if u.is_player:
		return PARTY_X[0]
	return 266.0 - 38.0 * (10 - u.slot)


func set_enemies(units: Array) -> void:
	clear_units("enemy")
	var xs: Array = ENEMY_X.get(clampi(units.size(), 1, 5), ENEMY_X[5])
	for i in units.size():
		var u: CombatUnit = units[i]
		var f := UnitFigure.new()
		_fig_layer.add_child(f)
		f.setup(u)
		var x: float = xs[mini(i, xs.size() - 1)]
		if u.type == "boss":
			x = 492
		f.position = Vector2(x, GROUND_Y)
		figures[u] = f
		# Auftauchen
		f.modulate.a = 0.0
		var tw := create_tween()
		tw.tween_interval(0.08 * i)
		tw.tween_property(f, "modulate:a", 1.0, 0.35)
	_sort_figures()


func _sort_figures() -> void:
	# Groessere Gegner hinten, damit kleine davor lesbar bleiben
	var list := _fig_layer.get_children()
	list.sort_custom(func(a, b): return a._height > b._height)
	for i in list.size():
		_fig_layer.move_child(list[i], i)


func figure_of(u: CombatUnit) -> UnitFigure:
	return figures.get(u)


## Figur unter der Mausposition (lokal), bevorzugt lebende.
func pick(pos: Vector2) -> CombatUnit:
	var best: CombatUnit = null
	var best_d := 1e9
	for u in figures:
		var f: UnitFigure = figures[u]
		if f.hit_rect().has_point(pos):
			var d := absf(f.position.x - pos.x) + (0.0 if u.alive else 100.0)
			if d < best_d:
				best_d = d
				best = u
	return best


# ---------------------------------------------------------------- Schwebende Zahlen und Effekte
func float_text(u: CombatUnit, text: String, color: Color, big := false, offset_y := 0.0) -> void:
	var f := figure_of(u)
	if f == null:
		return
	var l := Label.new()
	l.theme = UiTheme.theme      # unter Node2D wird das Theme nicht vererbt
	l.text = text
	l.add_theme_color_override("font_color", color)
	l.add_theme_color_override("font_shadow_color", Color(0.03, 0.02, 0.05, 0.95))
	if big:
		l.add_theme_font_override("font", UiTheme.font_title)
		l.add_theme_font_size_override("font_size", UiTheme.TITLE_SIZE)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.size = Vector2(120, 20)
	var start := f.head_pos() + Vector2(-60 + randf_range(-10, 10), -14 + offset_y)
	l.position = start.round()
	_text_layer.add_child(l)
	var rise := 22.0 if big else 16.0
	var tw := create_tween()
	if big:
		l.scale = Vector2(1, 1)
		l.pivot_offset = Vector2(60, 10)
	tw.tween_property(l, "position:y", start.y - rise, 0.9 if big else 0.75).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_QUAD)
	tw.parallel().tween_property(l, "modulate:a", 0.0, 0.35).set_delay(0.55 if big else 0.42)
	tw.tween_callback(l.queue_free)


## Kleine Lichtpartikel (Heilung: gold/gruen, Heilig-Schaden: gold, Schatten: violett).
func burst(u: CombatUnit, kind: String) -> void:
	var f := figure_of(u)
	if f == null:
		return
	var cols := {
		"heal": [Color("fff6c8"), Color("8ff08a"), Color("ffd46b")],
		"hot": [Color("b8f0a0"), Color("fff0a0")],
		"holy": [Color("fff6c8"), Color("ffd46b"), Color("ff9a3a")],
		"shadow": [Color("b070ff"), Color("5a2a9a"), Color("e0c0ff")],
		"hit": [Color("ffffff"), Color("ffd0a0")],
		"magic": [Color("ffb040"), Color("ff6a20")],
	}
	var palette: Array = cols.get(kind, cols["heal"])
	var n := 10 if kind in ["heal", "holy", "shadow"] else 6
	var dot: Texture2D = load("res://assets/gfx/fx/dot.png")
	for i in n:
		var s := Sprite2D.new()
		s.texture = dot
		s.modulate = palette[i % palette.size()]
		var mat := CanvasItemMaterial.new()
		mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
		s.material = mat
		var p := f.center_pos() + Vector2(randf_range(-f._width * 0.45, f._width * 0.45), randf_range(-f._height * 0.4, f._height * 0.35))
		s.position = p.round()
		_fx_layer.add_child(s)
		var tw := create_tween()
		var dy := -randf_range(10, 24) if kind != "shadow" else randf_range(-8, 8)
		tw.tween_property(s, "position", p + Vector2(randf_range(-4, 4), dy), randf_range(0.45, 0.8))
		tw.parallel().tween_property(s, "modulate:a", 0.0, 0.3).set_delay(0.3)
		tw.tween_callback(s.queue_free)
	if kind == "holy":
		# Heilige Pein: Lichtstrahl von oben
		var beam := Sprite2D.new()
		beam.texture = load("res://assets/gfx/fx/beam.png")
		beam.centered = false
		beam.position = Vector2(f.position.x - 20, f.position.y - 180)
		beam.modulate = Color(1, 0.9, 0.6, 0.0)
		var mat2 := CanvasItemMaterial.new()
		mat2.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
		beam.material = mat2
		_fx_layer.add_child(beam)
		var tw2 := create_tween()
		tw2.tween_property(beam, "modulate:a", 0.9, 0.06)
		tw2.tween_property(beam, "modulate:a", 0.0, 0.35)
		tw2.tween_callback(beam.queue_free)


## Level-Up: goldene Lichtsaeule, sich ausbreitender Lichtring und aufsteigende Funken.
func level_up_fx(u: CombatUnit) -> void:
	var f := figure_of(u)
	if f == null:
		return
	var add := CanvasItemMaterial.new()
	add.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	var beam := Sprite2D.new()
	beam.texture = load("res://assets/gfx/fx/beam.png")
	beam.centered = true
	beam.material = add
	beam.modulate = Color(1.0, 0.85, 0.4, 0.0)
	var bh: float = beam.texture.get_height()
	beam.position = Vector2(f.position.x, f.position.y - bh / 2.0 + 6)
	beam.scale = Vector2(0.3, 1.0)
	_fx_layer.add_child(beam)
	var tw := create_tween()
	tw.tween_property(beam, "modulate:a", 1.0, 0.12)
	tw.parallel().tween_property(beam, "scale:x", 1.4, 0.3).set_ease(Tween.EASE_OUT)
	tw.tween_interval(0.5)
	tw.tween_property(beam, "modulate:a", 0.0, 0.8)
	tw.parallel().tween_property(beam, "scale:x", 0.4, 0.8)
	tw.tween_callback(beam.queue_free)
	# Lichtring am Boden
	var ring := Sprite2D.new()
	ring.texture = load("res://assets/gfx/fx/glow_big.png")
	ring.material = add
	ring.position = f.position + Vector2(0, -4)
	ring.scale = Vector2(0.3, 0.12)
	ring.modulate = Color(1.0, 0.9, 0.5, 1.0)
	_fx_layer.add_child(ring)
	var tw2 := create_tween()
	tw2.tween_property(ring, "scale", Vector2(2.6, 0.9), 0.7).set_ease(Tween.EASE_OUT)
	tw2.parallel().tween_property(ring, "modulate:a", 0.0, 0.9)
	tw2.tween_callback(ring.queue_free)
	# Funken steigen in Wellen auf
	for wave in 3:
		get_tree().create_timer(0.15 * wave).timeout.connect(func(): burst(u, "holy"))
	f.play_spell()
	if f.view is CharacterView:
		f.view.flash(1.0)


func _process(delta: float) -> void:
	_t += delta
	for c in _clouds:
		c.position.x -= _clouds_speed * delta
		var w: float = c.texture.get_width()
		if c.position.x <= -w:
			c.position.x += w * 2
	for l in _lights:
		var ph: float = l.get_meta("phase")
		l.modulate.a = 0.55 + 0.25 * sin(_t * 3.1 + ph) + 0.1 * sin(_t * 7.3 + ph * 2.0)
