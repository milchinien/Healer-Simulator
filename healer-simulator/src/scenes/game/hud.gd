class_name Hud
extends RefCounted
## Gemeinsame Zeichenhilfen fuer Balken und Rahmen des Hauptbildschirms.

const OUTLINE := Color("120e18")
const BAR_BG := Color("2a2230")
const HP := Color("3cb43c")
const HP_ENEMY := Color("c8342a")
const MANA := Color("3a7ae8")
const RAGE := Color("d8322a")
const CAST := Color("e8b030")


## Balken mit Kontur, dunklem Grund, zweistufiger Fuellung und Glanzlinie.
static func bar(ci: CanvasItem, r: Rect2, frac: float, col: Color, bg := BAR_BG) -> void:
	ci.draw_rect(r.grow(1), OUTLINE)
	ci.draw_rect(r, bg)
	var w := roundf(r.size.x * clampf(frac, 0.0, 1.0))
	if w <= 0.0:
		return
	ci.draw_rect(Rect2(r.position, Vector2(w, r.size.y)), col.darkened(0.22))
	ci.draw_rect(Rect2(r.position, Vector2(w, ceilf(r.size.y * 0.5))), col)
	ci.draw_rect(Rect2(r.position, Vector2(w, 1)), col.lightened(0.4))


static func res_color(u: CombatUnit) -> Color:
	return RAGE if u.resource == "rage" else MANA


## Dunkle, halbtransparente Flaeche mit goldener Kante (Leisten).
static func strip(ci: CanvasItem, r: Rect2, top_line := false, bottom_line := false, alpha := 0.86) -> void:
	ci.draw_rect(r, Color(0.05, 0.035, 0.08, alpha))
	if top_line:
		ci.draw_rect(Rect2(r.position.x, r.position.y, r.size.x, 1), UiTheme.GOLD_DIM)
		ci.draw_rect(Rect2(r.position.x, r.position.y + 1, r.size.x, 1), Color(0, 0, 0, 0.5))
	if bottom_line:
		ci.draw_rect(Rect2(r.position.x, r.end.y - 1, r.size.x, 1), UiTheme.GOLD_DIM)


static func format_time(s: float) -> String:
	var txt := "%.1f" % maxf(0.0, s)
	return txt.replace(".", ",") if TranslationServer.get_locale().begins_with("de") else txt


static func combat_tex(name: String) -> Texture2D:
	return UnitFigure._aura_tex(name)


## Text mit Schatten direkt zeichnen (pixelgenau auf eine Grundlinie gesetzt).
static func text(ci: CanvasItem, baseline: Vector2, s: String, col: Color) -> void:
	ci.draw_string(UiTheme.font_body, baseline + Vector2(1, 1), s, HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.BODY_SIZE, UiTheme.SHADOW)
	ci.draw_string(UiTheme.font_body, baseline, s, HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.BODY_SIZE, col)


## Goldene Eckbeschlaege (passend zur gravierten unteren Leiste).
static func corner_studs(ci: CanvasItem, r: Rect2) -> void:
	var g := Color("c99a3a")
	var gl := Color("ffe08a")
	var gd := Color("8a6424")
	for p in [r.position, Vector2(r.end.x - 3, r.position.y), Vector2(r.position.x, r.end.y - 3), r.end - Vector2(3, 3)]:
		ci.draw_rect(Rect2(p, Vector2(3, 3)), g)
		ci.draw_rect(Rect2(p, Vector2(1, 1)), gl)
		ci.draw_rect(Rect2(p + Vector2(2, 2), Vector2(1, 1)), gd)
