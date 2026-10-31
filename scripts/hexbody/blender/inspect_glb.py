import bpy, sys, math, numpy as np
from mathutils import Vector
argv=sys.argv[sys.argv.index("--")+1:]; GLB, OUT = argv[0], argv[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
ms=[o for o in bpy.data.objects if o.type=='MESH']
print("objects", [(o.name,o.type,len(o.data.vertices) if o.type=='MESH' else 0) for o in bpy.data.objects])
o=ms[0]
co=np.array([(o.matrix_world@v.co)[:] for v in o.data.vertices])
print("bbox", co.min(0).round(3), co.max(0).round(3), "faces", len(o.data.polygons))
sc=bpy.context.scene
sc.render.engine='BLENDER_WORKBENCH'
sc.display.shading.light='STUDIO'; sc.display.shading.color_type='SINGLE'
sc.display.shading.single_color=(0.85,0.84,0.88)
sc.display.shading.show_cavity=True; sc.display.shading.cavity_type='BOTH'
sc.render.resolution_x=1600; sc.render.resolution_y=1000
lo,hi=co.min(0),co.max(0); c=Vector(((lo+hi)/2).tolist()); H=float(hi[2]-lo[2]); W=float(hi[0]-lo[0])
cd=bpy.data.cameras.new("c"); cd.type='ORTHO'; cd.ortho_scale=max(H*1.05*1.6, W*1.1)
cam=bpy.data.objects.new("c",cd); sc.collection.objects.link(cam); sc.camera=cam
sc.render.film_transparent=False
import os
for name,az in [("front",0),("back",180),("side",90)]:
    a=math.radians(az); d=Vector((math.sin(a),-math.cos(a),0))
    cam.location=c+d*10; cam.rotation_mode='QUATERNION'; cam.rotation_quaternion=(-d).to_track_quat('-Z','Y')
    sc.render.filepath=OUT+f"-{name}.png"; bpy.ops.render.render(write_still=True)
