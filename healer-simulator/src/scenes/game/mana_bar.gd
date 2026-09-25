class_name ManaBar
extends Control
## Grosse Mana-Leiste des Spielers ueber der Aktionsleiste (die HP stehen im Gruppenfenster).
## Tooltip: Stufe und Erfahrung.

var unit: CombatUnit
var character: Dictionary

var _text: Label


func _init(width: float, height := 11.0) -> void:
	custom_minimum_size = Vector2(width, height)
	size = custom_minimum_size
	mouse_filter = Control.MOUSE_FILTER_STOP
	_text = UI.label("", "", HORIZONTAL_ALIGNMENT_CENTER)
	_text.position = Vector2(0, floorf((height - 10.0) / 2.0))
	_text.size = Vector2(width, 10)
	add_child(_text)


func _process(_delta: float) -> void:
	if unit == null:
		return
	_text.text = Loc.t("MANA_BAR", {"mana": int(unit.res), "max": int(unit.res_max)})
	tooltip_text = Loc.t("FRAME_XP_TOOLTIP", {"level": unit.level, "xp": int(character.get("xp", 0)),
		"need": CombatData.xp_to_next(int(character.get("level", 1)))})
	queue_redraw()


func _draw() -> void:
	if unit == null:
		return
	Hud.bar(self, Rect2(Vector2.ZERO, size), unit.res_frac() if unit.alive else 0.0, Hud.MANA)
