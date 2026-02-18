extends Node3D
# Fixed Brain Cube Renderer — Identity-locked projection
# BORING / SCIENTIFIC RENDER MODE (Signal > Splendor)

# ===============================
# LAYER VISIBILITY STATE
# ===============================
var layer_count := 28
var active_layers := {}
var layer_cursor := 1
var last_layer_cursor := 1
var core_dims = [3040, 1044, 222, 104, 770, 1831, 2337]  # 1-indexed
# --- File stepping (next / previous artifact) ---
@export var token_start := 0
@export var token_end := 127
var current_token := 6 

@export var layers := 28
@export var dims_per_layer := 3072
@export var grid_width := 64
@export var grid_height := 48
@export var spacing := 0.35
@export var layer_spacing := 1.5

# --- Clinical visual style ---
@export var base_opacity := 0.15
@export var node_color := Color(0.7, 0.7, 0.7)
@export var edge_color := Color(0.2, 0.2, 0.2)
@export var core_edge_color := Color(0.05, 0.05, 0.05)

@export var data_path := "res://data/sweep/A_baseline_09/tokens/t0027_gen.json"

@export var rotate_sensitivity := 0.01
@export var pan_sensitivity := 0.05
@export var zoom_sensitivity := 5.0
@export var min_pitch := -85.0
@export var max_pitch := 85.0

# --- Noise suppression ---
@export var min_edge_score := 0.05   # hard gate for edge rendering
@export var min_node_activation := 0.02

var edge_instance: Node3D
var node_instances: Dictionary = {}   # "layer:dim" -> MeshInstance3D

var yaw := 0.0
var pitch := 0.0
var selected_id: String = ""

# ============================================================
func _ready():
	print("==== FIXED BRAIN CUBE READY (BORING MODE) ====")

	for l in range(1, layers + 1):
		active_layers[l] = true

	layer_count = layers
	layer_cursor = 1
	last_layer_cursor = 1

	_load_and_project()

# ============================================================
func _apply_active_graph(edges: Dictionary):
	print("Building active neuron set from edges (layer-filtered)...")

	var active := {}

	for key in edges.keys():
		var clean = key.replace("v:", "")
		var parts = clean.split("|")
		if parts.size() == 2:
			active[parts[0]] = true
			active[parts[1]] = true

	# Remove stale or hidden nodes
	for id in node_instances.keys():
		var parts = id.split(":")
		if parts.size() != 2:
			continue

		var layer = int(parts[0])
		if not active.has(id) or not active_layers.get(layer, true):
			node_instances[id].queue_free()
			node_instances.erase(id)

	# Create missing nodes
	for id in active.keys():
		if node_instances.has(id):
			continue

		var parts = id.split(":")
		if parts.size() != 2:
			continue

		var l = int(parts[0])
		var d = int(parts[1])
		if not active_layers.get(l, true):
			continue

		var x = (d - 1) % grid_width
		var z = (d - 1) / grid_width
		var y = l - 1

		var pos := Vector3(x * spacing, y * layer_spacing, z * spacing)
		_draw_node(id, pos)

	print("✔ Active neurons:", node_instances.size())

# ============================================================
func _load_and_project():
	var path = data_path
	print("==== LOADING PROBE JSON ====")
	print("Token:", current_token)
	print("Path:", path)

	var file = FileAccess.open(path, FileAccess.READ)
	if file == null:
		push_error("FAILED TO OPEN FILE: " + path)
		return

	var json_text = file.get_as_text()
	file.close()

	var json = JSON.new()
	if json.parse(json_text) != OK:
		push_error("JSON parse error")
		return

	var data = json.data
	if data == null:
		return

	var edges = data.get("edges", {})
	_apply_active_graph(edges)
	_apply_neuron_overlay(data.get("neurons", {}))
	_apply_edges(edges)

# ============================================================
func _draw_node(id: String, pos: Vector3):
	var sphere := SphereMesh.new()
	sphere.radius = 1.0
	sphere.height = 2.0

	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.albedo_color = Color(node_color.r, node_color.g, node_color.b, base_opacity)
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA

	var instance := MeshInstance3D.new()
	instance.mesh = sphere
	instance.material_override = material
	instance.scale = Vector3.ONE * 0.15

	var body := StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var sphere_shape := SphereShape3D.new()
	sphere_shape.radius = 0.15
	shape.shape = sphere_shape

	body.position = pos
	body.add_child(shape)
	body.add_child(instance)
	add_child(body)

	node_instances[id] = instance

# ============================================================
# NEURON OVERLAY — ACTIVATION ONLY (NO STYLING)
# ============================================================
func _apply_neuron_overlay(neurons: Dictionary):
	print("Applying neuron overlay (clinical mode)...")
	for key in neurons.keys():
		if not node_instances.has(key): continue

		var act := float(neurons[key].get("activation", 0.0))
		if abs(act) < min_node_activation:
			continue

		var inst: MeshInstance3D = node_instances[key]
		var mat := StandardMaterial3D.new()
		mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA

		mat.albedo_color = Color(
			node_color.r,
			node_color.g,
			node_color.b,
			clamp(abs(act), 0.1, 1.0)
		)

		inst.material_override = mat

