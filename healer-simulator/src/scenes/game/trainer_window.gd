class_name TrainerWindow
extends GameWindow
## Lehrmeister (GDD Kapitel 23): Zauber und Raenge fuer Gold lernen.
## Reiter "Zauber": alle Raenge (Allgemein), Status lernbar (gruen) / Stufe zu niedrig (grau mit Stufe) /
## gelernt (Haken); spaetere Raenge als Vorschau. "Lernen" je Eintrag, "Alle lernbaren lernen" mit Gesamtpreis.
## Reiter "Talente zuruecksetzen" ab Stufe 10 (noch gesperrt).

signal learned(id: String, rank: int)

const ROW_H := 24

var character: Dictionary
var player: CombatUnit
var _list: VBoxContainer
var _gold: Label
var _all_btn: Button
var _scroll: ScrollContainer


func _init(c: Dictionary, p: CombatUnit) -> void:
	super("trainer", "TRAINER_TITLE", Rect2(48, 22, 336, 230))
	character = c
	player = p
	var tabs := TabBar.new()
	tabs.focus_mode = Control.FOCUS_NONE
	tabs.add_tab("TRAINER_TAB_SPELLS")
	tabs.add_tab("TRAINER_TAB_TALENTS")
	tabs.set_tab_disabled(1, int(c.get("level", 1)) < 10)
	tabs.set_tab_tooltip(1, "TRAINER_TALENTS_LOCKED")
	body.add_child(tabs)
	_scroll = ScrollContainer.new()
	_scroll.custom_minimum_size = Vector2(0, 124)
	_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	body.add_child(_scroll)
	_list = UI.vbox(1)
	_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_scroll.add_child(_list)
	var foot := UI.hbox(6)
	var coin := UI.texture("res://assets/gfx/icons/coin.png")
	foot.add_child(coin)
	_gold = UI.label("", "GoldLabel")
	_gold.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	foot.add_child(_gold)
	_all_btn = UI.button("", 0, true)
	_all_btn.theme_type_variation = "RedButtonSmall"
	_all_btn.custom_minimum_size = Vector2(0, 18)
	_all_btn.pressed.connect(_learn_all)
	foot.add_child(_all_btn)
	body.add_child(foot)
	refresh()


var _seen := ""


## Gold oder Stufe haben sich geaendert (z. B. nach einer Welle): Liste aktualisieren.
func _process(_delta: float) -> void:
	var key := "%d/%d" % [int(character.get("gold", 0)), int(character.get("level", 1))]
	if key != _seen:
		refresh()


func refresh() -> void:
	_seen = "%d/%d" % [int(character.get("gold", 0)), int(character.get("level", 1))]
	for ch in _list.get_children():
		ch.queue_free()
	for e in CombatData.trainer_entries(character):
		var row := TrainerRow.new(e, character, player)
		row.learn_pressed.connect(_learn)
		_list.add_child(row)
	_gold.text = str(int(character.get("gold", 0)))
	var sum := Progression.learnable_summary(character)
	_all_btn.text = Loc.t("TRAINER_LEARN_ALL", {"price": sum["price"]})
	_all_btn.disabled = int(sum["count"]) == 0 or int(sum["price"]) > int(character.get("gold", 0))


func _learn(id: String, rank: int) -> void:
	var err := Progression.learn(character, id, rank)
	if err != "":
		Sfx.play("ui_error")
		return
	Sfx.play("hot_apply")
	learned.emit(id, rank)
	refresh()


func _learn_all() -> void:
	var any := false
	var progressed := true
	while progressed:
		progressed = false
		for e in CombatData.trainer_entries(character):
			if e["status"] == "learnable" and Progression.learn(character, e["id"], e["rank"]) == "":
				learned.emit(e["id"], e["rank"])
				any = true
				progressed = true
	Sfx.play("hot_apply" if any else "ui_error")
	refresh()


