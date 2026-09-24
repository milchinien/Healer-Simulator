extends SceneTree

const CYCLE := preload("res://src/core/loading_backdrop_cycle.gd")


func _init() -> void:
	var path := "user://loading_cycle_test_%s.cfg" % OS.get_process_id()
	var expected := [
		"loading_gruenhain", "loading_gruenhain_woods", "loading_gruenhain_lake",
		"loading_gruenhain", "loading_gruenhain_woods", "loading_gruenhain_lake",
	]
	for name in expected:
		# Each call reopens disk state, also covering restart persistence.
		if CYCLE.take_next(path) != name:
			push_error("Loading background sequence mismatch")
			DirAccess.remove_absolute(path)
			quit(1)
			return
	var state := ConfigFile.new()
	state.set_value("gruenhain", "next", -1)
	state.save(path)
	if CYCLE.take_next(path) != "loading_gruenhain_lake":
		push_error("Invalid index was not normalized")
		DirAccess.remove_absolute(path)
		quit(1)
		return
	DirAccess.remove_absolute(path)
	print("LOADING BACKDROP CYCLE OK: sequence, wraparound, persisted state, invalid index")
	quit(0)
