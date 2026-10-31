# HexGym muscle body: relaxed A-pose, every muscle drawn, optional activation.
# Usage: Blender -b work/body/hexbody_rig.blend -P blender/bodymodel.py --<clay|flat|line> <front|back|side|q34|q34b> <activation> <out.png> [res] [samples]
import bpy, sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hexlib as H, bodylook as BL
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view
argv = sys.argv[sys.argv.index("--") + 1:]
STYLE, VIEW, ACT, OUT = argv[0], argv[1], argv[2], argv[3]
RES = int(argv[4]) if len(argv) > 4 else 1080
SAMPLES = int(argv[5]) if len(argv) > 5 else 32
sc = bpy.context.scene
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
body = bpy.data.objects["HexBody"]
for o in bpy.data.objects:
    if o.type == 'MESH' and o is not body: o.hide_render = True
BL.load_fields(body, ACT)
Mw = arm.matrix_world.to_3x3().normalized()
def rot_world(name, axis, deg):
    pb = arm.pose.bones[name]; Ra = Mw.inverted() @ Matrix.Rotation(math.radians(deg), 3, axis) @ Mw
    h = pb.head.copy(); pb.matrix = Matrix.Translation(h) @ Ra.to_4x4() @ Matrix.Translation(-h) @ pb.matrix
    bpy.context.view_layer.update()
rot_world("L_Shoulder", 'Y', 66); rot_world("R_Shoulder", 'Y', -66)
rot_world("L_Elbow", 'Z', -10); rot_world("R_Elbow", 'Z', 10)
# camera fitted to the body
VIEWS = {"front": (0, 3), "back": (180, 3), "q34": (34, 6), "q34b": (214, 6), "side": (90, 3)}
def body_points(step=23):
    dg = bpy.context.evaluated_depsgraph_get(); ev = body.evaluated_get(dg); m_ = ev.to_mesh()
    pts = [body.matrix_world @ m_.vertices[i].co for i in range(0, len(m_.vertices), step)]
    ev.to_mesh_clear(); return pts
P3 = body_points()
lo = Vector((min(p.x for p in P3), min(p.y for p in P3), min(p.z for p in P3)))
hi = Vector((max(p.x for p in P3), max(p.y for p in P3), max(p.z for p in P3)))
ctr = (lo + hi) / 2
az, el = (math.radians(a) for a in VIEWS[VIEW])
cdir = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
cd = bpy.data.cameras.new("ModelCam"); cd.lens = 85
cam = bpy.data.objects.new("ModelCam", cd); sc.collection.objects.link(cam); sc.camera = cam
half = 18 / 85; dist = 6.0
for _ in range(4):
    cam.location = ctr + cdir * dist; cam.rotation_mode = 'QUATERNION'
    cam.rotation_quaternion = (ctr - cam.location).to_track_quat('-Z', 'Y'); bpy.context.view_layer.update()
    pr = [world_to_camera_view(sc, cam, p) for p in P3]
    x0, x1 = min(c.x for c in pr), max(c.x for c in pr); y0, y1 = min(c.y for c in pr), max(c.y for c in pr)
    ctr = ctr + cam.rotation_quaternion @ Vector(((x0 + x1) / 2 - 0.5, (y0 + y1) / 2 - 0.5, 0)) * (2 * dist * half)
    dist *= max(x1 - x0, y1 - y0) / 0.92
cam.location = ctr + cdir * dist; cam.rotation_quaternion = (ctr - cam.location).to_track_quat('-Z', 'Y')
bpy.context.view_layer.update(); cam_q = cam.matrix_world.to_quaternion()
for o in list(bpy.data.objects):
    if o.type == 'LIGHT': bpy.data.objects.remove(o, do_unlink=True)
def light(kind, d_cam, energy, size=1.0, angle=0.6, offset=None):
    ld = bpy.data.lights.new(kind, kind); ld.energy = energy
    if kind == 'SUN': ld.angle = math.radians(angle)
    else: ld.size = size
    o = bpy.data.objects.new(kind, ld); sc.collection.objects.link(o)
    d = (cam_q @ Vector(d_cam)).normalized()
    o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, -1)).rotation_difference(d)
    if offset is not None: o.location = ctr - d * offset
    return o
