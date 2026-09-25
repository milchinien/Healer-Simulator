class_name UnitFrame
extends Control
## Rahmen im Gruppenfenster (GDD 7.2): Name in Klassenfarbe, Rollensymbol, HP-Balken mit
## eingehender Heilung (heller Vorschau-Balken) und Schild (weisse Ueberlagerung), Ressourcenbalken,
## Buffs/Debuffs, Aggro-Warnung (roter Rand) und Zielmarkierung. Klick = Ziel, Maus drueber = Mouseover.
## Goldenes Stufen-Abzeichen vor dem Namen und eine eigene EP-Linie.

signal clicked(unit: CombatUnit)
signal hovered(unit: CombatUnit, inside: bool)

const W := 96                  # Mindestbreite; bei wenigen Mitgliedern breiter (siehe fit_width)
const W_MAX := 150
const H := 40
const RES_COLORS := {"mana": Color("3a7ae8"), "rage": Color("d8322a"), "energy": Color("f0d040")}

var unit: CombatUnit
var selected := false
var aggro := false
var incoming := 0.0            # erwartete Heilung des laufenden Zaubers
var _lvl_flash := 0.0          # Aufleuchten beim Level-Up

var _name: Label
var _hp_text: Label
var _dead_text: Label
var _sb_normal: StyleBox
var _sb_target: StyleBox
var _sb_aggro: StyleBox
var _hover := false


var w := W


func _init(u: CombatUnit, width := W) -> void:
	unit = u
	w = width
	custom_minimum_size = Vector2(w, H)
	size = Vector2(w, H)
	mouse_filter = Control.MOUSE_FILTER_STOP
	mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	_sb_normal = _frame_box("unitframe")
	_sb_target = _frame_box("unitframe_target")
	_sb_aggro = _frame_box("unitframe_aggro")
	_name = UI.label(u.name)
	_name.position = Vector2(badge_width() + 5, 2)
	_name.size = Vector2(w - badge_width() - 16, 10)
	_name.clip_text = true
	_name.add_theme_color_override("font_color", UnitFigure.CLASS_COLORS.get(u.klass, Color.WHITE))
	add_child(_name)
	_hp_text = UI.label("", "", HORIZONTAL_ALIGNMENT_CENTER)
	_hp_text.position = Vector2(3, 11)
	_hp_text.size = Vector2(w - 6, 10)
	add_child(_hp_text)
	_dead_text = UI.label("FRAME_DEAD", "DimLabel", HORIZONTAL_ALIGNMENT_CENTER)
	_dead_text.position = Vector2(3, 11)
	_dead_text.size = Vector2(w - 6, 10)
	_dead_text.visible = false
	add_child(_dead_text)
	mouse_entered.connect(func():
		_hover = true
		hovered.emit(unit, true))
	mouse_exited.connect(func():
		_hover = false
		hovered.emit(unit, false))


func level() -> int:
	return int(unit.data.get("level", unit.level))


func badge_width() -> float:
	return 5.0 + UiTheme.font_body.get_string_size(str(level()), HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.BODY_SIZE).x


## Stufen-Abzeichen: Goldplakette mit dunkler Zahl (auch fuer Zielfenster usw.).
static func draw_level_badge(ci: CanvasItem, pos: Vector2, lvl: int) -> float:
	var txt := str(lvl)
	var tw := UiTheme.font_body.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.BODY_SIZE).x
	var r := Rect2(pos, Vector2(tw + 5, 10))
	ci.draw_rect(r.grow(1), Color("120e18"))
	ci.draw_rect(r, Color("c99a3a"))
	ci.draw_rect(Rect2(r.position, Vector2(r.size.x, 1)), Color("ffe08a"))
	ci.draw_rect(Rect2(r.position.x, r.end.y - 1, r.size.x, 1), Color("8a6424"))
	ci.draw_string(UiTheme.font_body, pos + Vector2(3, 9), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.BODY_SIZE, Color("2a1606"))
	return r.size.x


static func _frame_box(name: String) -> StyleBox:
	var path := "res://assets/gfx/combat/%s.png" % name
	if ResourceLoader.exists(path):
		var sb := StyleBoxTexture.new()
		sb.texture = load(path)
		for side in [SIDE_LEFT, SIDE_TOP, SIDE_RIGHT, SIDE_BOTTOM]:
			sb.set_texture_margin(side, 3)
		return sb
	var f := StyleBoxFlat.new()
	f.bg_color = Color("1d1626")
	f.border_color = {"unitframe": Color("6e5a3a"), "unitframe_target": Color("fff0c0"), "unitframe_aggro": Color("ff3a2a")}[name]
	f.set_border_width_all(1)
	return f


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		accept_event()
		clicked.emit(unit)


