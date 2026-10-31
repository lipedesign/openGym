# Debug view: every MuscleMap piece in its own colour on the posed body.
import bpy, os, sys, math, colorsys, numpy as np
from mathutils import Matrix, Vector
argv=sys.argv[sys.argv.index("--")+1:]; LAB, OUT = argv[0], argv[1]
lab=np.load(LAB)
arm=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]; hb=bpy.data.objects["HexBody"]; sc=bpy.context.scene
Mw=arm.matrix_world.to_3x3().normalized()
def rot_world(name, axis, deg):
    pb=arm.pose.bones[name]; Ra=Mw.inverted()@Matrix.Rotation(math.radians(deg),3,axis)@Mw
    h=pb.head.copy(); pb.matrix=Matrix.Translation(h)@Ra.to_4x4()@Matrix.Translation(-h)@pb.matrix
    bpy.context.view_layer.update()
rot_world("L_Shoulder",'Y',68); rot_world("R_Shoulder",'Y',-68)
me=hb.data
ca=me.color_attributes.new("lab",'FLOAT_COLOR','POINT')
import json
TAB={t["id"]:t for t in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "musclemap", "labels.json")))["table"]}
GC={"chest":"e6194b","deltoids":"f58231","biceps":"ffe119","triceps":"bfef45","forearm":"3cb44b","abs":"42d4f4","obliques":"4363d8",
    "serratus":"911eb4","trapezius":"f032e6","upper-back":"7b68ee","lower-back":"469990","gluteal":"fabed4","quadriceps":"9a6324",
    "adductors":"dcbeff","hamstring":"800000","calves":"808000","tibialis":"ffd8b1","hip-flexors":"aaffc3","neck":"a9a9a9"}
SUBV={"upperChest":1.0,"lowerChest":0.75,"frontDeltoid":1.0,"rearDeltoid":0.7,"upperAbs":1.0,"lowerAbs":0.7,"innerQuad":1.0,"outerQuad":0.7,
      "upperTrapezius":1.0,"lowerTrapezius":0.65,"rhomboids":1.0,"rotatorCuff":0.65}
def col(i):
    t=TAB.get(int(i),{}); g=t.get("group")
    if g not in GC: return (0.92,0.92,0.94,1)
    h=GC[g]; c=[int(h[k:k+2],16)/255 for k in (0,2,4)]; v=SUBV.get(t["slug"],0.88)
    c=[(x*v)**2.2 for x in c]; return (c[0],c[1],c[2],1)
cols=np.array([col(int(i)) for i in lab],np.float32)
ev=np.zeros(len(me.edges)*2,np.int64); me.edges.foreach_get("vertices",ev); ev=ev.reshape(-1,2)
diff=lab[ev[:,0]]!=lab[ev[:,1]]; border=np.zeros(len(lab),bool); border[ev[diff].ravel()]=True
cols[border]=(0.12,0.11,0.16,1)
ca.data.foreach_set("color",cols.ravel())
me.color_attributes.active_color=ca
sc.render.engine='BLENDER_WORKBENCH'; sh=sc.display.shading; sh.light='FLAT'; sc.view_settings.view_transform='Standard'; sh.color_type='VERTEX'; sh.show_cavity=True; sh.cavity_type='WORLD'
for o in sc.objects:
    if o.type=='MESH' and o is not hb: o.hide_render=True
cd=bpy.data.cameras.new("c"); cd.type='ORTHO'; cd.ortho_scale=1.95; cam=bpy.data.objects.new("c",cd); sc.collection.objects.link(cam); sc.camera=cam
sc.render.resolution_x=1350; sc.render.resolution_y=1500; sc.render.film_transparent=False
c=Vector((0,0,-0.27))
for name,az in [("front",0),("back",180),("side",90),("q34",35)]:
    a=math.radians(az); d=Vector((math.sin(a),-math.cos(a),0.05))
    cam.location=c+d*10; cam.rotation_mode='QUATERNION'; cam.rotation_quaternion=(-d).to_track_quat('-Z','Y')
    sc.render.filepath=OUT+f"-{name}.png"; bpy.ops.render.render(write_still=True)
