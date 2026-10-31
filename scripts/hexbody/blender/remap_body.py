# Bend the Meshy body into the skeleton's rest stance, then bind it to the skeleton.
# B = skeleton moved to where the joints sit inside the mesh; bone heat on B; per-bone affine B->A; bind to A.
import bpy, sys, numpy as np, time
from mathutils import Vector, Matrix, Quaternion
OUT = sys.argv[-1]
arm=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]
body=bpy.data.objects["HexBody"]; old=bpy.data.objects["Body"]
RW=arm.matrix_basis.copy(); RWi=RW.inverted()
A={b.name:(RW@b.head_local, RW@b.tail_local) for b in arm.data.bones}
co=np.array([v.co[:] for v in body.data.vertices])
def ball(sg):
    m=(co[:,2]<-1.10)&(np.abs(co[:,1]+0.09)<0.012)&(sg*co[:,0]>0.05)
    return Vector((float(co[m,0].mean()), -0.09, A["L_Foot"][0].z))
# joint centres inside the Meshy mesh (left side; the right is mirrored). HEX_JB=file.json overrides the male values.
import os, json
JL={"Knee":(0.139, 0.010, -0.660), "Ankle":(0.175, 0.050, -1.050), "Elbow":(0.405, 0.039, 0.189), "Wrist":(0.660, 0.034, 0.205)}
if os.environ.get("HEX_JB"): JL.update(json.load(open(os.environ["HEX_JB"])))
print("JB left", JL)
JB={}
for s,sg in (("L",1),("R",-1)):
    for k,(x,y,z) in JL.items(): JB[s+"_"+k]=Vector((sg*x, y, z))
    JB[s+"_Foot"]=ball(sg)
    JB[s+"_Hip"]=A[s+"_Hip"][0].copy(); JB[s+"_Shoulder"]=A[s+"_Shoulder"][0].copy()
print("balls", JB["L_Foot"], JB["R_Foot"])
def seg_T(h, c):
    """affine taking B segment (JB[h]->JB[c]) onto A segment, stretching along the bone only"""
    bh,bc=JB[h],JB[c]; ah,ac=A[h][0],A[c][0]
    u=(bc-bh); v=(ac-ah); k=v.length/u.length; u.normalize(); v.normalize()
    R=u.rotation_difference(v).to_matrix()
    S=Matrix.Identity(3)+(k-1)*Matrix([[u[i]*u[j] for j in range(3)] for i in range(3)])
    L=R@S
    return Matrix.Translation(ah)@L.to_4x4()@Matrix.Translation(-bh), R
T={}
for s in "LR":
    T[s+"_Hip"],_=seg_T(s+"_Hip",s+"_Knee")
    T[s+"_Knee"],_=seg_T(s+"_Knee",s+"_Ankle")
    T[s+"_Ankle"],Ra=seg_T(s+"_Ankle",s+"_Foot")
    T[s+"_Foot"]=Matrix.Translation(A[s+"_Foot"][0])@Ra.to_4x4()@Matrix.Translation(-JB[s+"_Foot"])
    T[s+"_Shoulder"],_=seg_T(s+"_Shoulder",s+"_Elbow")
    T[s+"_Elbow"],Re=seg_T(s+"_Elbow",s+"_Wrist")
    hand=Matrix.Translation(A[s+"_Wrist"][0])@Re.to_4x4()@Matrix.Translation(-JB[s+"_Wrist"])
    def walk(b):
        T[b.name]=hand
        for c in b.children: walk(c)
    walk(arm.data.bones[s+"_Wrist"])
for b in arm.data.bones: T.setdefault(b.name, Matrix.Identity(4))
# ---- armature B
B=arm.copy(); B.data=arm.data.copy(); B.name="ArmB"; bpy.context.scene.collection.objects.link(B)
B.animation_data_clear()
for o in bpy.context.selected_objects: o.select_set(False)
bpy.context.view_layer.objects.active=B; B.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
for eb in B.data.edit_bones: eb.use_connect=False
for eb in B.data.edit_bones:
    Ti=T[eb.name].inverted()
    eb.head=RWi@(Ti@A[eb.name][0]); eb.tail=RWi@(Ti@A[eb.name][1])
bpy.ops.object.mode_set(mode='OBJECT')
# ---- bone heat on B
body.parent=None; body.matrix_world=Matrix.Identity(4)
for m in list(body.modifiers): body.modifiers.remove(m)
body.vertex_groups.clear()
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True); B.select_set(True); bpy.context.view_layer.objects.active=B
t0=time.time(); bpy.ops.object.parent_set(type='ARMATURE_AUTO'); print("bone heat s", round(time.time()-t0,1))
names=[g.name for g in body.vertex_groups]; gi={g.index:g.name for g in body.vertex_groups}
n=len(body.data.vertices); W=np.zeros((n,len(names)),np.float32)
for v in body.data.vertices:
    for g in v.groups: W[v.index,g.group]=g.weight
tot=W.sum(1); print("verts without weight", int((tot<1e-6).sum()), "of", n)
# vertices without weight: copy from the nearest weighted vertex
if (tot<1e-6).any():
    from mathutils.kdtree import KDTree
    ok=np.where(tot>=1e-6)[0]; kd=KDTree(len(ok))
    for j,i in enumerate(ok): kd.insert(co[i],j)
    kd.balance()
    for i in np.where(tot<1e-6)[0]:
        _,j,_=kd.find(co[i]); W[i]=W[ok[j]]
    tot=W.sum(1)
W/=tot[:,None]
# ---- remap B rest -> A rest
P=np.hstack([co,np.ones((n,1))]); new=np.zeros((n,3))
for k,nm in enumerate(names):
    w=W[:,k]; m=w>0
    if not m.any(): continue
    Tm=np.array(T[nm]); new[m]+=w[m,None]*(P[m]@Tm.T)[:,:3]
print("max move m", float(np.linalg.norm(new-co,axis=1).max()).__round__(3))
# ---- bind to A with the same groups
body.parent=None
for m in list(body.modifiers): body.modifiers.remove(m)
for i,v in enumerate(body.data.vertices): v.co=new[i]
for g in body.vertex_groups: g.remove(range(n))
for k,nm in enumerate(names):
    g=body.vertex_groups[nm]; idx=np.where(W[:,k]>1e-4)[0]
    for i in idx: g.add([int(i)], float(W[i,k]), 'REPLACE')
bpy.data.objects.remove(B)
body.parent=old.parent; body.matrix_parent_inverse=old.matrix_parent_inverse.copy(); body.matrix_basis=old.matrix_basis.copy()
md=body.modifiers.new("Armature",'ARMATURE'); md.object=arm
old.hide_render=True; old.hide_viewport=True
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved", OUT)
