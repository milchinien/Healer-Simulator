extends RefCounted
## Presentation-only rotation, independent of character saves and gameplay.

const BACKGROUNDS := [
	"loading_gruenhain",
	"loading_gruenhain_woods",
	"loading_gruenhain_lake",
]


static func take_next(state_path: String) -> String:
	var state := ConfigFile.new()
	state.load(state_path)
	var index := posmod(int(state.get_value("gruenhain", "next", 0)), BACKGROUNDS.size())
	state.set_value("gruenhain", "next", (index + 1) % BACKGROUNDS.size())
	var error := state.save(state_path)
	if error != OK:
		push_warning("Could not persist loading background rotation: %s" % error_string(error))
	return BACKGROUNDS[index]
