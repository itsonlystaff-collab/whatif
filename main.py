import bpy, math, os, random
from mathutils import Vector
random.seed(41)
ROOT=os.path.dirname(os.path.abspath(__file__))
# ---------- reset and render setup ----------
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.materials,bpy.data.curves,bpy.data.cameras,bpy.data.lights):
    pass
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items.keys() else 'BLENDER_EEVEE'
RENDER_SAMPLES = max(1, min(64, int(os.environ.get('RENDER_SAMPLES', '4'))))
if hasattr(scene,'eevee') and hasattr(scene.eevee,'taa_render_samples'): scene.eevee.taa_render_samples=RENDER_SAMPLES
RENDER_SCALE = max(25, min(100, int(os.environ.get('RENDER_SCALE', '35'))))
scene.render.resolution_x=1080; scene.render.resolution_y=1920; scene.render.resolution_percentage=RENDER_SCALE
scene.render.fps=30; scene.frame_start=1; scene.frame_end=2276
# Render PNG frames: some Ubuntu Blender builds (including Blender 5) omit FFmpeg support.
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGB'
scene.view_settings.view_transform='AgX'
scene.render.filepath=os.path.join(ROOT,'output','frames','frame_'); os.makedirs(os.path.dirname(scene.render.filepath),exist_ok=True)
# ---------- materials ----------
def mat(name,color,metal=0,rough=.55,emission=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    if emission:
        p.inputs['Emission Color'].default_value=(*color,1); p.inputs['Emission Strength'].default_value=emission
    return m
asphalt=mat('Road | textured charcoal',(.055,.068,.082),rough=.9); curb=mat('Sidewalk | warm stone',(.34,.34,.31)); concrete=mat('Architecture | warm graphite',(.12,.16,.2)); concrete2=mat('Architecture | slate',(.19,.22,.24)); glass=mat('Blue reflective glass',(.025,.105,.16),.45,.22); window_on=mat('Warm illuminated windows',(1,.64,.29),.15,.3,1.4); window_cool=mat('Cool illuminated windows',(.35,.64,.82),.15,.25,.65); lane=mat('Road markings',(.88,.84,.7),rough=.5); green=mat('Median grass',(.12,.29,.16)); leaf=mat('Tree foliage',(.14,.34,.2)); leaf2=mat('Tree foliage highlights',(.23,.43,.24)); bark=mat('Tree bark',(.19,.105,.065)); red=mat('Car | crimson',(.62,.075,.055),.25,.28); blue=mat('Car | midnight blue',(.045,.15,.34),.35,.25); ivory=mat('Car | pearl',(.68,.7,.67),.28,.25); black=mat('Rubber',(.012,.016,.02),.05,.8); metal=mat('Brushed metal',(.42,.5,.54),.72,.25); busred=mat('TransJakarta red',(.78,.035,.045),.22,.27); buswhite=mat('Transit white',(.82,.85,.83),.18,.25); skin=mat('Skin',(.57,.32,.2)); clothes=[mat('Clothing '+str(i),c) for i,c in enumerate([(.08,.18,.3),(.56,.18,.1),(.16,.32,.22),(.55,.43,.25),(.22,.22,.27)])]
# ---------- geometry helpers ----------
def cube(name,loc,scale,material,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if material:o.data.materials.append(material)
    if bevel:
        b=o.modifiers.new('Precision rounded edges','BEVEL'); b.width=bevel; b.segments=3
        o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return o
def cyl(name,loc,r,depth,material,vertices=16,rot=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(material)
    if rot:o.rotation_euler=rot
    return o
def sphere(name,loc,scale,material,segments=12,rings=8):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=1,location=loc); o=bpy.context.object; o.name=name; o.scale=scale; o.data.materials.append(material); return o
def aim(o,target): o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
# ---------- city street stage ----------
cube('Large city ground',(0,0,-.55),(42,70,.65),mat('Ground',(.075,.09,.095)))
cube('Main boulevard',(0,0,-.19),(12,72,.22),asphalt)
# central planted divider and sidewalks
cube('Green median',(-.02,0,-.035),(1.0,72,.18),green)
for x in (-6.65,6.65): cube('Wide pedestrian sidewalk',(x,0,-.06),(1.3,72,.28),curb,.05)
for y in range(-34,36,4):
    for x in (-4.55,-2.2,2.2,4.55): cube('Dashed lane line',(x,y,.0),(.10,1.9,.025),lane)
for side in (-1,1):
    for y in range(-32,34,8): cube('Zebra crossing stripe',(side*5.2,y,.015),(.8,3,.035),lane)
# city blocks with architectural ledges, facade grids, varied windows
for side in (-1,1):
  for i,y in enumerate(range(-29,32,10)):
    x=side*random.uniform(10.2,13.2); h=random.uniform(13,25); w=random.uniform(6.5,8.5); d=8.5
    base=cube('Jakarta tower',(x,y,h/2-.2),(w,d,h),random.choice([concrete,concrete2]),.10)
    cube('Tower podium',(x,y,1.0),(w+1,d+.7,2),concrete2,.08)
    # front facade facing boulevard
    face=x-side*(w/2+.025)
    for z in [2.7,4.8,6.9,9,11.1,13.2,15.3,17.4,19.5,21.6,23.7]:
      if z<h-.3:
       for yy in [y-3.1,y-1.05,y+1.05,y+3.1]:
        if random.random()>.14:
         wm=random.choice([window_on,window_cool,glass]); cube('Individual facade glazing',(face,yy,z),(.045,1.2,1.25),wm,.015)
    # roof parapet and side fins
    cube('Roof parapet',(x,y,h+.02),(w+.2,d+.2,.35),concrete2,.04)
    for yy in [y-d*.38,y+d*.38]: cube('Facade vertical fin',(face-.03,yy,h*.52),(.16,.12,h*.9),metal,.025)
# overhead elevated rail / station structure on one side
cube('Elevated rail deck',(7.9,0,7.0),(2.4,70,.42),concrete2,.08)
for y in range(-32,34,9):
    cube('Elevated rail support',(7.9,y,3.45),(.58,.72,7.1),concrete2,.08)
    cube('Support capital',(7.9,y,6.65),(3.1,1.0,.45),concrete2,.08)
for x in (7.25,8.55): cube('Steel rail',(x,0,7.28),(.14,70,.15),metal,.025)
# overhead street gantry and lamps
for y in (-23,-4,15):
    cyl('Streetlight pole',(6.0,y,4.0),.095,8,metal,12)
    cube('Streetlight arm',(5.2,y,7.85),(1.7,.12,.12),metal,.04)
    sphere('Warm street lamp',(4.45,y,7.78),(.22,.22,.11),mat('Lamp glow',(1,.72,.38),emission=3))
    # gantry across roadway, with hanging traffic cameras
    cube('Traffic gantry beam',(0,y,9.2),(13,.22,.22),metal,.04)
    for x in (-4.8,-1.8,1.8,4.8):
        cube('Traffic camera arm',(x,y,8.8),(.12,.12,.8),metal)
        cube('Traffic camera housing',(x,y,8.35),(.55,.45,.32),concrete2,.06)
# ---------- trees, planters, benches and people ----------
for side in (-1,1):
  for y in range(-29,32,7):
    x=side*6.55
    cube('Tree planter',(x,y,.12),(1.0,1.1,.25),curb,.08)
    cyl('Tree trunk',(x,y,1.15),.18,2.0,bark,12)
    sphere('Tree crown',(x,y,2.45),(1.0,.95,1.05),leaf,10,7)
    sphere('Tree crown highlight',(x-.35,y-.12,2.75),(.58,.62,.62),leaf2,10,7)
# benches
for y in (-18,0,18):
    cube('Park bench seat',(6.55,y,.72),(1.0,1.8,.16),bark,.05)
    cube('Park bench back',(6.55,y,1.2),(.14,1.8,.8),bark,.04)
# people with body, head, legs and arms
def person(x,y,scale=1.0,cloth=None):
    cloth=cloth or random.choice(clothes)
    cube('Pedestrian torso',(x,y,1.05*scale),(.42*scale,.28*scale,.72*scale),cloth,.09)
    sphere('Pedestrian head',(x,y,1.58*scale),(.19*scale,.19*scale,.22*scale),skin)
    for dx in (-.13,.13):
        cyl('Pedestrian leg',(x+dx*scale,y,.48*scale),.075*scale,.62*scale,black,10)
        cyl('Pedestrian arm',(x+dx*1.8*scale,y,1.05*scale),.065*scale,.62*scale,skin,10,(0,0,math.radians(10)))
for i in range(30):
    side=random.choice([-1,1]); person(side*random.uniform(5.8,6.7),random.uniform(-30,30),random.uniform(.82,1.08))
# ---------- detailed vehicles ----------
def car(name,x,y,body,length=3.2,width=1.48):
    # front points toward negative Y
    cube(name+' lower body',(x,y,.68),(width,length,.62),body,.22)
    cube(name+' hood',(x,y-length*.32,.94),(width*.96,length*.32,.22),body,.12)
    cube(name+' roof',(x,y+.12,1.22),(width*.78,length*.42,.48),body,.16)
    cube(name+' windshield',(x,y-length*.12,1.25),(width*.76,.06,.36),glass,.025)
    cube(name+' rear glass',(x,y+length*.31,1.25),(width*.72,.06,.32),glass,.025)
    for yy in (y-length*.06,y+length*.25):
      for xx in (x-width*.505,x+width*.505): cube(name+' side window',(xx,yy,1.24),(.035,.55,.32),glass,.015)
    for yy in (y-length*.31,y+length*.31):
      for xx in (x-width*.54,x+width*.54):
       cyl(name+' tire',(xx,yy,.43),.29,.16,black,16,(0,math.pi/2,0))
       cyl(name+' alloy hub',(xx+(-.09 if xx<x else .09),yy,.43),.15,.025,metal,12,(0,math.pi/2,0))
    for xx in (x-width*.31,x+width*.31):
      cube(name+' headlamp',(xx,y-length*.51,.76),(.25,.035,.14),mat(name+' headlamp glow',(1,.82,.55),emission=2.0),.03)
      cube(name+' tail lamp',(xx,y+length*.51,.78),(.22,.035,.13),red,.025)
    return cube(name+' chassis',(x,y,.55),(width*.75,length*.7,.12),black)
# initially many private cars, then visually sparse as public transit becomes dominant
for i in range(10):
    x=random.choice([-4.0,-2.2,2.2,4.0]); y=-27+i*5.8
    ob=car('Private vehicle '+str(i),x,y,random.choice([red,blue,ivory]))
    # animate the chassis and all objects grouped by parent-like location not used; whole car collection via nearby named objs
    for obj in bpy.data.objects:
        if obj.name.startswith(('Private vehicle '+str(i))):
            obj.keyframe_insert(data_path='location',frame=1); obj.location.y+=random.uniform(4,13); obj.keyframe_insert(data_path='location',frame=2276)
# detailed TransJakarta buses
for idx,y in enumerate((-19,9,29)):
    x=2.25
    bus=cube('TransJakarta articulated bus '+str(idx),(x,y,1.15),(1.9,8.2,2.1),busred,.18)
    cube('Bus window band',(x,y,1.55),(1.94,6.6,.72),glass,.04)
    for yy in [y-3.1,y-1.55,y, y+1.55,y+3.1]:
      cube('Bus window mullion',(x,yy,1.55),(2.0,.08,.78),metal,.015)
    cube('Bus lower white stripe',(x,y,.62),(1.94,7.9,.22),buswhite,.04)
    for yy in (y-2.8,y+2.8):
      for xx in (x-.85,x+.85): cyl('Bus wheel',(xx,yy,.48),.34,.16,black,16,(0,math.pi/2,0))
    bus.keyframe_insert(data_path='location',frame=1); bus.location.y+=16; bus.keyframe_insert(data_path='location',frame=2276)
# elevated MRT train with multiple cars
for idx,y in enumerate((-15,0,15)):
    train=cube('MRT carriage '+str(idx),(7.9,y,8.35),(1.55,9.0,1.8),buswhite,.22)
    cube('MRT dark window ribbon',(7.9,y,8.58),(1.58,7.5,.78),glass,.08)
    for yy in [y-3.0,y-1.5,y,y+1.5,y+3.0]: cube('MRT window divider',(7.9,yy,8.58),(1.6,.07,.82),metal,.015)
    train.keyframe_insert(data_path='location',frame=1); train.location.y+=22; train.keyframe_insert(data_path='location',frame=2276)
# bicycles parked near the greenway
for i in range(4):
    x=5.85; y=-15+i*3
    for yy in (y-.55,y+.55):
        bpy.ops.mesh.primitive_torus_add(major_radius=.34,minor_radius=.045,major_segments=16,minor_segments=6,location=(x,yy,.45),rotation=(math.pi/2,0,0)); bpy.context.object.name='Bicycle wheel'; bpy.context.object.data.materials.append(black)
    cyl('Bicycle frame tube',(x,y,.78),.035,.9,metal,8,(math.pi/2,0,0))
# ---------- camera and cinematic text ----------
bpy.ops.object.camera_add(location=(0,-26,15)); cam=bpy.context.object; cam.name='Vertical cinematic camera'; cam.data.lens=43; cam.data.sensor_fit='VERTICAL'; cam.data.sensor_height=36; scene.camera=cam
shots=[(1,(0,-25,16),(0,-1,2)),(380,(0,-13,13),(0,3,2)),(760,(3,-7,12),(2,3,3)),(1140,(6,-10,14),(6,2,6)),(1520,(0,-12,16),(0,2,2)),(1900,(1,-6,13),(2,5,2)),(2276,(0,-23,19),(0,0,2))]
for f,loc,target in shots:
    cam.location=loc; aim(cam,target); cam.keyframe_insert(data_path='location',frame=f); cam.keyframe_insert(data_path='rotation_euler',frame=f)
# overlay materials and camera-facing text
def emission(name,color):
 m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear(); out=nt.nodes.new('ShaderNodeOutputMaterial'); e=nt.nodes.new('ShaderNodeEmission'); e.inputs[0].default_value=(*color,1); e.inputs[1].default_value=1; nt.links.new(e.outputs[0],out.inputs['Surface']); return m
white_text=emission('Overlay | ivory',(1,.97,.88)); mint=emission('Overlay | mint',(.32,.92,.72)); panelmat=emission('Overlay | deep green',(.018,.075,.065)); orange=emission('Overlay | amber',(1,.48,.19))
def text_obj(body,name,loc,size,material):
    c=bpy.data.curves.new(name,'FONT'); c.body=body; c.size=size; c.extrude=0; c.align_x='LEFT'; o=bpy.data.objects.new(name,c); scene.collection.objects.link(o); o.parent=cam; o.location=loc; o.data.materials.append(material); return o
def panel(name,loc,scale,material):
    o=cube(name,(0,0,0),(1,1,1),material); o.parent=cam; o.location=loc; o.scale=scale; return o
# top editorial strip + large headline
panel('Top title panel',(0,3.15,-8),(2.0,.62,.012),panelmat)
text_obj('WHAT IF?  |  JAKARTA', 'Top label',(-1.72,3.33,-7.98),.15,mint)
text_obj('SEMUA NAIK', 'Headline line 1',(-1.72,3.04,-7.98),.23,white_text)
text_obj('TRANSPORTASI UMUM?', 'Headline line 2',(-1.72,2.77,-7.98),.18,white_text)
# bottom subtitles with active time ranges
subs=[
(1,250,'Bagaimana jika seluruh warga Jakarta\nmemilih transportasi umum?','KOTA BERGERAK BERSAMA'),
(251,510,'MRT, KRL, dan TransJakarta\nmenjadi pilihan utama masyarakat.','TRANSPORTASI PUBLIK'),
(511,770,'Kemacetan berkurang drastis.\nPolusi udara mulai menurun.','JALANAN LEBIH LENGANG'),
(771,1020,'Pengeluaran bahan bakar berkurang.\nWaktu menjadi lebih produktif.','WAKTU KEMBALI BERHARGA'),
(1021,1280,'Ruang parkir berubah menjadi taman.\nTrotoar dan jalur sepeda bertambah.','RUANG KOTA UNTUK MANUSIA'),
(1281,1530,'Udara terasa lebih segar.\nJakarta menjadi lebih sehat.','JAKARTA LEBIH HIJAU'),
(1531,1780,'Jakarta bukan lagi kota\nuntuk menghabiskan waktu dalam macet.','KOTA YANG BERUBAH'),
(1781,2020,'Melainkan kota tempat\norang menikmati perjalanan.','MENIKMATI PERJALANAN'),
(2021,2276,'Perubahan besar dimulai dari keputusan sederhana:\nmemilih transportasi umum.','MULAI DARI PILIHAN KITA')]
for i,(a,b,caption,tag) in enumerate(subs):
    bg=panel('Subtitle background '+str(i),(0,-2.8,-8),(2.0,.64,.012),panelmat)
    tx=text_obj(caption,'Subtitle '+str(i),(-1.72,-2.88,-7.98),.145,white_text)
    tg=text_obj(tag,'Chapter '+str(i),(-1.70,-2.35,-7.98),.105,mint)
    for ob in (bg,tx,tg):
        ob.hide_render=True; ob.keyframe_insert(data_path='hide_render',frame=1)
        ob.hide_render=False; ob.keyframe_insert(data_path='hide_render',frame=a)
        ob.hide_render=True; ob.keyframe_insert(data_path='hide_render',frame=b+1)
# ---------- lighting, atmosphere and sound ----------
world=scene.world or bpy.data.worlds.new('Dusk city world'); scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[0].default_value=(.035,.055,.085,1); world.node_tree.nodes['Background'].inputs[1].default_value=.55
bpy.ops.object.light_add(type='AREA',location=(-3,-4,25)); key=bpy.context.object; key.name='Large softbox key'; key.data.energy=5200; key.data.shape='DISK'; key.data.size=18; aim(key,(0,0,0))
bpy.ops.object.light_add(type='AREA',location=(13,5,14)); rim=bpy.context.object; rim.name='Cool architectural rim'; rim.data.energy=2600; rim.data.color=(.42,.62,1.0); rim.data.size=12; aim(rim,(0,0,3))
bpy.ops.object.light_add(type='AREA',location=(-12,-12,10)); fill=bpy.context.object; fill.name='Warm street fill'; fill.data.energy=1900; fill.data.color=(1.0,.63,.38); fill.data.size=10; aim(fill,(0,0,0))
# subtle compositor glow for lamps and highlights
# Blender 5.0.1: nonaktifkan compositor untuk menghindari error node_tree
scene.render.use_compositing = False
# audio
scene.sequence_editor_create(); audio=os.path.join(ROOT,'assets','voiceover.mp3')
if os.path.exists(audio): scene.sequence_editor.strips.new_sound('Original Indonesian voice-over',audio,channel=1,frame_start=1)
# linear camera and object motion; smooth ease
for ob in bpy.data.objects:
    if ob.animation_data and ob.animation_data.action:
# Blender 5.0.1 compatible interpolation
if ob.animation_data and ob.animation_data.action:
    action = ob.animation_data.action

    if hasattr(action, "fcurves"):
        for fc in action.fcurves:
            for key in fc.keyframe_points:
                key.interpolation = 'BEZIER'
    else:
  # Blender 5.0 layered Action API
        try:
            for layer in action.layers:
                for strip in layer.strips:
                    if hasattr(strip, "channelbag"):
                        bag = strip.channelbag(ob)
                        if bag:
                            for fc in bag.fcurves:
                                for key in fc.keyframe_points:
                                    key.interpolation = 'BEZIER'
        except Exception as e:
            print("Interpolation adjustment skipped:", e)
            for kp in fc.keyframe_points: kp.interpolation='BEZIER'
scene.render.image_settings.color_mode='RGB'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'jakarta_whatif.blend'))
bpy.ops.render.render(animation=True)
