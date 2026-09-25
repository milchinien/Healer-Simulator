class_name BossFrame
extends Control
## Grosser Boss-HP-Balken mit Castbalken (oben rechts, nur in Bosswellen).

var unit: CombatUnit
var _name: Label
var _pct: Label
var _cast: CastBar


func _init() -> void:
	custom_minimum_size = Vector2(212, 40)
	size = custom_minimum_size
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_name = UI.label("", "GoldLabel", HORIZONTAL_ALIGNMENT_LEFT)
	_name.position = Vector2(2, 0)
	_name.size = Vector2(160, 10)
	add_child(_name)
	_pct = UI.label("", "", HORIZONTAL_ALIGNMENT_RIGHT)
	_pct.position = Vector2(150, 12)
	_pct.size = Vector2(58, 10)
	add_child(_pct)
	_cast = CastBar.new(208, 11)
	_cast.position = Vector2(2, 27)
	add_child(_cast)
	visible = false


func show_unit(u: CombatUnit) -> void:
	unit = u
	visible = u != null
	_cast.unit = u
	if u:
		_name.text = u.name


func _process(_delta: float) -> void:
	if unit == null:
		return
	_pct.text = "%d %%" % int(ceil(unit.hp_frac() * 100.0))
	queue_redraw()


func _draw() -> void:
	if unit == null:
		return
	Hud.bar(self, Rect2(2, 12, 208, 11), unit.hp_frac(), Hud.HP_ENEMY)
	# Phasengrenze markieren
	for p in unit.data.get("phases", []):
		var x := 2 + roundf(208 * float(p))
		draw_rect(Rect2(x, 11, 1, 13), Color("ffd46b"))
