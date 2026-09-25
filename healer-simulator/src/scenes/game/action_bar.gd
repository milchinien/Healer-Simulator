class_name ActionBar
extends Control
## Aktionsleiste (GDD 13.3): 12 Plaetze, Tasten 1-0, ß, ´ (auf englischem Layout -, =).
## Zeigt Abklingzeit/GCD als Uhr-Animation, fehlendes Mana blau eingefaerbt, Tooltips mit Zauberdaten.
## Plaetze per Drag & Drop umsortieren, aus dem Zauberbuch belegen oder herausziehen.

signal slot_pressed(index: int)
signal bar_changed(spells: Array)    # nach Drag & Drop (zum Speichern)

const SLOTS := 12
const KEYS := [KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8, KEY_9, KEY_0, KEY_MINUS, KEY_EQUAL]

var spells: Array = []         # Zauber-ID je Platz ("" = leer)
var battle: Battle
var _flash := {}               # Platz -> Restzeit des Aufleuchtens
var _hover := -1
var _tex := {}
var slot := 40                 # Platz: Metallrahmen + Icon doppelt gross
var gap := 2
var _keys: Array = []          # Tastenbeschriftungen (einmal ermittelt)
var locked := false            # Leiste gesperrt (kein Umsortieren)
var _press_slot := -1
var _dragged := false
var _drag_origin := {}


func _init(slot_size := 40, slot_gap := 2) -> void:
	slot = slot_size
	gap = slot_gap
	custom_minimum_size = Vector2(SLOTS * (slot + gap) - gap, slot)
	size = custom_minimum_size
	mouse_filter = Control.MOUSE_FILTER_STOP
	# WoW-artige Plaetze: leere Vertiefung, Metallrahmen ueber dem Icon, Leuchtrand bei Maus/Druck
	for n in ["slot_frame", "slot_empty", "slot_hover", "slot_pressed"]:
		var p := "res://assets/gfx/hud/%s.png" % n
		_tex[n] = load(p) if ResourceLoader.exists(p) else null
	for i in SLOTS:
		_keys.append(key_label(i))


## Beschriftung der Taste nach aktuellem Tastaturlayout (deutsch: ß und ´).
static func key_label(i: int) -> String:
	var k: int = KEYS[i]
	var lbl := k
	if DisplayServer.get_name() != "headless":
		lbl = DisplayServer.keyboard_get_label_from_physical(k)
	var s := OS.get_keycode_string(lbl)
	if s.length() > 1:
		s = {KEY_MINUS: "-", KEY_EQUAL: "="}.get(k, s)
	return s


static func slot_for_key(e: InputEventKey) -> int:
	return KEYS.find(e.physical_keycode)


func set_spells(list: Array) -> void:
	spells = list.duplicate()
	queue_redraw()


func flash_slot(i: int) -> void:
	_flash[i] = 0.18


func _slot_at(pos: Vector2) -> int:
	var i := int(pos.x / (slot + gap))
	if i < 0 or i >= SLOTS or pos.y < 0 or pos.y > slot:
		return -1
	return i


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion:
		var h := _slot_at(event.position)
		if h != _hover:
			_hover = h
			if h >= 0 and spells.size() > h and spells[h] != "":
				Sfx.play("ui_hover")
			tooltip_text = _tooltip(h)
	elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		var i := _slot_at(event.position)
		if event.pressed:
			_press_slot = i
			_dragged = false
		elif i >= 0 and i == _press_slot and not _dragged:
			# Zaubern beim Loslassen (wie WoW), damit Ziehen nicht zaubert
			accept_event()
			slot_pressed.emit(i)
		if not event.pressed:
			_press_slot = -1


# ---------------------------------------------------------------- Drag & Drop (GDD 13.3)
func _get_drag_data(at_position: Vector2) -> Variant:
	var i := _slot_at(at_position)
	if locked or i < 0 or i >= spells.size() or spells[i] == "":
		return null
	_dragged = true
	set_drag_preview(SpellInfo.drag_preview(spells[i]))
	var data := {"spell": spells[i], "from_slot": i}
	# Platz leeren, solange gezogen wird (Loslassen ausserhalb = herausgezogen)
	spells[i] = ""
	_drag_origin = data
	Sfx.play("ui_select")
	return data


func _can_drop_data(at_position: Vector2, data: Variant) -> bool:
	return data is Dictionary and data.has("spell") and _slot_at(at_position) >= 0


