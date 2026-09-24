extends Control
## Titelbildschirm: Logo ueber animierter Nachtszene, "Beliebige Taste druecken".

var _logo: TextureRect
var _logo_glow: Sprite2D
var _press: Label
var _t := 0.0
var _leaving := false


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var bd := SceneBackdrop.new()
	add_child(bd)
	bd.setup("title")

	_logo_glow = Sprite2D.new()
	_logo_glow.texture = load("res://assets/gfx/fx/glow_big.png")
	_logo_glow.material = preload("res://src/render/additive.tres")
	_logo_glow.scale = Vector2(4, 2)
	_logo_glow.modulate = Color(1, 0.85, 0.5, 0.18)
	_logo_glow.position = Vector2(320, 76)
	add_child(_logo_glow)

	_logo = TextureRect.new()
	_logo.texture = load("res://assets/gfx/logo.png")
	_logo.position = Vector2(roundi((640 - _logo.texture.get_width()) / 2.0), 28)
	_logo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_logo)

	_press = UI.label("TITLE_PRESS_KEY", "TitleLabel", HORIZONTAL_ALIGNMENT_CENTER)
	UI.place(_press, Vector2(0, 322), Vector2(640, 18))
	add_child(_press)

	var version := UI.label(Loc.t("TITLE_VERSION", {"v": ProjectSettings.get_setting("application/config/version")}), "DimLabel", HORIZONTAL_ALIGNMENT_RIGHT)
	UI.place(version, Vector2(440, 348), Vector2(196, 10))
	add_child(version)
	var credit := UI.label("TITLE_CREDITS", "DimLabel")
	UI.place(credit, Vector2(4, 348), Vector2(300, 10))
	add_child(credit)


func _process(delta: float) -> void:
	_t += delta
	# Logo schwebt sanft (ganzzahlige Pixel)
	_logo.position.y = 28 + roundi(sin(_t * 1.4) * 2.0)
	_logo_glow.modulate.a = 0.14 + 0.06 * sin(_t * 1.4)
	_press.modulate.a = 0.35 + 0.65 * (0.5 + 0.5 * sin(_t * 3.2))


func _input(event: InputEvent) -> void:
	if _leaving or Router.busy:
		return
	var go := false
	if event is InputEventKey and event.pressed and not event.echo:
		go = true
	elif event is InputEventMouseButton and event.pressed:
		go = true
	if go:
		_leaving = true
		get_viewport().set_input_as_handled()
		Sfx.play("title_start")
		if SaveGame.count() == 0:
			Router.go("character_create", {"first": true}, 0.6)
		else:
			Router.go("character_select", {}, 0.6)
