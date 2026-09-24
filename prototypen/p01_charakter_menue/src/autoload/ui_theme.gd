extends Node
## Baut das UI-Theme aus den Pixel-Art-Texturen (assets/gfx/ui + data/ui_slices.json),
## setzt die Pixel-Schriften und den Mauszeiger.
##
## Theme-Varianten (theme_type_variation):
##   Button:  "RedButton" (Hauptaktion), Standard = dunkler Knopf
##   Label:   "TitleLabel", "NameLabel", "GoldLabel", "DimLabel", "ErrorLabel", "HintLabel"
##   Panel:   Standard = verzierter Goldrahmen, "PlainPanel", "HeaderPanel", "ListEntry*", "Tile*"

const GOLD := Color("ffd46b")
const GOLD_DIM := Color("c99a3a")
const CREAM := Color("f4e9cf")
const WHITE := Color("fbf7ee")
const DIM := Color("9a90a8")
const DISABLED := Color("6e6676")
const ERROR := Color("ff6a50")
const GOOD := Color("8ff08a")
const SHADOW := Color(0.03, 0.02, 0.05, 0.85)
const PANEL_ALPHA := 250
const HARDCORE := Color("ff4a3a")

var font_body: FontFile
var font_title: FontFile
var theme: Theme
var _slices := {}


func _enter_tree() -> void:
	font_body = _pixel_font("res://assets/fonts/Tiny5-Regular.ttf")
	font_title = _pixel_font("res://assets/fonts/Jersey15-Regular.ttf")
	var f := FileAccess.open("res://data/ui_slices.json", FileAccess.READ)
	_slices = JSON.parse_string(f.get_as_text())
	theme = _build_theme()


func _ready() -> void:
	get_tree().root.theme = theme
	get_tree().root.size_changed.connect(_update_cursor)
	_update_cursor.call_deferred()


func _pixel_font(path: String) -> FontFile:
	var font: FontFile = load(path)
	font.antialiasing = TextServer.FONT_ANTIALIASING_NONE
	font.hinting = TextServer.HINTING_NONE
	font.subpixel_positioning = TextServer.SUBPIXEL_POSITIONING_DISABLED
	font.generate_mipmaps = false
	font.force_autohinter = false
	return font


# ---------------------------------------------------------------- Mauszeiger
func _exit_tree() -> void:
	for shape in [Input.CURSOR_ARROW, Input.CURSOR_POINTING_HAND, Input.CURSOR_IBEAM]:
		Input.set_custom_mouse_cursor(null, shape)


func _update_cursor() -> void:
	if DisplayServer.get_name() == "headless":
		return
	var s := Settings.current_pixel_scale()
	_set_cursor("res://assets/gfx/cursor/pointer.png", Input.CURSOR_ARROW, Vector2(0, 0), s)
	_set_cursor("res://assets/gfx/cursor/pointer.png", Input.CURSOR_POINTING_HAND, Vector2(0, 0), s)
	_set_cursor("res://assets/gfx/cursor/text.png", Input.CURSOR_IBEAM, Vector2(3, 4), s)


func _set_cursor(path: String, shape: int, hotspot: Vector2, s: int) -> void:
	var tex: Texture2D = load(path)
	var img := tex.get_image()
	img.resize(img.get_width() * s, img.get_height() * s, Image.INTERPOLATE_NEAREST)
	Input.set_custom_mouse_cursor(ImageTexture.create_from_image(img), shape, hotspot * s)


# ---------------------------------------------------------------- Styleboxen
func stylebox(name: String) -> StyleBoxTexture:
	var sb := StyleBoxTexture.new()
	sb.texture = load("res://assets/gfx/ui/%s.png" % name)
	var info: Dictionary = _slices.get(name, {"margin": [4, 4, 4, 4], "content": [4, 4, 4, 4], "tile": true})
	var m: Array = info["margin"]
	var cm: Array = info["content"]
	sb.texture_margin_left = m[0]
	sb.texture_margin_top = m[1]
	sb.texture_margin_right = m[2]
	sb.texture_margin_bottom = m[3]
	sb.content_margin_left = cm[0]
	sb.content_margin_top = cm[1]
	sb.content_margin_right = cm[2]
	sb.content_margin_bottom = cm[3]
	if info.get("tile", true):
		sb.axis_stretch_horizontal = StyleBoxTexture.AXIS_STRETCH_MODE_TILE_FIT
		sb.axis_stretch_vertical = StyleBoxTexture.AXIS_STRETCH_MODE_TILE_FIT
	return sb


