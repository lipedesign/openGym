import bpy, numpy as np, sys
o=bpy.data.objects["HexBody"]
co=np.array([v.co[:] for v in o.data.vertices]); nm=np.array([v.normal[:] for v in o.data.vertices])
np.save(sys.argv[-1], np.hstack([co,nm]))
