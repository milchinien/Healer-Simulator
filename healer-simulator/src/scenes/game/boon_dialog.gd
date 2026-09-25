class_name BoonDialog
extends ModalDialog
## Segen-Wahl nach einem Level-Up: 3 Karten, eine davon waehlen (dauerhaft, +% stapelbar).
## Die Karten zeigen Seltenheit (Farbe), Wert, Zuschlag, Ziel (Spieler/Gruppe) und die bisherige Summe.

signal chosen(boon: Dictionary)

const CARD := Vector2(124, 128)

var _offer: Array = []
var _character: Dictionary


func _init(level: int, offer: Array, character: Dictionary) -> void:
	super(Loc.t("BOON_TITLE", {"level": level}), 420)
	closable = false
	_offer = offer
	_character = character
	body.add_child(UI.label("BOON_HINT", "HintLabel", HORIZONTAL_ALIGNMENT_CENTER))
	var row := UI.hbox(8)
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	for b in offer:
		var card := BoonCard.new(b, CombatData.boon_mults(character, b["target"]).get(b["stat"], 0.0))
		card.picked.connect(_pick)
		row.add_child(card)
	body.add_child(row)


func _pick(b: Dictionary) -> void:
	Sfx.play("quest_done")
	chosen.emit(b)
	close()


## Eine Karte der Auswahl.
class BoonCard extends Control:
	signal picked(boon: Dictionary)

	var boon: Dictionary
	var _before := 0.0
	var _hover := false
	var _icon: Texture2D
	var _badge: Texture2D

	func _init(b: Dictionary, before: float) -> void:
		boon = b
		_before = before
		custom_minimum_size = CARD
		size = CARD
		mouse_filter = Control.MOUSE_FILTER_STOP
		mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
		var p := "res://assets/gfx/stats/%s.png" % b["stat"]
		_icon = load(p) if ResourceLoader.exists(p) else null
		if ResourceLoader.exists("res://assets/gfx/stats/group_badge.png"):
			_badge = load("res://assets/gfx/stats/group_badge.png")
		mouse_entered.connect(func():
			_hover = true
			Sfx.play("ui_hover")
			queue_redraw())
		mouse_exited.connect(func():
			_hover = false
			queue_redraw())

	func _gui_input(event: InputEvent) -> void:
		if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
			accept_event()
			picked.emit(boon)

	func _draw() -> void:
		var col: Color = CombatData.RARITY_COLORS.get(boon["rarity"], Color.WHITE)
		var r := Rect2(Vector2.ZERO, size)
		# Grund: dunkler Stein, oben ein Schimmer in der Raritaetsfarbe
		draw_rect(r, Color("120e18"))
		draw_rect(r.grow(-1), Color("1d1626"))
		for i in 26:
			draw_rect(Rect2(2, 2 + i, size.x - 4, 1), Color(col, 0.22 * (1.0 - i / 26.0)))
		# Rand in Raritaetsfarbe (bei Maus heller und doppelt)
		var edge := col.lightened(0.35) if _hover else col
		draw_rect(r.grow(-1), edge, false, 1.0)
		if _hover:
			draw_rect(r.grow(-2), Color(edge, 0.5), false, 1.0)
		Hud.corner_studs(self, r)
		var font := UiTheme.font_body
		var cx := size.x / 2.0
		_center_text(tr("RARITY_%s" % str(boon["rarity"]).to_upper()), 12, col)
		# Symbol doppelt gross in einer Fassung
		var ir := Rect2(cx - 18, 18, 36, 36)
		draw_rect(ir.grow(1), Color("120e18"))
		draw_rect(ir, Color("2a2233"))
		draw_rect(ir, Color(col, 0.6), false, 1.0)
		if _icon:
			draw_texture_rect(_icon, Rect2(cx - 16, 20, 32, 32), false)
		if boon["target"] == "group" and _badge:
			draw_texture(_badge, Vector2(cx + 9, 45))
		_center_text(tr("STAT_%s" % str(boon["stat"]).to_upper()), 68, UiTheme.CREAM)
		# Zuschlag gross
		var pct := "+%s %%" % _fmt(float(boon["pct"]))
		var tw := UiTheme.font_title.get_string_size(pct, HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.TITLE_SIZE).x
		draw_string(UiTheme.font_title, Vector2(roundf(cx - tw / 2.0) + 1, 88), pct, HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.TITLE_SIZE, UiTheme.SHADOW)
		draw_string(UiTheme.font_title, Vector2(roundf(cx - tw / 2.0), 87), pct, HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.TITLE_SIZE, col.lightened(0.2))
		_center_text(tr("BOON_TARGET_GROUP" if boon["target"] == "group" else "BOON_TARGET_PLAYER"), 102, UiTheme.GOLD if boon["target"] == "group" else Color("c8bfd6"))
		_center_text(Loc.t("BOON_TOTAL", {"before": _fmt(_before * 100.0), "after": _fmt(_before * 100.0 + float(boon["pct"]))}), 118, UiTheme.DIM)

	func _center_text(t: String, baseline: float, col: Color) -> void:
		var w := UiTheme.font_body.get_string_size(t, HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.BODY_SIZE).x
		Hud.text(self, Vector2(roundf((size.x - w) / 2.0), baseline), t, col)

	static func _fmt(v: float) -> String:
		var s := str(snappedf(v, 0.1))
		if s.ends_with(".0"):
			s = s.left(s.length() - 2)
		return s.replace(".", ",") if TranslationServer.get_locale().begins_with("de") else s