func tex(path: String) -> Texture2D:
	return load("res://assets/gfx/%s.png" % path)


func _build_theme() -> Theme:
	var t := Theme.new()
	t.default_font = font_body
	t.default_font_size = 8
	var empty := StyleBoxEmpty.new()

	# Label
	t.set_color("font_color", "Label", CREAM)
	t.set_color("font_shadow_color", "Label", SHADOW)
	t.set_constant("shadow_offset_x", "Label", 1)
	t.set_constant("shadow_offset_y", "Label", 1)
	t.set_constant("line_spacing", "Label", 1)
	_label_variant(t, "TitleLabel", font_title, 18, GOLD)
	_label_variant(t, "NameLabel", font_title, 18, WHITE)
	_label_variant(t, "GoldLabel", font_body, 8, GOLD)
	_label_variant(t, "DimLabel", font_body, 8, DIM)
	_label_variant(t, "ErrorLabel", font_body, 8, ERROR)
	_label_variant(t, "HintLabel", font_body, 8, Color("d8cfe6"))
	_label_variant(t, "HardcoreLabel", font_body, 8, HARDCORE)

	# RichTextLabel (fuer Beschreibungstexte)
	t.set_color("default_color", "RichTextLabel", CREAM)
	t.set_color("font_shadow_color", "RichTextLabel", SHADOW)
	t.set_constant("shadow_offset_x", "RichTextLabel", 1)
	t.set_constant("shadow_offset_y", "RichTextLabel", 1)
	t.set_constant("line_separation", "RichTextLabel", 2)
	t.set_font("normal_font", "RichTextLabel", font_body)
	t.set_font_size("normal_font_size", "RichTextLabel", 8)
	t.set_stylebox("normal", "RichTextLabel", empty)
	t.set_stylebox("focus", "RichTextLabel", empty)

	# Panels
	t.set_stylebox("panel", "PanelContainer", stylebox("panel"))
	t.set_stylebox("panel", "Panel", stylebox("panel"))
	for v in [["PlainPanel", "panel_plain"], ["HeaderPanel", "header"], ["TooltipPanel", "tooltip"],
			["ListEntryNormal", "list_normal"], ["ListEntryHover", "list_hover"], ["ListEntrySelected", "list_selected"],
			["TileNormal", "tile_normal"], ["TileHover", "tile_hover"], ["TileSelected", "tile_selected"]]:
		t.set_type_variation(v[0], "PanelContainer")
		t.set_stylebox("panel", v[0], stylebox(v[1]))

	# Buttons
	_button_type(t, "Button", "dark")
	t.set_type_variation("RedButton", "Button")
	_button_type(t, "RedButton", "red")
	t.set_font("font", "RedButton", font_title)
	t.set_font_size("font_size", "RedButton", 18)
	t.set_color("font_color", "RedButton", GOLD)
	t.set_color("font_hover_color", "RedButton", Color("fff2c0"))
	t.set_color("font_pressed_color", "RedButton", Color("e8c068"))
	t.set_color("font_focus_color", "RedButton", GOLD)
	t.set_color("font_hover_pressed_color", "RedButton", Color("fff2c0"))
	# Flacher Knopf ohne Rahmen (fuer Icon-Knoepfe)
	t.set_type_variation("FlatButton", "Button")
	for st in ["normal", "hover", "pressed", "disabled", "focus", "hover_pressed"]:
		t.set_stylebox(st, "FlatButton", empty)

	# LineEdit
	t.set_stylebox("normal", "LineEdit", stylebox("input_normal"))
	t.set_stylebox("focus", "LineEdit", stylebox("input_focus"))
	t.set_stylebox("read_only", "LineEdit", stylebox("input_normal"))
	t.set_color("font_color", "LineEdit", WHITE)
	t.set_color("font_placeholder_color", "LineEdit", DISABLED)
	t.set_color("caret_color", "LineEdit", GOLD)
	t.set_color("selection_color", "LineEdit", Color(0.8, 0.6, 0.2, 0.45))
	t.set_color("font_selected_color", "LineEdit", WHITE)
	t.set_constant("caret_width", "LineEdit", 1)
	t.set_constant("minimum_character_width", "LineEdit", 4)

	# Slider
	t.set_stylebox("slider", "HSlider", stylebox("slider_track"))
	t.set_stylebox("grabber_area", "HSlider", stylebox("slider_fill"))
	t.set_stylebox("grabber_area_highlight", "HSlider", stylebox("slider_fill"))
	t.set_icon("grabber", "HSlider", tex("ui/slider_knob_normal"))
	t.set_icon("grabber_highlight", "HSlider", tex("ui/slider_knob_hover"))
	t.set_icon("grabber_disabled", "HSlider", tex("ui/slider_knob_normal"))
	t.set_constant("center_grabber", "HSlider", 1)

	# CheckBox
	for type_name in ["CheckBox", "CheckButton"]:
		t.set_icon("checked", type_name, tex("ui/check_on"))
		t.set_icon("unchecked", type_name, tex("ui/check_off"))
		t.set_icon("checked_disabled", type_name, tex("ui/check_on"))
		t.set_icon("unchecked_disabled", type_name, tex("ui/check_off"))
		for st in ["normal", "hover", "pressed", "disabled", "focus", "hover_pressed"]:
			t.set_stylebox(st, type_name, empty)
		t.set_color("font_color", type_name, CREAM)
		t.set_color("font_hover_color", type_name, WHITE)
		t.set_color("font_pressed_color", type_name, CREAM)
		t.set_constant("h_separation", type_name, 4)

	# TabBar
	t.set_stylebox("tab_selected", "TabBar", stylebox("tab_selected"))
	t.set_stylebox("tab_unselected", "TabBar", stylebox("tab_normal"))
	t.set_stylebox("tab_hovered", "TabBar", stylebox("tab_hover"))
	t.set_stylebox("tab_focus", "TabBar", empty)
	t.set_color("font_selected_color", "TabBar", GOLD)
	t.set_color("font_unselected_color", "TabBar", DIM)
	t.set_color("font_hovered_color", "TabBar", CREAM)
	t.set_constant("h_separation", "TabBar", 2)

	# ProgressBar
	t.set_stylebox("background", "ProgressBar", stylebox("progress_bg"))
	t.set_stylebox("fill", "ProgressBar", stylebox("progress_fill"))
	t.set_color("font_color", "ProgressBar", WHITE)

	# ScrollBar
	t.set_stylebox("scroll", "VScrollBar", stylebox("scroll_track"))
	t.set_stylebox("grabber", "VScrollBar", stylebox("scroll_grabber"))
	t.set_stylebox("grabber_highlight", "VScrollBar", stylebox("scroll_grabber"))
	t.set_stylebox("grabber_pressed", "VScrollBar", stylebox("scroll_grabber"))

	# Tooltip
	t.set_stylebox("panel", "TooltipPanel", stylebox("tooltip"))
	t.set_color("font_color", "TooltipLabel", CREAM)
	t.set_font("font", "TooltipLabel", font_body)
	t.set_font_size("font_size", "TooltipLabel", 8)
	return t


