# Shared: bring the rigged HexBody into an exercise scene and drive it with that scene's skeleton.
import bpy, os
PRESERVE=False
# HEX_RIG picks the body (work/body_f/hexbody_rig.blend for the female one)
RIG=os.environ.get("HEX_RIG", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work", "body", "hexbody_rig.blend"))
def bring_hexbody(sc=None):
    sc=sc or bpy.context.scene
    arm=[o for o in sc.objects if o.type=='ARMATURE'][0]
    old=bpy.data.objects["Body"]
    with bpy.data.libraries.load(RIG, link=False) as (src, dst):
        dst.objects=["HexBody"]
    hb=dst.objects[0]; sc.collection.objects.link(hb)
    hb.parent=old.parent; hb.matrix_parent_inverse=old.matrix_parent_inverse.copy(); hb.matrix_basis=old.matrix_basis.copy()
    for m in hb.modifiers:
        if m.type=="ARMATURE": m.object=arm; m.use_deform_preserve_volume=PRESERVE
    old.hide_render=True; old.hide_viewport=True
    return hb, arm