func _drop_data(at_position: Vector2, data: Variant) -> void:
	var i := _slot_at(at_position)
	var id: String = data["spell"]
	# gleicher Zauber schon woanders auf der Leiste: dort entfernen
	var old := spells.find(id)
	if old != -1 and old != i:
		spells[old] = ""
	var displaced: String = spells[i]
	spells[i] = id
	if data.has("from_slot") and displaced != "" and displaced != id:
		spells[int(data["from_slot"])] = displaced     # Tausch
	_drag_origin = {}
	Sfx.play("ui_toggle")
	bar_changed.emit(spells.duplicate())


func _notification(what: int) -> void:
	if what == NOTIFICATION_MOUSE_EXIT:
		_hover = -1
	elif what == NOTIFICATION_DRAG_END and not _drag_origin.is_empty():
		# Ziehen ausserhalb der Leiste beendet: Zauber ist herausgezogen
		if not get_viewport().gui_is_drag_successful():
			Sfx.play("ui_back")
		_drag_origin = {}
		bar_changed.emit(spells.duplicate())


func _make_custom_tooltip(for_text: String) -> Object:
	return SpellInfo.make_tooltip(for_text)


func _tooltip(i: int) -> String:
	if i < 0 or i >= spells.size() or spells[i] == "" or battle == null or battle.player == null:
		return ""
	var id: String = spells[i]
	return SpellInfo.tooltip(id, battle.player.known_rank(id), battle.player)


func _process(delta: float) -> void:
	for k in _flash.keys():
		_flash[k] -= delta
		if _flash[k] <= 0.0:
			_flash.erase(k)
	queue_redraw()


func _draw() -> void:
	var p: CombatUnit = battle.player if battle else null
	for i in SLOTS:
		var x := i * (slot + gap)
		var r := Rect2(x + 2, 2, slot - 4, slot - 4)
		var id: String = spells[i] if i < spells.size() else ""
		if id == "":
			_tex_at("slot_empty", x)
			_tex_at("slot_frame", x)
			continue
		var icon := UnitFigure._aura_tex(str(CombatData.spell(id).get("icon", "")))
		if icon:
			draw_texture_rect(icon, r, false)
		if p != null:
			# zu wenig Mana: blau einfaerben (wie WoW)
			if p.res < battle.spell_mana(id, p) or not p.alive:
				draw_rect(r, Color(0.1, 0.2, 0.75, 0.55))
			# Abklingzeit bzw. GCD als Uhr
			var cd := float(p.cooldowns.get(id, 0.0))
			var total := float(CombatData.spell(id).get("cd", 0.0))
			var frac := 0.0
			if cd > 0.0 and total > 0.0:
				frac = cd / total
			elif p.gcd > 0.0:
				frac = p.gcd / battle.gcd_time(p)
			if frac > 0.0:
				_clock(r, frac)
			# laufender Zauber leuchtet
			if p.is_casting() and p.cast.get("spell", "") == id:
				draw_rect(r, Color(1.0, 0.9, 0.5, 0.18))
		_tex_at("slot_frame", x)
		if _flash.has(i):
			_tex_at("slot_pressed", x)
		elif i == _hover:
			_tex_at("slot_hover", x)
		# Taste oben rechts (wie WoW)
		var key: String = _keys[i]
		var kw := UiTheme.font_body.get_string_size(key, HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.BODY_SIZE).x
		Hud.text(self, Vector2(x + slot - 4 - kw, 11), key, Color("e8e4f0"))


func _tex_at(n: String, x: float) -> void:
	var t: Texture2D = _tex.get(n)
	if t:
		draw_texture_rect(t, Rect2(x, 0, slot, slot), false)


## Verdunkelt den verbleibenden Anteil im Uhrzeigersinn ab 12 Uhr.
func _clock(r: Rect2, frac: float) -> void:
	var c := r.get_center()
	var pts := PackedVector2Array([c])
	var steps := 24
	var start := -PI / 2 + TAU * (1.0 - frac)
	for s in steps + 1:
		var a := start + TAU * frac * s / steps
		var v := Vector2(cos(a), sin(a))
		# auf das Quadrat projizieren
		var m := maxf(absf(v.x), absf(v.y))
		pts.append(c + v / m * (r.size.x / 2.0))
	draw_colored_polygon(pts, Color(0.02, 0.01, 0.05, 0.62))
