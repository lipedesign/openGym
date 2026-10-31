# Load the exercise scene, strip the motion, import the Meshy body and fit it to the SMPL-H rest skeleton.
import bpy, sys, os, math, numpy as np
from mathutils import Vector, Matrix
argv=sys.argv[sys.argv.index("--")+1:]; GLB, OUTBLEND, OUTPNG = argv
sc=bpy.context.scene
arm=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]
old=bpy.data.objects["Body"]
for o in bpy.data.objects: o.animation_data_clear()
bpy.data.objects["Fix"].matrix_world=Matrix.Identity(4)
for pb in arm.pose.bones:
    for c in list(pb.constraints): pb.constraints.remove(c)
    pb.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()
RW=arm.matrix_basis
J={b.name: RW@b.head_local for b in arm.data.bones}
JT={b.name: RW@b.tail_local for b in arm.data.bones}
oc=np.array([v.co[:] for v in old.data.vertices])
before=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=GLB)
new=[o for o in bpy.data.objects if o not in before and o.type=='MESH'][0]
new.name="HexBody"
for o in list(bpy.data.objects):
    if o not in before and o is not new and o.type=='EMPTY' and not o.children: bpy.data.objects.remove(o)
new.parent=None
M=new.matrix_world.copy(); new.data.transform(M); new.matrix_world=Matrix.Identity(4)
co=np.array([v.co[:] for v in new.data.vertices])
lo,hi=co.min(0),co.max(0)
olo,ohi=oc.min(0),oc.max(0)
s=(ohi[2]-olo[2])/(hi[2]-lo[2])
# horizontal centre: midpoint in x; depth: match the torso depth centre at chest height of the old body
def ymid(c,z0,z1):
    m=(c[:,2]>z0)&(c[:,2]<z1)&(np.abs(c[:,0])<0.15); return (c[m,1].min()+c[m,1].max())/2
co_s=co*s; lo_s=co_s.min(0)
t=np.array([-(co_s[:,0].min()+co_s[:,0].max())/2, 0, olo[2]-lo_s[2]])
co_s=co_s+t
t[1]=ymid(oc,-0.1,0.15)-ymid(co_s,-0.1,0.15)
new.data.transform(Matrix.Translation(Vector(t.tolist()))@Matrix.Scale(s,4))
co=np.array([v.co[:] for v in new.data.vertices])
print("scale",round(s,4),"t",t.round(3),"bbox",co.min(0).round(3),co.max(0).round(3))
# islands
import bmesh
bm=bmesh.new(); bm.from_mesh(new.data)
print("nonmanifold edges", sum(1 for e in bm.edges if not e.is_manifold), "loose verts", sum(1 for v in bm.verts if not v.link_edges))
bm.free()
# overlay: joints as spheres, render front + side
old.hide_render=True
for o in bpy.data.objects:
    if o.type=='MESH' and o not in (new,): o.hide_render=True
mj=bpy.data.materials.new("J"); mj.use_nodes=True
nt=mj.node_tree; nt.nodes.clear(); e=nt.nodes.new("ShaderNodeEmission"); e.inputs[0].default_value=(1,0.1,0.05,1); out=nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(e.outputs[0],out.inputs[0])
for n,p in J.items():
    if any(k in n for k in ("Index","Middle","Ring","Pinky","Thumb")): continue
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.012, location=p, segments=12, ring_count=8)
    o=bpy.context.active_object; o.name="J_"+n; o.data.materials.append(mj); o.show_in_front=True
mb=bpy.data.materials.new("B"); mb.use_nodes=True; mb.blend_method='BLEND' if hasattr(mb,'blend_method') else None
mb.node_tree.nodes.clear(); bsdf=mb.node_tree.nodes.new("ShaderNodeBsdfPrincipled"); mo=mb.node_tree.nodes.new("ShaderNodeOutputMaterial"); mb.node_tree.links.new(bsdf.outputs[0],mo.inputs[0]); bsdf.inputs["Base Color"].default_value=(0.8,0.8,0.85,1); bsdf.inputs["Alpha"].default_value=0.35
if hasattr(mb,'surface_render_method'): mb.surface_render_method='BLENDED'
new.data.materials.clear(); new.data.materials.append(mb)
sc.render.engine='BLENDER_EEVEE' if 'BLENDER_EEVEE' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE_NEXT'
for o in list(bpy.data.objects):
    if o.type=='LIGHT': bpy.data.objects.remove(o)
ld=bpy.data.lights.new("s",'SUN'); ld.energy=3; lo_=bpy.data.objects.new("s",ld); sc.collection.objects.link(lo_); lo_.rotation_euler=(0.6,0.2,0.3)
sc.world.node_tree.nodes["Background"].inputs[1].default_value=0.6
cd=bpy.data.cameras.new("c"); cd.type='ORTHO'; cd.ortho_scale=1.95
cam=bpy.data.objects.new("c",cd); sc.collection.objects.link(cam); sc.camera=cam
sc.render.resolution_x=1400; sc.render.resolution_y=1400; sc.render.film_transparent=False
sc.eevee.taa_render_samples=8
c=Vector((0,0,(co[:,2].min()+co[:,2].max())/2))
for name,az in [("front",0),("side",90)]:
    a=math.radians(az); d=Vector((math.sin(a),-math.cos(a),0))
    cam.location=c+d*10; cam.rotation_mode='QUATERNION'; cam.rotation_quaternion=(-d).to_track_quat('-Z','Y')
    sc.render.filepath=OUTPNG+f"-{name}.png"; bpy.ops.render.render(write_still=True)
# clean overlay helpers before saving
for o in list(bpy.data.objects):
    if o.name.startswith("J_") or o.name in ("c","s"): bpy.data.objects.remove(o)
new.data.materials.clear()
bpy.ops.wm.save_as_mainfile(filepath=OUTBLEND)
