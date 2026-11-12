
import bpy
import math
import os
import random
from mathutils import Vector

random.seed(41)

ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(ROOT, "output", "frames")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =====================================================
# RESET AND RENDER SETUP
# =====================================================

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

scene = bpy.context.scene

scene.render.engine = (
    'BLENDER_EEVEE_NEXT'
    if 'BLENDER_EEVEE_NEXT' in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items.keys()
    else 'BLENDER_EEVEE'
)

# FAST RENDER SETTINGS
# Override with environment variables when needed:
# RENDER_SCALE=50 (half width/height), RENDER_SAMPLES=8
# RENDER_TEST_FRAMES=20 renders only the first 20 frames for benchmarking.
RENDER_SCALE = max(25, min(100, int(os.environ.get("RENDER_SCALE", "50"))))
RENDER_SAMPLES = max(1, min(64, int(os.environ.get("RENDER_SAMPLES", "8"))))
RENDER_TEST_FRAMES = int(os.environ.get("RENDER_TEST_FRAMES", "0"))

if hasattr(scene, 'eevee') and hasattr(scene.eevee, 'taa_render_samples'):
    scene.eevee.taa_render_samples = RENDER_SAMPLES

scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.resolution_percentage = RENDER_SCALE
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = min(2276, RENDER_TEST_FRAMES) if RENDER_TEST_FRAMES > 0 else 2276

# Avoid unnecessary per-frame compositor work on the CPU-only GitHub runner.
# The scene remains lit by its materials and lights; only the extra Fog Glow is skipped.
scene.render.use_compositing = False

# Render PNG sequence
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.filepath = os.path.join(OUTPUT_DIR, "frame_")

scene.view_settings.view_transform = 'AgX'
# Compositing disabled above for faster CPU rendering.

# =====================================================
# MATERIALS
# =====================================================

def mat(name, color, metal=0, rough=.55, emission=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)

    # Blender creates shader nodes for new materials
    nt = m.node_tree
    p = nt.nodes.get('Principled BSDF')

    if p:
        p.inputs['Base Color'].default_value = (*color, 1)
        p.inputs['Metallic'].default_value = metal
        p.inputs['Roughness'].default_value = rough

        if emission:
            p.inputs['Emission Color'].default_value = (*color, 1)
            p.inputs['Emission Strength'].default_value = emission

    return m


asphalt = mat('Road | textured charcoal', (.055, .068, .082), rough=.9)
curb = mat('Sidewalk | warm stone', (.34, .34, .31))
concrete = mat('Architecture | warm graphite', (.12, .16, .2))
concrete2 = mat('Architecture | slate', (.19, .22, .24))
glass = mat('Blue reflective glass', (.025, .105, .16), .45, .22)
window_on = mat('Warm illuminated windows', (1, .64, .29), .15, .3, 1.4)
window_cool = mat('Cool illuminated windows', (.35, .64, .82), .15, .25, .65)
lane = mat('Road markings', (.88, .84, .7), rough=.5)
green = mat('Median grass', (.12, .29, .16))
leaf = mat('Tree foliage', (.14, .34, .2))
leaf2 = mat('Tree foliage highlights', (.23, .43, .24))
bark = mat('Tree bark', (.19, .105, .065))
red = mat('Car | crimson', (.62, .075, .055), .25, .28)
blue = mat('Car | midnight blue', (.045, .15, .34), .35, .25)
