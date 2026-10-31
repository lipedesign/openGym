# Triangulates HexBody so every face corner maps 1:1 to a triangle corner (corner attributes for the seams).
import bpy, bmesh
hb = bpy.data.objects["HexBody"]; me = hb.data
bm = bmesh.new(); bm.from_mesh(me)
bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
bm.to_mesh(me); bm.free(); me.update()
for p in me.polygons: p.use_smooth = True
print("polys", len(me.polygons), "all tris", all(len(p.vertices) == 3 for p in me.polygons), "verts", len(me.vertices))
bpy.ops.wm.save_mainfile()
