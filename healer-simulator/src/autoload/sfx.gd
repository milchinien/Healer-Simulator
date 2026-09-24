extends Node
## Soundeffekte. Sfx.play("ui_click") spielt assets/sfx/ui_click.wav auf dem SFX-Bus.

const SOUNDS := [
	"ui_hover", "ui_click", "ui_back", "ui_select", "ui_toggle", "ui_error", "ui_open", "ui_close",
	"ui_type", "ui_dice", "char_created", "char_deleted", "enter_world", "title_start", "hardcore",
]
const POOL_SIZE := 8

var _streams := {}
var _players: Array[AudioStreamPlayer] = []
var _next := 0
var _last_played := {}


func _ready() -> void:
	for sound_name in SOUNDS:
		var path := "res://assets/sfx/%s.wav" % sound_name
		if ResourceLoader.exists(path):
			_streams[sound_name] = load(path)
	for i in POOL_SIZE:
		var p := AudioStreamPlayer.new()
		p.bus = "SFX"
		add_child(p)
		_players.append(p)


func play(sound_name: String, pitch := 1.0, volume_db := 0.0) -> void:
	if not _streams.has(sound_name):
		return
	# Gleiche Sounds nicht mehrfach im selben Moment (z. B. Hover beim schnellen Ueberfahren)
	var now := Time.get_ticks_msec()
	if now - int(_last_played.get(sound_name, -1000)) < 30:
		return
	_last_played[sound_name] = now
	var p := _players[_next]
	_next = (_next + 1) % POOL_SIZE
	p.stream = _streams[sound_name]
	p.pitch_scale = pitch
	p.volume_db = volume_db
	p.play()


## Haengt Hover- und Klick-Sounds an einen Button.
func attach(button: BaseButton, click_sound := "ui_click") -> void:
	button.mouse_entered.connect(func():
		if not button.disabled:
			play("ui_hover"))
	button.pressed.connect(func(): play(click_sound))