# ============================================================
# EDGE RENDERER — SCORE ONLY
# ============================================================
func _apply_edges(edges: Dictionary):
	print("Rendering edges (clinical mode)...")
	if edge_instance != null:
		edge_instance.queue_free()
	edge_instance = Node3D.new()
	add_child(edge_instance)

	for key in edges.keys():
		var parts = key.replace("v:", "").split("|")
		if parts.size() != 2: continue

		var a_id = parts[0]
		var b_id = parts[1]
		if not node_instances.has(a_id) or not node_instances.has(b_id):
			continue

		var e = edges[key]
		var score = float(e.get("score", 0.0))
		if score < min_edge_score:
			continue

		var a: Vector3 = node_instances[a_id].global_position
		var b: Vector3 = node_instances[b_id].global_position
		var dist = a.distance_to(b)
		if dist < 0.01:
			continue

		var cyl := CylinderMesh.new()
		cyl.top_radius = 0.03
		cyl.bottom_radius = 0.03
		cyl.height = dist

		var mat := StandardMaterial3D.new()
		mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA

		var is_core_edge = _touches_core(key, core_dims)
		var color = core_edge_color if is_core_edge else edge_color
		mat.albedo_color = Color(color.r, color.g, color.b, clamp(score, 0.05, 0.5))

		var inst := MeshInstance3D.new()
		inst.mesh = cyl
		inst.material_override = mat
		edge_instance.add_child(inst)

		inst.look_at_from_position((a + b) / 2.0, b, Vector3.UP)
		inst.rotate_object_local(Vector3.RIGHT, deg_to_rad(90))

# ============================================================
func _touches_core(edge_key: String, core_list: Array) -> bool:
	var clean_key = edge_key.replace("v:", "")
	var parts = clean_key.split("|")
	for p in parts:
		if ":" in p:
			var dim_part = p.split(":")[1]
			if core_list.has(int(dim_part)):
				return true
	return false

# ============================================================
func _update_transform():
	var basis = Basis()
	basis = Basis(Vector3.UP, yaw) * basis
	basis = basis * Basis(Vector3.RIGHT, pitch)
	transform.basis = basis
	
#=====================================================================
func _try_select_under_mouse():
	var cam := get_viewport().get_camera_3d()
	if cam == null:
		return
	
	var mouse_pos := get_viewport().get_mouse_position()
	var from := cam.project_ray_origin(mouse_pos)
	var to := from + cam.project_ray_normal(mouse_pos) * 10000.0
	
	var space_state := get_world_3d().direct_space_state
	var query := PhysicsRayQueryParameters3D.create(from, to)
	query.collide_with_bodies = true
	query.collide_with_areas = false
	
	var result := space_state.intersect_ray(query)
	if result.is_empty():
		_clear_selection()
		return
	
	var collider = result.get("collider")
	if collider == null:
		_clear_selection()
		return
	
	for id in node_instances.keys():
		var node_parent = node_instances[id].get_parent()
		if node_parent == collider:
			_set_selected(id)
			return
	
	_clear_selection()
#===========================================================================
func _set_selected(id: String):
	if selected_id == id:
		return
	_clear_selection()
	selected_id = id
	if not node_instances.has(id):
		return
	var inst: MeshInstance3D = node_instances[id]
	var mat: StandardMaterial3D = inst.material_override
	mat.albedo_color = Color(1.0, 1.0, 0.2, 1.0)
	print("▶ Selected dim:", id)

func _clear_selection():
	if selected_id != "" and node_instances.has(selected_id):
		var inst: MeshInstance3D = node_instances[selected_id]
		var mat: StandardMaterial3D = inst.material_override
		mat.albedo_color = Color(node_color.r, node_color.g, node_color.b, base_opacity)
	selected_id = ""

func _token_path(token_index: int) -> String:
	return "res://data/bob_ross_pizza/tokens/t%04d_gen.json" % token_index
	
func _unhandled_input(event):
	if event is InputEventKey and event.pressed:
		
				# -------------------------
		# MOVE LAYER CURSOR
		# -------------------------
		if event.keycode == KEY_UP:
			layer_cursor = clamp(layer_cursor - 1, 1, layer_count)
			print("▶ Layer cursor:", layer_cursor)
			return

		elif event.keycode == KEY_DOWN:
			layer_cursor = clamp(layer_cursor + 1, 1, layer_count)
			print("▶ Layer cursor:", layer_cursor)
			return

		# -------------------------
		# TOGGLE LAYER (ENTER)
		# -------------------------
		elif event.keycode == KEY_ENTER or event.keycode == KEY_KP_ENTER:

			active_layers[layer_cursor] = not active_layers.get(layer_cursor, true)
			print("▣ Toggled layer:", layer_cursor, "→", active_layers[layer_cursor])

			_load_and_project()
			return


		# Load previous file
		if event.keycode == KEY_LEFT:
			current_token = max(token_start, current_token - 1)
			print("⏪ Prev file:", current_token)
			_load_and_project()
			return

		# Load next file
		elif event.keycode == KEY_RIGHT:
			current_token = min(token_end, current_token + 1)
			print("⏩ Next file:", current_token)
			_load_and_project()
			return

		# Optional: click to select
		elif event.keycode == KEY_ENTER:
			_try_select_under_mouse()
