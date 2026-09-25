class_name SpellInfo
extends RefCounted
## Gemeinsame Zauber-Tooltips (Aktionsleiste, Zauberbuch, Lehrmeister).


## Tooltip-Text (BBCode) fuer einen Zauberrang. u = Spieler (fuer Heilstaerke/Schaden), darf null sein.
static func tooltip(id: String, rank: int, u: CombatUnit, extra := "") -> String:
	var sp := CombatData.spell(id)
	var rd := CombatData.rank_data(id, maxi(1, rank))
	if rd.is_empty():
		return ""
	var lines: Array = []
	lines.append("[color=#ffd46b]%s[/color]  [color=#9a90a8]%s[/color]" % [TranslationServer.translate("SPELL_%s" % id.to_upper()), Loc.t("SPELL_RANK", {"r": maxi(1, rank)})])
	var ct := float(sp.get("cast", 0.0))
	var cast_txt: String = TranslationServer.translate("SPELL_INSTANT") if ct <= 0.0 else Loc.t("SPELL_CAST_TIME", {"s": num(ct)})
	lines.append("%s    %s" % [Loc.t("SPELL_MANA", {"m": int(rd.get("mana", 0))}), cast_txt])
	var power := 0.0
	if u:
		power = u.stat("heal_power") if sp.get("kind") in ["heal", "hot"] else u.stat("damage")
	var coef := float(sp.get("coef", 0.0))
	var args := {}
	match str(sp.get("kind", "")):
		"heal", "damage":
			args = {"min": int(rd["min"] + power * coef), "max": int(rd["max"] + power * coef)}
		"hot", "dot":
			args = {"total": int(rd["total"] + power * coef), "s": int(sp["duration"])}
	lines.append(Loc.t("SPELL_DESC_%s" % id.to_upper(), args))
	if extra != "":
		lines.append(extra)
	return "\n".join(lines)


static func num(v: float) -> String:
	return str(v).replace(".", ",") if TranslationServer.get_locale().begins_with("de") else str(v)


## Tooltip-Fenster mit BBCode (fuer _make_custom_tooltip).
static func make_tooltip(text: String, width := 160) -> Control:
	if text == "":
		return null
	var l := RichTextLabel.new()
	l.bbcode_enabled = true
	l.fit_content = true
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size = Vector2(width, 0)
	l.text = text
	return l


## Kleines Zieh-Vorschaubild eines Zaubers.
static func drag_preview(id: String) -> Control:
	var t := TextureRect.new()
	t.texture = UnitFigure._aura_tex(str(CombatData.spell(id).get("icon", "")))
	t.custom_minimum_size = Vector2(36, 36)
	t.size = Vector2(36, 36)
	t.stretch_mode = TextureRect.STRETCH_SCALE
	t.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	t.modulate = Color(1, 1, 1, 0.85)
	t.position = Vector2(-18, -18)
	var c := Control.new()
	c.add_child(t)
	return c
