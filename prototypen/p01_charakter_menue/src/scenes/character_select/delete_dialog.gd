class_name DeleteDialog
extends ModalDialog
## Sicherheitsabfrage beim Loeschen: der Charaktername muss eingetippt werden.

signal confirmed

var _character: Dictionary
var _input: LineEdit
var _delete_btn: Button


func _init(c: Dictionary) -> void:
	super("DELETE_TITLE", 300)
	_character = c


func _ready() -> void:
	super()
	var txt := UI.wrap_label(Loc.t("DELETE_TEXT", {"name": _character.get("name", "")}), 288)
	txt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	body.add_child(txt)
	_input = LineEdit.new()
	_input.placeholder_text = _character.get("name", "")
	_input.max_length = GameData.NAME_MAX
	_input.custom_minimum_size = Vector2(130, 16)
	_input.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	_input.alignment = HORIZONTAL_ALIGNMENT_CENTER
	_input.text_changed.connect(func(_t):
		Sfx.play("ui_type")
		_validate())
	_input.text_submitted.connect(func(_t):
		if not _delete_btn.disabled:
			_confirm())
	body.add_child(_input)
	var cancel := add_button("DELETE_CANCEL", false, 96, "ui_back")
	cancel.pressed.connect(close)
	_delete_btn = add_button("DELETE_CONFIRM", false, 96, "ui_click")
	_delete_btn.icon = load("res://assets/gfx/icons/trash.png")
	_delete_btn.pressed.connect(_confirm)
	_validate()
	_input.grab_focus.call_deferred()


func _validate() -> void:
	_delete_btn.disabled = _input.text.strip_edges().to_lower() != str(_character.get("name", "")).to_lower()


func _confirm() -> void:
	confirmed.emit()
	close()
