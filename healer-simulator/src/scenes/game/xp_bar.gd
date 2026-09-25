class_name XpBar
extends Control
## EP-Leiste des Spielers (zwischen Kampfszene und Gruppenfenster), 20 Segmente wie WoW.
## EP werden sofort gutgeschrieben (jeder Kill, jede Quest); neue EP laufen sichtbar in die Leiste.
## Text: Stufe und EP.

const XP := Color("8a4ae0")
const XP_PENDING := Color("d8b0ff")
const SEGMENTS := 20

var character: Dictionary
var _shown := -1.0             # angezeigter Fuellstand (laeuft dem echten Wert nach)
var _shown_level := 0
var _flash := 0.0
var _t := 0.0


func _init(width: float, height: float) -> void:
	custom_minimum_size = Vector2(width, height)
	size = custom_minimum_size
	mouse_filter = Control.MOUSE_FILTER_STOP


## Kurzes Aufleuchten (Level-Up).
func flash() -> void:
	_flash = 1.2


func _process(delta: float) -> void:
	_t += delta
	_flash = maxf(0.0, _flash - delta)
	# angezeigter Stand laeuft dem echten nach (Fuellen sichtbar)
	var lvl_now := int(character.get("level", 1))
	var real := clampf(float(character.get("xp", 0)) / CombatData.xp_to_next(lvl_now), 0.0, 1.0)
	if _shown >= 0.0 and _shown_level == lvl_now and _shown < real:
		_shown = minf(real, _shown + delta * 0.6)
	var lvl := int(character.get("level", 1))
	var need := CombatData.xp_to_next(lvl)
	var tip := Loc.t("XP_BAR_TIP", {"level": lvl, "xp": int(character.get("xp", 0)), "need": need,
		"rest": maxi(0, need - int(character.get("xp", 0)))})
	# gewaehlte Segen zusammengefasst
	var lines: Array = []
	for target in ["player", "group"]:
		var m := CombatData.boon_mults(character, target)
		for st in m:
			lines.append("%s%s +%s %%" % [tr("STAT_%s" % st.to_upper()), " (" + tr("BOON_TARGET_GROUP") + ")" if target == "group" else "",
				str(snappedf(m[st] * 100.0, 0.1)).trim_suffix(".0")])
	if not lines.is_empty():
		tip += "

" + tr("XP_BAR_BOONS") + "
" + "
".join(lines)
	tooltip_text = tip
	queue_redraw()


func _draw() -> void:
	var lvl := int(character.get("level", 1))
	var max_level := int(CombatData.g("max_level", 60))
	var need := float(CombatData.xp_to_next(lvl))
	var xp := float(character.get("xp", 0))
	var w := size.x
	var h := size.y
	var target := 1.0 if lvl >= max_level else clampf(xp / need, 0.0, 1.0)
	# neue EP: heller Abschnitt zwischen angezeigtem und echtem Stand, der sich fuellt
	if _shown > target + 0.001 or _shown_level != lvl or _shown < 0.0:
		_shown = 0.0 if _shown >= 0.0 and _shown_level != lvl else target
		_shown_level = lvl
	var f_done := _shown
	if target > f_done:
		draw_rect(Rect2(roundf(w * f_done), 1, roundf(w * (target - f_done)), h - 1), Color(XP_PENDING, 0.8))
	var fw := roundf(w * f_done)
	if fw > 0:
		draw_rect(Rect2(0, 1, fw, h - 1), XP.darkened(0.2))
		draw_rect(Rect2(0, 1, fw, ceilf((h - 1) * 0.5)), XP)
		draw_rect(Rect2(0, 1, fw, 1), XP.lightened(0.45))
	if _flash > 0.0:
		draw_rect(Rect2(0, 1, w, h - 1), Color(1, 0.95, 0.7, _flash * 0.5))
	# 20 Segmente
	for i in range(1, SEGMENTS):
		var x := roundf(w * i / SEGMENTS)
		draw_rect(Rect2(x, 1, 1, h - 1), Color(0.03, 0.02, 0.06, 0.8))
	# Text: Stufe links, EP mittig
	var lvl_txt := Loc.t("XP_BAR_LEVEL", {"level": lvl})
	var font := UiTheme.font_body
	var base := h - 0.0
	Hud.text(self, Vector2(4, base), lvl_txt, UiTheme.GOLD)
	var mid: String
	if lvl >= max_level:
		mid = tr("XP_BAR_MAX")
	else:
		mid = Loc.t("XP_BAR_TEXT", {"xp": int(xp), "need": int(need)})
	var mw := font.get_string_size(mid, HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.BODY_SIZE).x
	Hud.text(self, Vector2(roundf((w - mw) / 2.0), base), mid, UiTheme.WHITE)
