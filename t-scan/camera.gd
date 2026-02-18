extends Camera3D
# RTS-Style Camera — Mouse Only, One-Handed Friendly
# Left = Pan, Right = Rotate, Middle = Vertical, Scroll = Zoom
@export var brain_renderer_path: NodePath
var brain_renderer: Node = null

# ===============================
# CONFIG
# ===============================
@export var scroll_speed := 5.0
@export var orbit_sensitivity := 0.003
@export var pan_sensitivity := 0.1
@export var min_pitch := -85.0
@export var max_pitch := 85.0

# ===============================
# STATE
# ===============================
var yaw := 0.0
var pitch := 0.0
var _ignore_next_mouse_motion := false

# ===============================
func _ready():
	current = true
	position = Vector3(0, 20, 50)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	if brain_renderer_path != NodePath():
		brain_renderer = get_node(brain_renderer_path)
	_update_camera()

# ===============================
func _unhandled_input(event):
	# --- Selection on left click ---
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
			if brain_renderer != null:
				brain_renderer._try_select_under_mouse()
	
	# -------------------------------
	# Mouse button press / release
	# -------------------------------
	if event is InputEventMouseButton:
		if event.pressed:
			# Only capture for right/middle mouse, not left
			if event.button_index != MOUSE_BUTTON_LEFT:
				Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
		else:
			# Release mouse when all buttons are up
			if not (Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT)
				or Input.is_mouse_button_pressed(MOUSE_BUTTON_MIDDLE)
				or Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT)):
				Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		
		# Scroll wheel = forward/back zoom
		if event.button_index == MOUSE_BUTTON_WHEEL_UP and event.pressed:
			var forward = -transform.basis.z
			position += forward * scroll_speed
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN and event.pressed:
			var forward = -transform.basis.z
			position -= forward * scroll_speed
	
	# -------------------------------
	# Mouse motion
	# -------------------------------
	if event is InputEventMouseMotion:
		if _ignore_next_mouse_motion:
			_ignore_next_mouse_motion = false
			return
		
		var left := Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT)
		var middle := Input.is_mouse_button_pressed(MOUSE_BUTTON_MIDDLE)
		var right := Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT)
		
		if right:
			# Right mouse = Rotate view (yaw/pitch)
			yaw -= event.relative.x * orbit_sensitivity
			pitch -= event.relative.y * orbit_sensitivity
			pitch = clamp(pitch, deg_to_rad(min_pitch), deg_to_rad(max_pitch))
			_update_camera()
		elif left:
			# Left mouse = Pan camera in screen space
			var right_vec := global_transform.basis.x
			var forward := -global_transform.basis.z
			# Flatten to horizontal plane for stable motion
			forward.y = 0
			forward = forward.normalized()
			position -= right_vec * event.relative.x * pan_sensitivity
			position -= forward * event.relative.y * pan_sensitivity
		elif middle:
			# Middle mouse = Vertical movement (up/down)
			position += Vector3.UP * event.relative.y * pan_sensitivity

# ===============================
func _update_camera():
	rotation = Vector3.ZERO
	rotate_y(yaw)
	rotate_object_local(Vector3.RIGHT, pitch)
	
