    o = cube(name, (0, 0, 0), (1, 1, 1), material)
    o.parent = cam
    o.location = loc
    o.scale = scale
    return o


panel('Top title panel', (0, 3.15, -8), (2.0, .62, .012), panelmat)
text_obj('WHAT IF?  |  JAKARTA', 'Top label', (-1.72, 3.33, -7.98), .15, mint)
text_obj('SEMUA NAIK', 'Headline line 1', (-1.72, 3.04, -7.98), .23, white_text)
text_obj('TRANSPORTASI UMUM?', 'Headline line 2', (-1.72, 2.77, -7.98), .18, white_text)

subs = [
    (1, 250, 'Bagaimana jika seluruh warga Jakarta\nmemilih transportasi umum?', 'KOTA BERGERAK BERSAMA'),
    (251, 510, 'MRT, KRL, dan TransJakarta\nmenjadi pilihan utama masyarakat.', 'TRANSPORTASI PUBLIK'),
    (511, 770, 'Kemacetan berkurang drastis.\nPolusi udara mulai menurun.', 'JALANAN LEBIH LENGANG'),
    (771, 1020, 'Pengeluaran bahan bakar berkurang.\nWaktu menjadi lebih produktif.', 'WAKTU KEMBALI BERHARGA'),
    (1021, 1280, 'Ruang parkir berubah menjadi taman.\nTrotoar dan jalur sepeda bertambah.', 'RUANG KOTA UNTUK MANUSIA'),
    (1281, 1530, 'Udara terasa lebih segar.\nJakarta menjadi lebih sehat.', 'JAKARTA LEBIH HIJAU'),
    (1531, 1780, 'Jakarta bukan lagi kota\nuntuk menghabiskan waktu dalam macet.', 'KOTA YANG BERUBAH'),
    (1781, 2020, 'Melainkan kota tempat\norang menikmati perjalanan.', 'MENIKMATI PERJALANAN'),
    (2021, 2276, 'Perubahan besar dimulai dari keputusan sederhana:\nmemilih transportasi umum.', 'MULAI DARI PILIHAN KITA'),
]
for i, (a, b, caption, tag) in enumerate(subs):
    bg = panel('Subtitle background ' + str(i), (0, -2.8, -8), (2.0, .64, .012), panelmat)
    tx = text_obj(caption, 'Subtitle ' + str(i), (-1.72, -2.88, -7.98), .145, white_text)
    tg = text_obj(tag, 'Chapter ' + str(i), (-1.70, -2.35, -7.98), .105, mint)
    for ob in (bg, tx, tg):
        ob.hide_render = True
        ob.keyframe_insert(data_path='hide_render', frame=1)
        ob.hide_render = False
        ob.keyframe_insert(data_path='hide_render', frame=a)
        ob.hide_render = True
        ob.keyframe_insert(data_path='hide_render', frame=b + 1)

# ---------- lighting and atmosphere ----------
world = scene.world or bpy.data.worlds.new('Dusk city world')
scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (.035, .055, .085, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = .55

bpy.ops.object.light_add(type='AREA', location=(-3, -4, 25))
key = bpy.context.object
key.name = 'Large softbox key'
key.data.energy = 5200
key.data.shape = 'DISK'
key.data.size = 18
aim(key, (0, 0, 0))

bpy.ops.object.light_add(type='AREA', location=(13, 5, 14))
rim = bpy.context.object
rim.name = 'Cool architectural rim'
rim.data.energy = 2600
rim.data.color = (.42, .62, 1.0)
rim.data.size = 12
aim(rim, (0, 0, 3))
if hasattr(rim.data, 'use_shadow'):
    rim.data.use_shadow = False

bpy.ops.object.light_add(type='AREA', location=(-12, -12, 10))
fill = bpy.context.object
fill.name = 'Warm street fill'
fill.data.energy = 1900
fill.data.color = (1.0, .63, .38)
fill.data.size = 10
aim(fill, (0, 0, 0))
if hasattr(fill.data, 'use_shadow'):
    fill.data.use_shadow = False

# Blender 5 compositor API differs; disable compositing for this optimized render.
scene.render.use_compositing = False

# ---------- voice-over ----------
scene.sequence_editor_create()
audio = os.path.join(ROOT, 'assets', 'voiceover.mp3')
if os.path.exists(audio):
    scene.sequence_editor.strips.new_sound('Original Indonesian voice-over', audio, channel=1, frame_start=1)

# ---------- animation interpolation ----------
# Guard action access because Blender 5 introduced newer layered Action structures.
for ob in bpy.data.objects:
    anim = ob.animation_data
    action = anim.action if anim else None
    if action and hasattr(action, 'fcurves'):
        for fc in action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'BEZIER'

# ---------- save and render ----------
scene.render.image_settings.color_mode = 'RGB'
blend_path = os.path.join(ROOT, 'jakarta_whatif.blend')
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

print('=== RENDER SETTINGS ===', flush=True)
print('Blender:', bpy.app.version_string, flush=True)
print('Resolution:', scene.render.resolution_x, scene.render.resolution_y,
      scene.render.resolution_percentage, flush=True)
print('Samples:', RENDER_SAMPLES, flush=True)
print('Frames:', scene.frame_start, scene.frame_end, flush=True)
print('Output:', scene.render.filepath, flush=True)
print('Starting animation render...', flush=True)

bpy.ops.render.render(animation=True)
print('=== BLENDER RENDER COMPLETED ===', flush=True)