## Rahmen leuchtet beim Level-Up golden auf.
func flash_level_up() -> void:
	_lvl_flash = 1.6


func _process(delta: float) -> void:
	_lvl_flash = maxf(0.0, _lvl_flash - delta)
	var alive := unit.alive
	_dead_text.visible = not alive
	_hp_text.visible = alive
	if alive:
		_hp_text.text = "%d / %d" % [int(ceil(unit.hp)), int(unit.max_hp)]
	_name.modulate = Color(1, 1, 1, 1.0 if alive else 0.5)
	_name.position.x = badge_width() + 5
	_name.size.x = w - badge_width() - 16
	queue_redraw()


func _draw() -> void:
	var sb := _sb_normal
	if aggro and unit.alive:
		sb = _sb_aggro
	if selected:
		sb = _sb_target
	draw_style_box(sb, Rect2(Vector2.ZERO, size))
	Hud.corner_studs(self, Rect2(Vector2.ZERO, size))
	if _hover:
		draw_rect(Rect2(2, 2, w - 4, H - 4), Color(1, 1, 1, 0.06))
	# Rollensymbol
	var role_tex := UnitFigure._aura_tex("role_%s" % unit.role)
	if role_tex:
		draw_texture(role_tex, Vector2(w - 11, 3))
	# HP-Balken
	var bx := 3.0
	var by := 11.0
	var bw := float(w - 6)
	draw_rect(Rect2(bx, by, bw, 10), Color("120e18"))
	if unit.alive:
		var frac := unit.hp_frac()
		var fill := bw * frac
		var hp_col := Color("3cb43c") if frac > 0.35 else (Color("d8b030") if frac > 0.2 else Color("d8402e"))
		draw_rect(Rect2(bx, by, fill, 10), hp_col.darkened(0.25))
		draw_rect(Rect2(bx, by, fill, 5), hp_col)
		draw_rect(Rect2(bx, by, fill, 1), hp_col.lightened(0.4))
		# eingehende Heilung
		if incoming > 0.0:
			var inc := minf(bw - fill, bw * incoming / unit.max_hp)
			draw_rect(Rect2(bx + fill, by, inc, 10), Color(0.55, 1.0, 0.55, 0.45))
		# Schild
		var absorb := 0.0
		for a in unit.auras:
			absorb += float(a.get("absorb", 0.0))
		if absorb > 0.0:
			var sw := minf(bw, bw * absorb / unit.max_hp)
			draw_rect(Rect2(bx + minf(fill, bw - sw), by, sw, 10), Color(1, 1, 1, 0.55))
	else:
		draw_rect(Rect2(bx, by, bw, 10), Color("2a2430"))
	# Ressource
	var ry := 22.0
	draw_rect(Rect2(bx, ry, bw, 2), Color("120e18"))
	if unit.alive and unit.res_max > 0.0:
		draw_rect(Rect2(bx, ry, bw * unit.res_frac(), 2), RES_COLORS.get(unit.resource, Color.GRAY))
	# EP-Linie (violett; EP der laufenden Welle hell)
	var d: Dictionary = unit.data
	var need := float(CombatData.xp_to_next(level()))
	var xf := clampf(float(d.get("xp", 0)) / need, 0.0, 1.0)
	draw_rect(Rect2(bx, 25, bw, 2), Color("120e18"))
	draw_rect(Rect2(bx, 25, roundf(bw * xf), 2), XpBar.XP)
	# Stufen-Abzeichen
	draw_level_badge(self, Vector2(3, 1), level())
	# Level-Up: goldenes Aufleuchten mit pulsierendem Rand
	if _lvl_flash > 0.0:
		var a := minf(1.0, _lvl_flash) * (0.6 + 0.4 * sin(_lvl_flash * 18.0))
		draw_rect(Rect2(Vector2.ZERO, size), Color(1.0, 0.85, 0.35, a * 0.45))
		draw_rect(Rect2(Vector2.ZERO, size), Color(1.0, 0.95, 0.6, a), false, 2.0)
	# Buffs/Debuffs
	var ax := 3.0
	for a in unit.auras:
		var tex := UnitFigure._aura_tex(str(a.get("icon", "")))
		if tex:
			draw_texture(tex, Vector2(ax, 28))
			ax += 10
			if ax > w - 10:
				break