## Eine Zeile: Symbol, Name, Rang/Stufe, Preis, Knopf bzw. Status.
class TrainerRow extends Control:
	signal learn_pressed(id: String, rank: int)

	var e: Dictionary
	var _c: Dictionary
	var _p: CombatUnit
	var _icon: Texture2D
	var _btn: Button

	func _init(entry: Dictionary, c: Dictionary, p: CombatUnit) -> void:
		e = entry
		_c = c
		_p = p
		custom_minimum_size = Vector2(0, ROW_H)
		mouse_filter = Control.MOUSE_FILTER_PASS
		_icon = UnitFigure._aura_tex(str(CombatData.spell(e["id"]).get("icon", "")))
		tooltip_text = "x"
		if e["status"] == "learnable":
			_btn = UI.button("TRAINER_LEARN", 0)
			_btn.custom_minimum_size = Vector2(52, 16)
			_btn.disabled = int(c.get("gold", 0)) < int(e["price"])
			_btn.pressed.connect(func(): learn_pressed.emit(e["id"], e["rank"]))
			add_child(_btn)

	func _notification(what: int) -> void:
		if what == NOTIFICATION_RESIZED and _btn:
			_btn.position = Vector2(size.x - 56, 4)

	func _make_custom_tooltip(_for_text: String) -> Object:
		return SpellInfo.make_tooltip(SpellInfo.tooltip(e["id"], e["rank"], _p))

	func _draw() -> void:
		var st: String = e["status"]
		var dim := st in ["level", "previous"]
		draw_rect(Rect2(0, 0, size.x, ROW_H - 1), Color(1, 1, 1, 0.03) if not dim else Color(0, 0, 0, 0.15))
		draw_rect(Rect2(0, ROW_H - 1, size.x, 1), Color(0.78, 0.6, 0.23, 0.18))
		# Symbol in Fassung
		draw_rect(Rect2(2, 2, 20, 20), Color("120e18"))
		if _icon:
			draw_texture_rect(_icon, Rect2(3, 3, 18, 18), false, Color(1, 1, 1, 0.35) if dim else Color.WHITE)
		# Name und Rang/Stufe
		var name_col := UiTheme.CREAM
		match st:
			"learnable":
				name_col = UiTheme.GOOD
			"learned":
				name_col = UiTheme.GOLD
			_:
				name_col = UiTheme.DISABLED
		Hud.text(self, Vector2(26, 10), TranslationServer.translate("SPELL_%s" % str(e["id"]).to_upper()), name_col)
		var sub := Loc.t("SPELL_RANK", {"r": e["rank"]}) + "   " + Loc.t("TRAINER_REQ_LEVEL", {"level": e["level"]})
		Hud.text(self, Vector2(26, 20), sub, UiTheme.DIM if st != "level" else Color("c86a5a"))
		# Preis bzw. Status rechts
		var right := size.x - 60
		match st:
			"learned":
				# gruener Haken (gelernt)
				var o := Vector2(size.x - 38, 7)
				for d in [Vector2(1, 1), Vector2.ZERO]:
					var col := UiTheme.SHADOW if d != Vector2.ZERO else UiTheme.GOOD
					draw_line(o + d + Vector2(0, 5), o + d + Vector2(3, 8), col, 2.0)
					draw_line(o + d + Vector2(3, 8), o + d + Vector2(9, 1), col, 2.0)
			"learnable":
				var price := str(e["price"])
				var pw := UiTheme.font_body.get_string_size(price, HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.BODY_SIZE).x
				var enough := int(_c.get("gold", 0)) >= int(e["price"])
				Hud.text(self, Vector2(right - pw - 2, 15), price, UiTheme.GOLD if enough else UiTheme.ERROR)
				draw_texture(load("res://assets/gfx/icons/coin.png"), Vector2(right - pw - 13, 7))
			_:
				var price2 := str(e["price"])
				var pw2 := UiTheme.font_body.get_string_size(price2, HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.BODY_SIZE).x
				Hud.text(self, Vector2(size.x - pw2 - 4, 15), price2, UiTheme.DISABLED)
