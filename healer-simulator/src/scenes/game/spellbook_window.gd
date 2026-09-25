class_name SpellbookWindow
extends GameWindow
## Zauberbuch (GDD 13.2): Reiter "Allgemein" und Reiter der Spezialisierung (ab Stufe 10, noch gesperrt).
## Jeder Eintrag: Symbol, Name, hoechster gelernter Rang, Tooltip. Zauber per Drag & Drop auf die Aktionsleiste.

var character: Dictionary
var player: CombatUnit
var _grid: GridContainer
var _empty: Label


func _init(c: Dictionary, p: CombatUnit) -> void:
	super("spellbook", "SPELLBOOK_TITLE", Rect2(48, 22, 300, 214))
	character = c
	player = p
	var tabs := TabBar.new()
	tabs.focus_mode = Control.FOCUS_NONE
	tabs.add_tab("SPELLBOOK_TAB_GENERAL")
	tabs.add_tab("SPELLBOOK_TAB_SPEC")
	tabs.set_tab_disabled(1, str(c.get("spec", "")) == "")
	tabs.set_tab_tooltip(1, "SPELLBOOK_SPEC_LOCKED")
	body.add_child(tabs)
	var page := UI.panel("PlainPanel")
	page.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.add_child(page)
	var v := UI.vbox(4)
	page.add_child(v)
	_grid = GridContainer.new()
	_grid.columns = 1
	_grid.add_theme_constant_override("h_separation", 6)
	_grid.add_theme_constant_override("v_separation", 3)
	v.add_child(_grid)
	_empty = UI.label("", "DimLabel", HORIZONTAL_ALIGNMENT_CENTER)
	v.add_child(_empty)
	body.add_child(UI.label("SPELLBOOK_HINT", "HintLabel", HORIZONTAL_ALIGNMENT_CENTER))
	refresh()


func refresh() -> void:
	for ch in _grid.get_children():
		ch.queue_free()
	var n := 0
	for id in CombatData.bal()["spell_order"]:
		var rank := CombatData.learned_rank(character, id)
		if rank > 0:
			_grid.add_child(SpellEntry.new(id, rank, player))
			n += 1
	_empty.text = "" if n > 0 else "SPELLBOOK_EMPTY"


## Ein Zauber im Buch; wird per Drag & Drop auf die Aktionsleiste gezogen.
class SpellEntry extends Control:
	var id := ""
	var rank := 1
	var _p: CombatUnit
	var _icon: Texture2D
	var _hover := false

	func _init(spell_id: String, r: int, p: CombatUnit) -> void:
		id = spell_id
		rank = r
		_p = p
		custom_minimum_size = Vector2(250, 24)
		mouse_filter = Control.MOUSE_FILTER_STOP
		mouse_default_cursor_shape = Control.CURSOR_DRAG
		tooltip_text = "x"
		_icon = UnitFigure._aura_tex(str(CombatData.spell(id).get("icon", "")))
		mouse_entered.connect(func():
			_hover = true
			queue_redraw())
		mouse_exited.connect(func():
			_hover = false
			queue_redraw())

	func _make_custom_tooltip(_for_text: String) -> Object:
		return SpellInfo.make_tooltip(SpellInfo.tooltip(id, rank, _p, "[color=#9a90a8]%s[/color]" % TranslationServer.translate("SPELLBOOK_DRAG_TIP")))

	func _get_drag_data(_at_position: Vector2) -> Variant:
		set_drag_preview(SpellInfo.drag_preview(id))
		Sfx.play("ui_select")
		return {"spell": id}

	func _draw() -> void:
		if _hover:
			draw_rect(Rect2(Vector2.ZERO, size), Color(1, 0.9, 0.6, 0.08))
		draw_rect(Rect2(0, 1, 22, 22), Color("120e18"))
		draw_rect(Rect2(1, 2, 20, 20), Color("8a8698") if _hover else Color("4a4656"), false, 1.0)
		if _icon:
			draw_texture_rect(_icon, Rect2(2, 3, 18, 18), false)
		var name := TranslationServer.translate("SPELL_%s" % id.to_upper())
		var max_w := size.x - 27
		# lange Namen kuerzen, damit sie in die Spalte passen
		while UiTheme.font_body.get_string_size(name, HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.BODY_SIZE).x > max_w and name.length() > 3:
			name = name.left(name.length() - 2) + "."
		Hud.text(self, Vector2(26, 11), name, UiTheme.GOLD)
		Hud.text(self, Vector2(26, 21), Loc.t("SPELL_RANK", {"r": rank}), UiTheme.DIM)
