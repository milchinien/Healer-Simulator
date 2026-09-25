class_name TargetFrame
extends Control
## Zielfenster (GDD 7.2 [Festlegung]): aktuelles freundliches bzw. feindliches Ziel mit Name,
## Level (bei Gegnern farbig wie WoW), HP und Buffs/Debuffs.

var unit: CombatUnit
var viewer_level := 1
var hostile := false

var _name: Label
var _level: Label
var _hp: Label
var _sb: StyleBox


func _init(is_hostile: bool, width := 172) -> void:
	hostile = is_hostile
	custom_minimum_size = Vector2(width, 34)
	size = custom_minimum_size
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_sb = UnitFrame._frame_box("unitframe")
	_name = UI.label("")
	_name.position = Vector2(4, 1)
	_name.size = Vector2(width - 30, 10)
	_name.clip_text = true
	add_child(_name)
	_hp = UI.label("", "", HORIZONTAL_ALIGNMENT_CENTER)
	_hp.position = Vector2(3, 12)
	_hp.size = Vector2(width - 6, 10)
	add_child(_hp)
	# Level rechts in der Namenszeile (bei Gegnern farbig wie WoW)
	_level = UI.label("", "", HORIZONTAL_ALIGNMENT_RIGHT)
	_level.position = Vector2(width - 28, 1)
	_level.size = Vector2(24, 10)
	add_child(_level)
	visible = false


func show_unit(u: CombatUnit, own_level: int) -> void:
	unit = u
	viewer_level = own_level
	visible = u != null
	if u == null:
		return
	_name.text = u.name
	_level.text = str(u.level) if u.type != "boss" else "??"
	if u.side == "enemy":
		_level.add_theme_color_override("font_color", CombatData.level_color(own_level, u.level))
		var elite := u.type in ["elite", "boss"]
		_name.add_theme_color_override("font_color", Color("ffd46b") if elite else Color("f4e9cf"))
	else:
		_level.text = ""
		_name.add_theme_color_override("font_color", UnitFigure.CLASS_COLORS.get(u.klass, Color.WHITE))


func _process(_delta: float) -> void:
	if unit == null:
		return
	if unit.alive:
		_hp.text = "%d / %d" % [int(ceil(unit.hp)), int(unit.max_hp)] if unit.type != "dummy" else ""
	else:
		_hp.text = tr("FRAME_DEAD")
	queue_redraw()


func _draw() -> void:
	if unit == null:
		return
	draw_style_box(_sb, Rect2(Vector2.ZERO, size))
	Hud.corner_studs(self, Rect2(Vector2.ZERO, size))
	if unit.side == "party":
		# Gruppenmitglieder: Stufe als goldenes Abzeichen
		var lvl := int(unit.data.get("level", unit.level))
		var bw_ := UiTheme.font_body.get_string_size(str(lvl), HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.BODY_SIZE).x + 5
		UnitFrame.draw_level_badge(self, Vector2(size.x - bw_ - 3, 1), lvl)
	var bw := size.x - 6
	var col := Hud.HP_ENEMY if unit.side == "enemy" else Hud.HP
	if unit.type == "dummy":
		col = Color("c8a060")
	Hud.bar(self, Rect2(3, 12, bw, 10), unit.hp_frac() if unit.alive else 0.0, col)
	if unit.res_max > 0.0:
		Hud.bar(self, Rect2(3, 24, bw, 2), unit.res_frac() if unit.alive else 0.0, Hud.res_color(unit))
	var ax := size.x - 3
	for i in range(unit.auras.size() - 1, -1, -1):
		var tex := Hud.combat_tex(str(unit.auras[i].get("icon", "")))
		if tex:
			ax -= 10
			draw_texture(tex, Vector2(ax, 24 if unit.res_max <= 0.0 else 26) + Vector2(0, -1))