wn = sc.world.node_tree.nodes["Background"]; wn.inputs["Strength"].default_value = 0.0
body.data.materials.clear()
for m in list(body.modifiers):
    if m.type == 'SOLIDIFY': body.modifiers.remove(m)
if os.environ.get("HEX_ANCHORS"):
    # per-vertex screen position, depth and facing, for labelling the plates
    import numpy as np
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get(); ev = body.evaluated_get(dg); m_ = ev.to_mesh()
    MW = body.matrix_world; N3 = MW.to_3x3().inverted().transposed(); camp = cam.matrix_world.translation
    uv, dep, fac, cw = [], [], [], []
    for v in m_.vertices:
        w = MW @ v.co; c = world_to_camera_view(sc, cam, w)
        uv.append((c.x, 1 - c.y)); dep.append(c.z); cw.append(w[:])
        fac.append((N3 @ v.normal).dot(camp - w) > 0)
    ev.to_mesh_clear()
    np.savez(os.path.splitext(OUT)[0] + "_anchors.npz", uv=np.array(uv), dep=np.array(dep), fac=np.array(fac), co=np.array(cw))
sc.view_settings.view_transform = 'Standard'; sc.view_settings.exposure = 0.0
if STYLE == "clay":
    body.data.materials.append(BL.mat_clay('#E9E5EF', '#B4A8FF', '#6A57FF', 0.75))
    light('AREA', (0.55, -0.45, -0.7), 380, 2.5, offset=4.0)
    light('AREA', (-0.8, -0.1, -0.6), 110, 3.0, offset=4.0)
    light('AREA', (-0.2, 0.6, 0.75), 420, 1.5, offset=4.0).data.color = H.lin('#9D8CFF')[:3]
    wn.inputs["Color"].default_value = H.lin('#2A2638'); wn.inputs["Strength"].default_value = 0.6
    sc.view_settings.exposure = -0.45
elif STYLE == "flat":
    C = dict(base=('#ECE8F3', '#B3ABC9'), sec=('#C3BAFF', '#9A8EEA'), prim=('#8B7BFF', '#6A57EE'))
    body.data.materials.append(BL.mat_flat(C))
    H.outline(body, H.mat_hull("Ink", H.lin('#07060C')), 0.005)
    light('SUN', (0.5, -0.5, -0.7), 3.4).data.use_shadow = False   # toon reads N.L only; shadow maps band
else:
    body.data.materials.append(BL.mat_line('#100E19', '#463E80', '#8B7BFF', '#5E5873', '#CFCBDA'))
    H.outline(body, H.mat_hull("Chalk", H.lin('#F2EFE9')), 0.0045)
sm = body.modifiers.new("Smooth", 'SUBSURF'); sm.levels = 0; sm.render_levels = 0
sc.render.engine = 'BLENDER_EEVEE' if 'BLENDER_EEVEE' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE_NEXT'
sc.render.use_compositing = False; sc.render.film_transparent = True
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
sc.render.resolution_x = sc.render.resolution_y = RES; sc.render.resolution_percentage = 100
sc.eevee.taa_render_samples = SAMPLES
if hasattr(sc.eevee, 'use_raytracing'): sc.eevee.use_raytracing = False
pts = []
for p in body_points(5):
    if p.z < lo.z + 0.05:
        c = world_to_camera_view(sc, cam, Vector((p.x, p.y, lo.z))); pts.append((c.x, 1 - c.y))
foot = dict(x0=min(p[0] for p in pts), x1=max(p[0] for p in pts), y0=min(p[1] for p in pts), y1=max(p[1] for p in pts)) if pts else None
with open(os.path.splitext(OUT)[0] + ".json", "w") as fh: json.dump(dict(foot=foot, view=VIEW, act=ACT, style=STYLE), fh)
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
