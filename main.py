import bpy
import math
import os
import random
from mathutils import Vector

# ============================================================
# JAKARTA WHAT-IF SHORT — Blender 5.0.1 compatible
# Output: output/frames/frame_0001.png ...
# Test:   RENDER_TEST_FRAMES=20
# Full:   RENDER_TEST_FRAMES=0
# ============================================================

random.seed(41)
ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(ROOT, "output", "frames")
os.makedirs(OUTPUT_DIR, exist_ok=True)

RENDER_SCALE = max(10, min(100, int(os.environ.get("RENDER_SCALE", "50"))))
RENDER_SAMPLES = max(1, min(128, int(os.environ.get("RENDER_SAMPLES", "16"))))
RENDER_TEST_FRAMES = int(os.environ.get("RENDER_TEST_FRAMES", "20"))
FULL_FRAME_COUNT = 2276
FPS = 30

# ---------- reset ----------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials,
                   bpy.data.cameras, bpy.data.lights):
    # Orphan cleanup is safe; do not remove datablocks still in use.
    pass

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.resolution_percentage = RENDER_SCALE
scene.render.fps = FPS
scene.frame_start = 1
scene.frame_end = RENDER_TEST_FRAMES if RENDER_TEST_FRAMES > 0 else FULL_FRAME_COUNT
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.image_settings.color_depth = '8'
scene.render.filepath = os.path.join(OUTPUT_DIR, "frame_")
scene.render.use_file_extension = True
scene.render.use_compositing = False
scene.render.film_transparent = False
scene.render.image_settings.color_mode = 'RGB'
scene.render.resolution_percentage = RENDER_SCALE
scene.render.engine = 'BLENDER_EEVEE'
scene.render.use_motion_blur = False
scene.view_settings.view_transform = 'AgX'
scene.render.image_settings.color_mode = 'RGB'
scene.camera = None

# ---------- materials ----------
def mat(name, color, metal=0.0, rough=0.55, emission=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1)
        bsdf.inputs["Metallic"].default_value = metal
        bsdf.inputs["Roughness"].default_value = rough
        if emission:
            bsdf.inputs["Emission Color"].default_value = (*color, 1)
            bsdf.inputs["Emission Strength"].default_value = emission
    return m

asphalt = mat("Road | charcoal", (.045, .055, .065), rough=.92)
sidewalk = mat("Sidewalk | concrete", (.36, .35, .31), rough=.85)
concrete = mat("Tower | warm graphite", (.16, .19, .22), rough=.72)
concrete2 = mat("Tower | slate", (.23, .26, .29), rough=.65)
glass = mat("Reflective blue glass", (.025, .12, .19), .35, .22)
window_warm = mat("Lit windows | warm", (1.0, .55, .22), .05, .35, 1.3)
window_cool = mat("Lit windows | cool", (.32, .62, .85), .05, .3, .8)
lane = mat("Road markings", (.9, .82, .62), rough=.6)
grass = mat("Median grass", (.09, .25, .12), rough=1)
leaf = mat("Tree foliage", (.10, .30, .14), rough=1)
leaf_light = mat("Tree foliage light", (.20, .40, .19), rough=1)
bark = mat("Tree bark", (.18, .09, .045), rough=1)
red = mat("Car | crimson", (.65, .035, .035), .25, .28)
blue = mat("Car | blue", (.025, .10, .27), .35, .25)
white = mat("Vehicle | pearl", (.72, .75, .72), .2, .28)
black = mat("Rubber", (.012, .015, .018), rough=.9)
metal = mat("Metal", (.38, .45, .49), .7, .25)
bus_red = mat("TransJakarta | red", (.75, .025, .035), .2, .28)
bus_white = mat("TransJakarta | white", (.82, .84, .81), .15, .3)
skin = mat("Skin", (.57, .32, .20))
shirt_blue = mat("People | blue", (.035, .18, .48))
shirt_yellow = mat("People | yellow", (.95, .53, .06))
shirt_white = mat("People | white", (.78, .80, .76))
shirt_green = mat("People | green", (.06, .30, .16))

