# Front/back orthographic renders of the posed body with a z ruler, to read landmark heights.
import bpy, sys, math
from mathutils import Matrix, Vector
OUT=sys.argv[-1]
arm=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]; hb=bpy.data.objects["HexBody"]; sc=bpy.context.scene
Mw=arm.matrix_world.to_3x3().normalized()
def rot_world(name, axis, deg):
    pb=arm.pose.bones[name]; Ra=Mw.inverted()@Matrix.Rotation(math.radians(deg),3,axis)@Mw
    h=pb.head.copy(); pb.matrix=Matrix.Translation(h)@Ra.to_4x4()@Matrix.Translation(-h)@pb.matrix
    bpy.context.view_layer.update()
rot_world("L_Shoulder",'Y',72.6); rot_world("R_Shoulder",'Y',-72.6)
for o in sc.objects:
    if o.type=='MESH' and o is not hb: o.hide_render=True
sc.render.engine='BLENDER_WORKBENCH'; sh=sc.display.shading; sh.light='STUDIO'; sh.color_type='SINGLE'; sh.single_color=(0.8,0.8,0.82); sh.show_cavity=True; sh.cavity_type='BOTH'
sc.view_settings.view_transform='Standard'
cd=bpy.data.cameras.new("c"); cd.type='ORTHO'; cd.ortho_scale=1.0; cam=bpy.data.objects.new("c",cd); sc.collection.objects.link(cam); sc.camera=cam
sc.render.resolution_x=1000; sc.render.resolution_y=1000
# torso window: z from -0.75 to +0.25
c=Vector((0,0,-0.25))
for name,az in [("front",0),("back",180)]:
    a=math.radians(az); d=Vector((math.sin(a),-math.cos(a),0))
    cam.location=c+d*10; cam.rotation_mode='QUATERNION'; cam.rotation_quaternion=(-d).to_track_quat('-Z','Y')
    sc.render.filepath=OUT+f"-{name}.png"; bpy.ops.render.render(write_still=True)
