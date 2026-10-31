# Uniform remesh of the rigged body (voxel), weights carried over from the original.
import bpy, sys, time
VOX=float(sys.argv[-2]); OUT=sys.argv[-1]
arm=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]; hb=bpy.data.objects["HexBody"]
for m in hb.modifiers: m.show_viewport=False; m.show_render=False
src=hb.copy(); src.data=hb.data.copy(); src.name="HexSrc"; bpy.context.scene.collection.objects.link(src)
for m in list(src.modifiers): src.modifiers.remove(m)
new=hb.copy(); new.data=hb.data.copy(); new.name="HexNew"; bpy.context.scene.collection.objects.link(new)
for m in list(new.modifiers): new.modifiers.remove(m)
new.vertex_groups.clear()
bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active=new; new.select_set(True)
t=time.time()
rm=new.modifiers.new("R",'REMESH'); rm.mode='VOXEL'; rm.voxel_size=VOX; rm.adaptivity=0; rm.use_smooth_shade=True
bpy.ops.object.modifier_apply(modifier="R")
sw=new.modifiers.new("SW",'SHRINKWRAP'); sw.target=src; sw.wrap_method='NEAREST_SURFACEPOINT'
bpy.ops.object.modifier_apply(modifier="SW")
print("remesh s", round(time.time()-t,1), "verts", len(new.data.vertices))
# weights
dt=new.modifiers.new("DT",'DATA_TRANSFER'); dt.object=src; dt.use_vert_data=True; dt.data_types_verts={'VGROUP_WEIGHTS'}
dt.vert_mapping='POLYINTERP_NEAREST'; dt.layers_vgroup_select_src='ALL'; dt.layers_vgroup_select_dst='NAME'
bpy.ops.object.datalayout_transfer(modifier="DT")
bpy.ops.object.modifier_apply(modifier="DT")
print("groups", len(new.vertex_groups))
# swap in
name=hb.name; parent=hb.parent; pinv=hb.matrix_parent_inverse.copy(); mb=hb.matrix_basis.copy()
bpy.data.objects.remove(hb); bpy.data.objects.remove(src)
new.name=name; new.data.name="HexBody"
new.parent=parent; new.matrix_parent_inverse=pinv; new.matrix_basis=mb
md=new.modifiers.new("Armature",'ARMATURE'); md.object=arm
for p in new.data.polygons: p.use_smooth=True
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("saved")
