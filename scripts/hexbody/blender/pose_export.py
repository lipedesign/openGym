# Pose the rigged body like the MuscleMap figure (male: arms 17.4 deg from the body; female: 11.4 plus HEX_ELBOW=18) and export what the projection needs.
import bpy, sys, math, numpy as np
from mathutils import Matrix, Vector
ARMDEG=float(sys.argv[-2]); OUT=sys.argv[-1]
arm=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]; hb=bpy.data.objects["HexBody"]
Mw=arm.matrix_world.to_3x3().normalized()
def rot_world(name, axis, deg):
    pb=arm.pose.bones[name]; Ra=Mw.inverted()@Matrix.Rotation(math.radians(deg),3,axis)@Mw
    h=pb.head.copy(); pb.matrix=Matrix.Translation(h)@Ra.to_4x4()@Matrix.Translation(-h)@pb.matrix
    bpy.context.view_layer.update()
rot_world("L_Shoulder",'Y',90-ARMDEG); rot_world("R_Shoulder",'Y',-(90-ARMDEG))
# HEX_ELBOW: extra outward bend of the forearm, degrees (the female MuscleMap figure carries its forearms wider)
import os
EL=float(os.environ.get("HEX_ELBOW","0"))
if EL: rot_world("L_Elbow",'Y',-EL); rot_world("R_Elbow",'Y',EL)
dg=bpy.context.evaluated_depsgraph_get(); ev=hb.evaluated_get(dg); me=ev.to_mesh()
MW=hb.matrix_world
co=np.array([(MW@v.co)[:] for v in me.vertices]); nm=np.array([(MW.to_3x3()@v.normal).normalized()[:] for v in me.vertices])
assert all(len(p.vertices)==3 for p in me.polygons), 'HexBody must be triangulated'
vi=np.zeros(len(me.loops),np.int64); me.loops.foreach_get('vertex_index',vi); tris=vi.reshape(-1,3)   # corner order == loop order
ev.to_mesh_clear()
def grp(n):
    for s in "LR":
        if n in (s+"_Shoulder",s+"_Elbow",s+"_Wrist") or (n.startswith(s+"_") and any(k in n for k in ("Index","Middle","Ring","Pinky","Thumb"))): return "arm"+s
        if n in (s+"_Hip",s+"_Knee",s+"_Ankle",s+"_Foot"): return "leg"+s
    return "torso"
PARTS=["torso","armL","armR","legL","legR"]
gp={g.index:PARTS.index(grp(g.name)) for g in hb.vertex_groups}
acc=np.zeros((len(hb.data.vertices),5))
for v in hb.data.vertices:
    for g in v.groups: acc[v.index,gp[g.group]]+=g.weight
part=acc.argmax(1)
J={pb.name:list((arm.matrix_world@pb.head)) for pb in arm.pose.bones}
JT={pb.name:list((arm.matrix_world@pb.tail)) for pb in arm.pose.bones}
np.savez(OUT, tris=tris, co=co, nm=nm, part=part, jn=np.array(list(J)), jh=np.array(list(J.values())), jt=np.array(list(JT.values())))
print("parts", np.bincount(part), "z", co[:,2].min().round(3), co[:,2].max().round(3))
