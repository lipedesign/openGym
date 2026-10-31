# Vertices and joint heads of a fitted body, for joints.py.
# Usage: Blender -b work/body_f/hexbody.blend -P blender/dump_body.py -- work/body_f/fit_verts.npz
import bpy, sys, numpy as np
o=bpy.data.objects["HexBody"]; co=np.array([(o.matrix_world@v.co)[:] for v in o.data.vertices])
arm=[a for a in bpy.data.objects if a.type=='ARMATURE'][0]; RW=arm.matrix_basis
J={b.name:list(RW@b.head_local) for b in arm.data.bones}
np.savez(sys.argv[-1], co=co, jn=np.array(list(J)), jh=np.array(list(J.values())))
print("verts", len(co))
