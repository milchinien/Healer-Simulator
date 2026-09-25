class_name UnitFigure
extends Node2D
## Figur auf dem Schlachtfeld: Pixel-Figur (Gruppe: CharacterView, Gegner: EnemyView), darunter
## HP-Balken und Buff-/Debuff-Symbole, darueber (Gegner) der Castbalken. Ursprung = Fusspunkt.

const SCALE := 2
const BAR_W := 34
const CLASS_COLORS := {
	"warrior": Color("c79c6e"), "paladin": Color("f58cba"), "mage": Color("69ccf0"), "warlock": Color("9482c9"),
	"hunter": Color("abd473"), "rogue": Color("fff569"), "druid": Color("ff7d0a"), "priest": Color("ffffff"),
}
const CAST_COLORS := {"": Color("e8b030"), "tank_buster": Color("ff5a2a"), "aoe": Color("b060ff")}

var unit: CombatUnit
var view: Node2D                # CharacterView oder EnemyView
var selected := false:
	set(v):
		selected = v
		queue_redraw()
var hovered := false:
	set(v):
		hovered = v
		queue_redraw()
var aggro_warning := false

var _body: Node2D               # Traeger fuer Ausfallschritt / Liegen
var _height := 72.0
var _width := 40.0
var _dead_shown := false
var _cast_label: Label
var _tween: Tween


func setup(u: CombatUnit, appearance: Dictionary = {}) -> void:
	unit = u
	_body = Node2D.new()
	add_child(_body)
	if u.side == "party":
		var cv := CharacterView.new()
		_body.add_child(cv)
		cv.set_appearance(appearance)
		cv.scale = Vector2(SCALE, SCALE)
		view = cv
		var fs := GameData.frame_size()
		_height = fs.y * SCALE - 8
		_width = 36
	else:
		var ev := EnemyView.new()
		ev.scale = Vector2(SCALE, SCALE)
		_body.add_child(ev)
		ev.setup(u.klass)
		view = ev
		_height = ev.frame_size.y * SCALE - 4
		_width = maxf(28.0, ev.frame_size.x * SCALE - 16)
	_cast_label = UI.label("", "", HORIZONTAL_ALIGNMENT_CENTER)
	_cast_label.theme = UiTheme.theme
	_cast_label.add_theme_color_override("font_color", Color("ffe6a0"))
	_cast_label.size = Vector2(140, 10)
	_cast_label.position = Vector2(-70, -_height - 22)
	_cast_label.visible = false
	add_child(_cast_label)
	queue_redraw()


## Rechteck fuer Mausklicks (lokal zum Schlachtfeld).
func hit_rect() -> Rect2:
	if unit and not unit.alive and unit.side == "party":
		return Rect2(position + Vector2(-_height / 2, -26), Vector2(_height, 30))
	return Rect2(position + Vector2(-_width / 2, -_height), Vector2(_width, _height + 12))


func head_pos() -> Vector2:
	return position + Vector2(0, -_height)


func center_pos() -> Vector2:
	return position + Vector2(0, -_height * 0.5)


func _process(_delta: float) -> void:
	if unit == null:
		return
	if not unit.alive and not _dead_shown:
		show_death()
	elif unit.alive and _dead_shown:
		show_alive()
	_update_cast()
	queue_redraw()


func _update_cast() -> void:
	if unit.side != "enemy":
		return
	var casting := unit.is_casting()
	_cast_label.visible = casting
	if casting:
		_cast_label.text = unit.cast.get("name", "")


# ---------------------------------------------------------------- Animationen
func play_attack(strong := false) -> void:
	if not unit.alive:
		return
	var dir := 1.0 if unit.side == "party" else -1.0
	if view is EnemyView and view.has_anim("attack"):
		view.play("attack")
	if _tween:
		_tween.kill()
	_tween = create_tween()
	var dist := (10.0 if strong else 6.0) * dir
	_tween.tween_property(_body, "position:x", dist, 0.08).set_ease(Tween.EASE_OUT)
	_tween.tween_property(_body, "position:x", 0.0, 0.16).set_ease(Tween.EASE_IN_OUT)


func play_hit(color := Color.WHITE) -> void:
	if not unit.alive:
		return
	if view is EnemyView:
		view.flash(color)
		if view.anim == view.base_anim and view.has_anim("hit") and view.base_anim == "idle":
			view.play("hit")
	elif view is CharacterView:
		view.flash(0.7)


func play_cast_start(anim_name := "cast") -> void:
	if view is EnemyView:
		view.set_base(anim_name if view.has_anim(anim_name) else "cast")
	elif view is CharacterView:
		view.play("cast")


func play_cast_end() -> void:
	if view is EnemyView and unit.alive:
		view.set_base("idle")


func play_spell() -> void:
	if view is CharacterView and unit.alive:
		view.play("cast")


