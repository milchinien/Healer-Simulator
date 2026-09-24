extends Node
## Spieleinstellungen (Anzeige, Audio, Sprache). Gespeichert in <base_dir>/settings.cfg.
##
## base_dir ist normalerweise "user://". Mit dem Startargument `-- profile=<name>`
## wird ein getrenntes Profil verwendet (z. B. fuer automatische Tests/Screenshots).

signal changed

const BASE_W := 640
const BASE_H := 360
const SCALES := [2, 3, 4]

var base_dir := "user://"
var user_args := {}

var fullscreen := false
var window_scale := 2
var vol_master := 0.8
var vol_music := 0.7
var vol_sfx := 0.8
var language := "en"
var background_style := "refined"


func _enter_tree() -> void:
	_parse_user_args()
	if user_args.has("profile"):
		base_dir = "user://profiles/%s/" % user_args["profile"]
	DirAccess.make_dir_recursive_absolute(base_dir)
	_ensure_audio_buses()
	load_settings()
	if user_args.has("lang"):
		language = user_args["lang"]
	if user_args.get("background_style", "") in ["refined", "classic"]:
		background_style = user_args["background_style"]


func _ready() -> void:
	apply()


func _parse_user_args() -> void:
	for arg in OS.get_cmdline_user_args():
		var parts: PackedStringArray = arg.split("=", true, 1)
		user_args[parts[0]] = parts[1] if parts.size() > 1 else "1"


func _ensure_audio_buses() -> void:
	for bus_name in ["Music", "SFX"]:
		if AudioServer.get_bus_index(bus_name) == -1:
			AudioServer.add_bus()
			var idx := AudioServer.bus_count - 1
			AudioServer.set_bus_name(idx, bus_name)
			AudioServer.set_bus_send(idx, "Master")


func settings_path() -> String:
	return base_dir + "settings.cfg"


func load_settings() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(settings_path()) != OK:
		return
	fullscreen = cfg.get_value("display", "fullscreen", fullscreen)
	window_scale = int(cfg.get_value("display", "window_scale", window_scale))
	vol_master = float(cfg.get_value("audio", "master", vol_master))
	vol_music = float(cfg.get_value("audio", "music", vol_music))
	vol_sfx = float(cfg.get_value("audio", "sfx", vol_sfx))
	language = str(cfg.get_value("general", "language", language))
	background_style = str(cfg.get_value("display", "background_style", "refined"))
	if background_style not in ["refined", "classic"]:
		background_style = "refined"
	if not window_scale in SCALES:
		window_scale = 2


func save_settings() -> void:
	var cfg := ConfigFile.new()
	cfg.set_value("display", "fullscreen", fullscreen)
	cfg.set_value("display", "window_scale", window_scale)
	cfg.set_value("display", "background_style", background_style)
	cfg.set_value("audio", "master", vol_master)
	cfg.set_value("audio", "music", vol_music)
	cfg.set_value("audio", "sfx", vol_sfx)
	cfg.set_value("general", "language", language)
	cfg.save(settings_path())


func snapshot() -> Dictionary:
	return {
		"fullscreen": fullscreen, "window_scale": window_scale, "vol_master": vol_master,
		"vol_music": vol_music, "vol_sfx": vol_sfx, "language": language,
		"background_style": background_style,
	}


func restore(snap: Dictionary) -> void:
	for key in snap:
		set(key, snap[key])
	apply()


func reset_defaults() -> void:
	background_style = "refined"
	fullscreen = false
	window_scale = 2
	vol_master = 0.8
	vol_music = 0.7
	vol_sfx = 0.8
	apply()


## Wendet alle Werte an (Fenster, Lautstaerke, Sprache).
func apply() -> void:
	_apply_audio()
	_apply_display()
	TranslationServer.set_locale(language)
	changed.emit()


func _apply_audio() -> void:
	_set_bus_volume("Master", vol_master)
	_set_bus_volume("Music", vol_music)
	_set_bus_volume("SFX", vol_sfx)


func _set_bus_volume(bus_name: String, value: float) -> void:
	var idx := AudioServer.get_bus_index(bus_name)
	if idx == -1:
		return
	AudioServer.set_bus_mute(idx, value <= 0.001)
	AudioServer.set_bus_volume_db(idx, linear_to_db(maxf(value, 0.0001)))


func _apply_display() -> void:
	if DisplayServer.get_name() == "headless":
		return
	var win := get_window()
	if fullscreen:
		win.mode = Window.MODE_FULLSCREEN
	else:
		if win.mode != Window.MODE_WINDOWED:
			win.mode = Window.MODE_WINDOWED
		var size := Vector2i(BASE_W * window_scale, BASE_H * window_scale)
		var screen := DisplayServer.window_get_current_screen()
		var usable := DisplayServer.screen_get_usable_rect(screen)
		# Zu grosse Fenster auf die groesste passende Stufe begrenzen
		while (size.x > usable.size.x or size.y > usable.size.y) and size.x > BASE_W * 2:
			size -= Vector2i(BASE_W, BASE_H)
		win.size = size
		win.position = usable.position + (usable.size - size) / 2


## Groesster ganzzahliger Skalierungsfaktor der aktuellen Fenstergroesse.
func current_pixel_scale() -> int:
	var s := get_window().size
	return maxi(1, mini(s.x / BASE_W, s.y / BASE_H))


func max_window_scale() -> int:
	var usable := DisplayServer.screen_get_usable_rect(DisplayServer.window_get_current_screen())
	var best := 2
	for s in SCALES:
		if BASE_W * s <= usable.size.x and BASE_H * s <= usable.size.y:
			best = s
	return best