func _label_variant(t: Theme, variant: String, font: Font, size: int, color: Color) -> void:
	t.set_type_variation(variant, "Label")
	t.set_font("font", variant, font)
	t.set_font_size("font_size", variant, size)
	t.set_color("font_color", variant, color)


func _button_type(t: Theme, type_name: String, kind: String) -> void:
	t.set_stylebox("normal", type_name, stylebox("btn_%s_normal" % kind))
	t.set_stylebox("hover", type_name, stylebox("btn_%s_hover" % kind))
	t.set_stylebox("pressed", type_name, stylebox("btn_%s_pressed" % kind))
	t.set_stylebox("hover_pressed", type_name, stylebox("btn_%s_pressed" % kind))
	t.set_stylebox("disabled", type_name, stylebox("btn_%s_disabled" % kind))
	t.set_stylebox("focus", type_name, StyleBoxEmpty.new())
	t.set_color("font_color", type_name, CREAM)
	t.set_color("font_hover_color", type_name, WHITE)
	t.set_color("font_pressed_color", type_name, GOLD_DIM)
	t.set_color("font_hover_pressed_color", type_name, GOLD)
	t.set_color("font_focus_color", type_name, CREAM)
	t.set_color("font_disabled_color", type_name, DISABLED)
	t.set_color("font_shadow_color", type_name, SHADOW)
	t.set_constant("h_separation", type_name, 4)
	t.set_font("font", type_name, font_body)
	t.set_font_size("font_size", type_name, 8)
