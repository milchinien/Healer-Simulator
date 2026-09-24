class_name UI
extends RefCounted
## Kleine Fabrik fuer einheitliche UI-Elemente (alle Texte sind Uebersetzungsschluessel).


static func label(text_key: String, variant := "", align := HORIZONTAL_ALIGNMENT_LEFT) -> Label:
	var l := Label.new()
	l.text = text_key
	if variant != "":
		l.theme_type_variation = variant
	l.horizontal_alignment = align
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


static func wrap_label(text_key: String, width: int, variant := "") -> Label:
	var l := label(text_key, variant)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size.x = width
	return l


static func button(text_key: String, min_width := 0, red := false, click_sound := "ui_click") -> Button:
	var b := Button.new()
	b.text = text_key
	if red:
		b.theme_type_variation = "RedButton"
	b.custom_minimum_size = Vector2(min_width, 22 if red else 17)
	b.focus_mode = Control.FOCUS_NONE
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	Sfx.attach(b, click_sound)
	return b


static func icon_button(icon_path: String, tooltip_key := "", click_sound := "ui_click") -> Button:
	var b := Button.new()
	b.icon = load(icon_path)
	b.tooltip_text = tooltip_key
	b.focus_mode = Control.FOCUS_NONE
	b.custom_minimum_size = Vector2(17, 17)
	b.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
	Sfx.attach(b, click_sound)
	return b


static func texture(path: String) -> TextureRect:
	var t := TextureRect.new()
	t.texture = load(path)
	t.stretch_mode = TextureRect.STRETCH_KEEP_CENTERED
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return t


static func panel(variant := "") -> PanelContainer:
	var p := PanelContainer.new()
	if variant != "":
		p.theme_type_variation = variant
	return p


static func separator(width := 0) -> NinePatchRect:
	# Zierlinie als 9-Slice: Mitte gestreckt, verzierte Enden bleiben scharf
	var np := NinePatchRect.new()
	np.texture = load("res://assets/gfx/ui/separator.png")
	np.patch_margin_left = 6
	np.patch_margin_right = 6
	np.custom_minimum_size = Vector2(width, 5)
	np.size_flags_horizontal = Control.SIZE_EXPAND_FILL if width == 0 else Control.SIZE_SHRINK_CENTER
	np.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return np


static func vbox(sep := 2) -> VBoxContainer:
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", sep)
	return v


static func hbox(sep := 2) -> HBoxContainer:
	var h := HBoxContainer.new()
	h.add_theme_constant_override("separation", sep)
	return h


static func spacer(w := 0, h := 0) -> Control:
	var c := Control.new()
	c.custom_minimum_size = Vector2(w, h)
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return c


static func margin(child: Control, l := 4, t := 4, r := 4, b := 4) -> MarginContainer:
	var m := MarginContainer.new()
	m.add_theme_constant_override("margin_left", l)
	m.add_theme_constant_override("margin_top", t)
	m.add_theme_constant_override("margin_right", r)
	m.add_theme_constant_override("margin_bottom", b)
	m.add_child(child)
	return m


## Titelzeile mit Plakette (Fensterueberschrift).
static func header(text_key: String) -> PanelContainer:
	var p := panel("HeaderPanel")
	var l := label(text_key, "GoldLabel", HORIZONTAL_ALIGNMENT_CENTER)
	p.add_child(l)
	p.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	return p


## Abschnittsueberschrift: goldener Text mit Zierlinie darunter.
static func section(text_key: String) -> VBoxContainer:
	var v := vbox(1)
	v.add_child(label(text_key, "GoldLabel", HORIZONTAL_ALIGNMENT_CENTER))
	v.add_child(separator())
	return v


## Setzt ein Control so, dass seine Unterkante auf bottom_y liegt (Hoehe aus dem Inhalt).
static func pin_bottom(c: Control, x: float, bottom_y: float, width := 0.0) -> Control:
	if width > 0:
		c.custom_minimum_size.x = width
	c.reset_size()
	c.position = Vector2(x, bottom_y - c.get_combined_minimum_size().y)
	return c


## Positioniert ein Control fest (Pixel-Layout im 640x360-Raster).
static func place(c: Control, pos: Vector2, size := Vector2.ZERO) -> Control:
	c.position = pos
	if size != Vector2.ZERO:
		c.size = size
		c.custom_minimum_size = size
	return c