# ---------- geometry helpers ----------
def cube(name, loc, scale, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        ob.data.materials.append(material)
    if bevel:
        mod = ob.modifiers.new("Soft edges", 'BEVEL')
        mod.width = bevel
        mod.segments = 2
    return ob

def cylinder(name, loc, radius, depth, material, vertices=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    ob = bpy.context.object
    ob.name = name
    if material:
        ob.data.materials.append(material)
    return ob

def uv_sphere(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, location=loc)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    if material:
        ob.data.materials.append(material)
    return ob

def key_location(ob, frame, loc):
    ob.location = loc
    ob.keyframe_insert(data_path="location", frame=frame)

def animate_x(ob, x1, x2, y, z, start=1, end=None):
    if end is None:
        end = FULL_FRAME_COUNT
    key_location(ob, start, (x1, y, z))
    key_location(ob, end, (x2, y, z))

# ---------- city road and sidewalks ----------
cube("Main asphalt avenue", (0, 0, -0.22), (18, 100, .4), asphalt)
cube("West sidewalk", (-8.0, 0, -.02), (2.0, 100, .25), sidewalk)
cube("East sidewalk", (8.0, 0, -.02), (2.0, 100, .25), sidewalk)
cube("Central busway", (0, 0, .015), (3.5, 100, .08), mat("Busway pavement", (.12,.14,.15), rough=.9))
# Road lanes and dashed markings
for x in (-5.2, -2.1, 2.1, 5.2):
    for y in range(-46, 50, 8):
        cube("Dashed lane marking", (x, y, .015), (.10, 3.4, .025), lane)
# Busway edge lines
for x in (-1.85, 1.85):
    cube("Busway boundary", (x, 0, .075), (.12, 100, .035), lane)
# Crosswalk in foreground
for i in range(9):
    cube("Crosswalk stripe", (-5.2 + i*1.3, -10, .035), (.72, 4.0, .035), lane)
# Median planter
cube("Green median", (0, 0, .11), (.22, 100, .12), grass)

# ---------- buildings ----------
for side in (-1, 1):
    for i, y in enumerate(range(-38, 45, 13)):
        h = random.uniform(15, 34)
        w = random.uniform(6.5, 9.5)
        x = side * random.uniform(12.5, 16.5)
        base_mat = concrete if i % 2 else concrete2
        cube("Jakarta office tower", (x, y, h/2 - .1), (w, 10.5, h), base_mat, .12)
        # glass facade and window grid facing avenue
        facade_x = x - side * (w/2 + .035)
        cube("Blue glass facade", (facade_x, y, h*.53), (.08, 9.7, h*.82), glass)
        for row in range(max(3, int(h/2.6))):
            wz = 2.0 + row*2.45
            if wz > h-1:
                continue
            for col in range(4):
                wy = y - 3.8 + col*2.5
                wm = window_warm if random.random() < .48 else window_cool
                cube("Illuminated office window",
                     (facade_x - side*.055, wy, wz),
                     (.035, 1.35, 1.25), wm)
        # roof cap / sign structure
        cube("Tower rooftop", (x, y, h+.18), (w*.72, 3.0, .35), metal, .05)

# ---------- trees ----------
for side in (-1, 1):
    for y in range(-40, 43, 10):
        x = side * 8.0
        cylinder("Tree trunk", (x, y, 1.45), .22, 2.9, bark)
        uv_sphere("Tree crown", (x, y, 3.4), (1.35, 1.25, 1.45), leaf)
        uv_sphere("Tree crown highlight", (x+.35, y-.25, 3.8), (.8,.75,.85), leaf_light)

# ---------- streetlights ----------
for side in (-1, 1):
    for y in range(-35, 40, 15):
        x = side * 7.0
        cylinder("Streetlight pole", (x, y, 4.0), .07, 8.0, metal)
        arm = cube("Streetlight arm", (x-side*.65, y, 7.8), (1.4,.09,.09), metal)
        lamp = uv_sphere("Streetlight lamp", (x-side*1.25, y, 7.75), (.25,.25,.12), window_warm)


# ---------- vehicles ----------
def make_car(name, body_mat, y, x=-4.0, direction=1):
    parts = []

    body = cube(
        name+" body",
        (x,y,.72),
        (2.0,4.1,1.05),
        body_mat,
        .18
    )

    roof = cube(
        name+" roof",
        (x,y+.15,1.43),
        (1.65,2.0,.72),
        body_mat,
        .2
    )

    windshield = cube(
        name+" windshield",
        (x,y-0.78,1.48),
        (1.48,.06,.52),
        glass,
        .025
    )

    rear = cube(
        name+" rear glass",
        (x,y+1.08,1.48),
        (1.48,.06,.48),
        glass,
        .025
    )

    parts += [roof, windshield, rear]

    for wx in (-.95,.95):
        for wy in (-1.25,1.25):
            wheel = cylinder(
                name+" wheel",
                (x+wx,y+wy,.43),
                .38,
                .18,
                black,
                16
            )

            wheel.rotation_euler[1] = math.pi/2
            parts.append(wheel)

    # Parent hanya objek tambahan, bukan body itu sendiri
    for part in parts:
        part.parent = body
        part.matrix_parent_inverse = body.matrix_world.inverted()

    return body


car1 = make_car("Red sedan", red, -13, -4.3)
car2 = make_car("Blue sedan", blue, 5, 4.4)
car3 = make_car("White sedan", white, 24, -4.3)
animate_x(car1, -4.3, -4.3, -13, .72)
animate_x(car2, 4.4, 4.4, 5, .72)
animate_x(car3, -4.3, -4.3, 24, .72)

def make_bus(name, y, material_main, material_secondary):
    base = cube(name+" long body", (0,y,1.65), (2.8,11.5,3.1), material_main, .22)
    lower = cube(name+" lower panel", (0,y,.75), (2.82,11.2,1.0), material_secondary, .1)
    for side in (-1,1):
        for i in range(5):
            cube(name+" passenger window", (side*1.415, y-4.3+i*1.75, 2.15),
                 (.045,1.42,1.0), glass, .025)
    cube(name+" front windshield", (0,y-5.78,2.1), (2.3,.045,1.45), glass, .04)
    cube(name+" destination display", (0,y-5.82,2.85), (1.6,.04,.28), window_warm)
    for wx in (-1.25,1.25):
        for wy in (-3.8,3.8):
            wh = cylinder(name+" wheel", (wx,y+wy,.62), .48,.22,black,16)
            wh.rotation_euler[1] = math.pi/2
    return base

bus = make_bus("TransJakarta articulated bus", -2.5, bus_red, bus_white)
key_location(bus, 1, (0,-2.5,1.65))
key_location(bus, FULL_FRAME_COUNT, (0,12,1.65))

# ---------- pedestrians ----------
def make_person(name, x, y, shirt):
    legs = []
    torso = cylinder(name+" torso", (x,y,1.12), .27, .85, shirt, 12)
    head = uv_sphere(name+" head", (x,y,1.85), (.23,.23,.25), skin)
    for dx in (-.13,.13):
        leg = cylinder(name+" leg", (x+dx,y,.48), .10,.75,blue,10)
        legs.append(leg)
    return torso

for i in range(18):
    px = random.choice([-7.8, 7.8]) + random.uniform(-.35,.35)
    py = random.uniform(-20, 34)
    make_person("Commuter", px, py, random.choice([shirt_blue,shirt_yellow,shirt_white,shirt_green]))

# ---------- MRT elevated structure in distance ----------
cube("MRT elevated viaduct", (0, 35, 9.0), (4.5, 45, .75), concrete2, .15)
for y in range(15, 56, 10):
    cube("MRT support pillar", (0,y,4.4), (.85,.85,8.7), concrete, .08)
mrt = cube("MRT train", (0,34,10.45), (2.5,15,2.2), white, .18)
for side in (-1,1):
    for i in range(6):
        cube("MRT train window", (side*1.27, 27.8+i*2.45, 10.75),
             (.04,1.9,.85), glass, .03)
key_location(mrt, 1, (0,34,10.45))
key_location(mrt, FULL_FRAME_COUNT, (0,10,10.45))

# ---------- camera ----------
bpy.ops.object.camera_add(location=(19,-30,18))
camera = bpy.context.object
camera.name = "Vertical cinematic camera"
target = Vector((0, 4, 5))
direction = target - camera.location
camera.rotation_euler = direction.to_track_quat('-Z','Y').to_euler()
camera.data.lens = 32
camera.data.dof.use_dof = False
scene.camera = camera

# Smooth camera push-in across full sequence.
camera.location = (19,-30,18)
camera.keyframe_insert(data_path="location", frame=1)
camera.location = (16,-17,15)
camera.keyframe_insert(data_path="location", frame=FULL_FRAME_COUNT)
target_obj = bpy.data.objects.new("Camera look target", None)
scene.collection.objects.link(target_obj)
target_obj.location = target
track = camera.constraints.new(type='TRACK_TO')
track.target = target_obj
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

# ---------- lighting and world ----------
world = bpy.data.worlds.new("Jakarta dusk sky") if not bpy.data.worlds else bpy.data.worlds[0]
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (.12,.17,.24,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = .45

bpy.ops.object.light_add(type='AREA', location=(2,-8,25))
key = bpy.context.object
key.name = "Large soft sunset"
key.data.energy = 4200
key.data.shape = 'DISK'
key.data.size = 18
key.rotation_euler = (math.radians(20),0,math.radians(20))

bpy.ops.object.light_add(type='AREA', location=(-15,10,12))
fill = bpy.context.object
fill.name = "Cool city fill"
fill.data.energy = 1800
fill.data.size = 14
fill.rotation_euler = (math.radians(25),0,math.radians(-35))

# ---------- title card in camera space ----------
def camera_text(body, name, y, size, material):
    curve = bpy.data.curves.new(name, type='FONT')
    curve.body = body
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.size = size
    curve.extrude = .002
    ob = bpy.data.objects.new(name, curve)
    scene.collection.objects.link(ob)
    ob.parent = camera
    ob.location = (0, y, -8)
    ob.data.materials.append(material)
    return ob

title_mat = mat("Overlay | white", (1,1,1), emission=1.0)
accent_mat = mat("Overlay | yellow", (1,.65,.08), emission=1.0)
title = camera_text("BAGAIMANA JIKA...", "Opening title", 3.25, .48, title_mat)
subtitle = camera_text("SELURUH WARGA JAKARTA\\nNAIK TRANSPORTASI UMUM?", "Question title", 2.45, .28, accent_mat)
# Hide opening text after first portion of the full animation.
for ob in (title, subtitle):
    ob.keyframe_insert(data_path="hide_render", frame=1)
    ob.hide_render = False
    ob.keyframe_insert(data_path="hide_render", frame=150)
    ob.hide_render = True
    ob.keyframe_insert(data_path="hide_render", frame=151)

# ---------- optional voice-over ----------
voice_candidates = [
    os.path.join(ROOT, "assets", "voiceover.mp3"),
    os.path.join(ROOT, "voiceover.mp3"),
]
voice_path = next((f for f in voice_candidates if os.path.isfile(f)), None)
if voice_path:
    try:
        if scene.sequence_editor is None:
            scene.sequence_editor_create()
        scene.sequence_editor.strips.new_sound(
            name="Voice Over", filepath=voice_path, channel=1, frame_start=1
        )
        print("Voice-over added:", voice_path)
    except Exception as exc:
        print("WARNING: Voice-over could not be added:", repr(exc))
else:
    print("INFO: No voiceover.mp3 found; rendering video frames without audio.")

# ---------- output and render ----------
# Do not use Action.fcurves: Blender 5 uses layered animation actions.
scene.frame_set(1)
scene.render.filepath = os.path.join(OUTPUT_DIR, "frame_")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Save a .blend file before rendering to help diagnose failures.
blend_path = os.path.join(ROOT, "output", "jakarta_whatif.blend")
os.makedirs(os.path.dirname(blend_path), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

print("==================================================")
print("STARTING JAKARTA WHAT-IF RENDER")
print("Blender:", bpy.app.version_string)
print("Frames:", scene.frame_start, "to", scene.frame_end)
print("Resolution:", scene.render.resolution_x, "x", scene.render.resolution_y)
print("Scale:", scene.render.resolution_percentage)
print("Samples:", RENDER_SAMPLES)
print("Output:", scene.render.filepath)
print("==================================================")

# Render animation to numbered PNG files.
bpy.ops.render.render(animation=True)

# Verify PNG output inside Blender as an early, clear failure.
pngs = [f for f in os.listdir(OUTPUT_DIR) if f.lower().endswith(".png")]
print("PNG frames written:", len(pngs))
if not pngs:
    raise RuntimeError("Blender finished without producing PNG frames in " + OUTPUT_DIR)

print("JAKARTA WHAT-IF RENDER COMPLETED")