func show_death() -> void:
	_dead_shown = true
	_cast_label.visible = false
	if view is EnemyView:
		view.set_base("dead")
		var tw := create_tween()
		tw.tween_property(view, "modulate", Color(0.75, 0.72, 0.8, 0.85), 0.6)
	else:
		# Gruppenfigur liegt am Boden
		if _tween:
			_tween.kill()
		_body.position = Vector2.ZERO
		var tw := create_tween()
		tw.tween_property(_body, "rotation", -PI / 2, 0.25).set_ease(Tween.EASE_IN)
		tw.parallel().tween_property(_body, "position", Vector2(-16, -2), 0.25)
		tw.parallel().tween_property(view, "modulate", Color(0.55, 0.52, 0.6), 0.4)


func show_alive() -> void:
	_dead_shown = false
	if view is EnemyView:
		view.set_base("idle")
		view.modulate = Color.WHITE
		return
	var tw := create_tween()
	tw.tween_property(_body, "rotation", 0.0, 0.3)
	tw.parallel().tween_property(_body, "position", Vector2.ZERO, 0.3)
	tw.parallel().tween_property(view, "modulate", Color.WHITE, 0.3)


# ---------------------------------------------------------------- Zeichnen
func _draw() -> void:
	if unit == null:
		return
	# Auswahlring unter den Fuessen
	if selected or hovered:
		var col := Color("ffd46b") if unit.side == "party" else Color("ff5040")
		if not selected:
			col.a = 0.45
		_ring(Vector2(0, 1), _width * 0.55, 4.0, col)
	if not unit.alive:
		return
	# HP-Balken
	var bw := BAR_W if unit.type in ["normal", "dummy"] else BAR_W + 12
	var x0 := -bw / 2.0
	var y0 := 6.0
	draw_rect(Rect2(x0 - 1, y0 - 1, bw + 2, 6), Color("120e18"))
	draw_rect(Rect2(x0, y0, bw, 4), Color("3a1a1e"))
	var fill := bw * unit.hp_frac()
	var hp_col := Color("4ad04a") if unit.side == "party" else Color("d83a2e")
	if unit.side == "enemy" and unit.type == "dummy":
		hp_col = Color("c8a060")
	draw_rect(Rect2(x0, y0, fill, 4), hp_col)
	draw_rect(Rect2(x0, y0, fill, 1), hp_col.lightened(0.35))
	if unit.type in ["elite", "boss"]:
		# Elite/Boss: goldene Ecken am Balken
		var gold := Color("ffd46b")
		draw_rect(Rect2(x0 - 2, y0 - 2, 3, 1), gold)
		draw_rect(Rect2(x0 - 2, y0 - 2, 1, 3), gold)
		draw_rect(Rect2(x0 + bw - 1, y0 - 2, 3, 1), gold)
		draw_rect(Rect2(x0 + bw + 1, y0 - 2, 1, 3), gold)
	# Buffs/Debuffs
	var ax := -((unit.auras.size() * 10) - 1) / 2.0
	for a in unit.auras:
		var tex := _aura_tex(str(a.get("icon", "")))
		if tex:
			draw_texture(tex, Vector2(ax, y0 + 7))
			if not a.get("permanent", false) and float(a.get("remaining", 0.0)) < 3.0:
				draw_rect(Rect2(ax, y0 + 7, 9, 9), Color(0, 0, 0, 0.35))
		ax += 10
	# Castbalken der Gegner ueber dem Kopf
	if unit.side == "enemy" and unit.is_casting():
		var cw := 48.0
		var cy := -_height - 10
		var prog := 1.0 - float(unit.cast["left"]) / maxf(0.01, float(unit.cast["total"]))
		var col: Color = CAST_COLORS.get(str(unit.cast["ability"].get("mechanic", "")), CAST_COLORS[""])
		draw_rect(Rect2(-cw / 2 - 1, cy - 1, cw + 2, 6), Color("120e18"))
		draw_rect(Rect2(-cw / 2, cy, cw, 4), Color("2a2230"))
		draw_rect(Rect2(-cw / 2, cy, cw * prog, 4), col)
		draw_rect(Rect2(-cw / 2, cy, cw * prog, 1), col.lightened(0.4))


func _ring(c: Vector2, rx: float, ry: float, col: Color) -> void:
	var pts := PackedVector2Array()
	for i in 33:
		var a := TAU * i / 32.0
		pts.append(c + Vector2(cos(a) * rx, sin(a) * ry).round())
	draw_polyline(pts, col, 1.0)


static var _aura_cache := {}


static func _aura_tex(icon: String) -> Texture2D:
	if icon == "":
		return null
	if not _aura_cache.has(icon):
		var path := "res://assets/gfx/combat/%s.png" % icon
		var original: Texture2D = load(path) if ResourceLoader.exists(path) else null
		var illustrated_path := "res://assets/gfx/icons_v2/%s.png" % icon
		if original != null and ResourceLoader.exists(illustrated_path):
			var illustrated: Texture2D = load(illustrated_path)
			var pixels := illustrated.get_image()
			# Auf Spielpixel reduzieren; Original-PNG und Alpha bleiben erhalten.
			var target := Vector2i(original.get_size())
			if icon.begins_with("spell_"):
				target = Vector2i(36, 36)
			pixels.resize(target.x, target.y, Image.INTERPOLATE_LANCZOS)
			_aura_cache[icon] = ImageTexture.create_from_image(pixels)
		else:
			_aura_cache[icon] = original
	return _aura_cache[icon]
