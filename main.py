aim(fill, (0, 0, 0))

# =====================================================
# BLENDER 5.0.1 COMPOSITOR (NEW SOCKET API)
# =====================================================

# Blender 5.0 uses a standalone compositor node group.
scene.render.use_compositing = True

# Remove an earlier group with the same name if this script is run again.
old_comp = bpy.data.node_groups.get("Jakarta Cinematic Compositor")
if old_comp:
    bpy.data.node_groups.remove(old_comp)

comp_tree = bpy.data.node_groups.new(
    "Jakarta Cinematic Compositor",
    "CompositorNodeTree"
)
scene.compositing_node_group = comp_tree

comp_tree.interface.new_socket(
    name="Image",
    in_out='OUTPUT',
    socket_type='NodeSocketColor'
)

rl = comp_tree.nodes.new(type='CompositorNodeRLayers')
glare = comp_tree.nodes.new(type='CompositorNodeGlare')
comp_out = comp_tree.nodes.new(type='NodeGroupOutput')

# Blender 5.0 moved Glare settings from node properties to input sockets.
# Use the menu label for the Glare Type socket.
type_socket = glare.inputs.get("Type")
if type_socket is not None:
    type_socket.default_value = 'Fog Glow'

threshold_socket = glare.inputs.get("Threshold")
if threshold_socket is not None:
    threshold_socket.default_value = 1.5

# Optional strength control; leave Blender's default if unavailable.
strength_socket = glare.inputs.get("Strength")
if strength_socket is not None:
    strength_socket.default_value = 0.8

rl.location = (-400, 0)
glare.location = (-100, 0)
comp_out.location = (200, 0)

comp_tree.links.new(rl.outputs["Image"], glare.inputs["Image"])
comp_tree.links.new(glare.outputs["Image"], comp_out.inputs["Image"])

print("Blender 5.0.1 compositor configured with Fog Glow sockets.")

# =====================================================
# AUDIO
# =====================================================

audio = os.path.join(ROOT, 'assets', 'voiceover.mp3')

if os.path.exists(audio):
    editor = scene.sequence_editor_create()

    editor.strips.new_sound(
        'Original Indonesian voice-over',
        audio,
        channel=1,
        frame_start=1
    )

    print("Voice-over loaded:", audio)

else:
    print("WARNING: voiceover.mp3 not found:", audio)

# =====================================================
# ANIMATION INTERPOLATION
# =====================================================

for ob in bpy.data.objects:
    if ob.animation_data and ob.animation_data.action:
        try:
            # Legacy/simple action access; Blender 5.x may use layered actions.
            for fc in ob.animation_data.action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = 'BEZIER'
        except (AttributeError, TypeError):
            # Keep the animation and let Blender use its default interpolation
            # if the Action API does not expose legacy fcurves.
            pass

# =====================================================
# SAVE PROJECT
# =====================================================

scene.frame_set(1)

blend_path = os.path.join(ROOT, 'jakarta_whatif.blend')

bpy.ops.wm.save_as_mainfile(
    filepath=blend_path
)

print("Project saved:", blend_path)
print("Starting PNG animation render...")
print("Render resolution: %d%% (%dx%d)" % (
    RENDER_SCALE,
    int(scene.render.resolution_x * RENDER_SCALE / 100),
    int(scene.render.resolution_y * RENDER_SCALE / 100)
))
print("Eevee samples:", RENDER_SAMPLES)
print("Frames to render:", scene.frame_end)

# =====================================================
# RENDER ANIMATION
# =====================================================

bpy.ops.render.render(animation=True)

print("RENDER COMPLETED!")
print("PNG frames:", OUTPUT_DIR)
