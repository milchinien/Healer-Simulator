class_name HardcoreDialog
extends ModalDialog
## Erklaert die Hardcore-Regeln (GDD Kapitel 6) und verlangt eine Bestaetigung.

signal accepted


func _init() -> void:
	super("HC_TITLE", 290)


func _ready() -> void:
	super()
	var skull := UI.texture("res://assets/gfx/icons/skull.png")
	body.add_child(skull)
	body.add_child(UI.wrap_label("HC_INTRO", 278, "HardcoreLabel"))
	for i in range(1, 6):
		var h := UI.hbox(3)
		var dot := UI.label("•", "GoldLabel")
		dot.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
		h.add_child(dot)
		h.add_child(UI.wrap_label("HC_RULE_%d" % i, 266))
		body.add_child(h)
	var back := add_button("HC_BACK", false, 80, "ui_back")
	back.pressed.connect(close)
	var ok := add_button("HC_ACCEPT", true, 110, "ui_select")
	ok.pressed.connect(func():
		accepted.emit()
		close())
