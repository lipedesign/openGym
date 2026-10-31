# Joint centres measured from cross-sections, checked against the male body (whose JB were set by hand).
# Usage: python3 blender/joints.py work/body_f/fit_verts.npz work/body/fit_verts.npz
# Prints leg and arm cross-sections; the joint centres picked from them go in joints_<fig>.json (HEX_JB for remap_body.py).
import sys, numpy as np
np.set_printoptions(precision=3, suppress=True)
def prof_leg(co, sg, zs):
    out=[]
    for z in zs:
        m=(np.abs(co[:,2]-z)<0.004)&(sg*co[:,0]>0.01)
        if m.sum()<8: out.append((z,np.nan,np.nan,np.nan,np.nan)); continue
        c=co[m]; out.append((z,c[:,0].max()-c[:,0].min(),c[:,1].max()-c[:,1].min(),(c[:,0].max()+c[:,0].min())/2,(c[:,1].max()+c[:,1].min())/2))
    return np.array(out)
def prof_arm(co, sg, xs):
    out=[]
    for x in xs:
        m=(np.abs(sg*co[:,0]-x)<0.004)&(co[:,2]>0.0)
        if m.sum()<8: out.append((x,np.nan,np.nan,np.nan,np.nan)); continue
        c=co[m]; out.append((x,c[:,2].max()-c[:,2].min(),c[:,1].max()-c[:,1].min(),(c[:,2].max()+c[:,2].min())/2,(c[:,1].max()+c[:,1].min())/2))
    return np.array(out)
for name in sys.argv[1:]:
    d=np.load(name); co=d["co"]
    print("==", name, "z", co[:,2].min().round(3), co[:,2].max().round(3), "x", co[:,0].max().round(3))
    zs=np.arange(-1.12,-0.40,0.01); P=prof_leg(co,1,zs)
    print(" leg L  z    wx    dy    cx    cy")
    for r in P[::2]: print("  ", r)
    xs=np.arange(0.24,0.82,0.01); A=prof_arm(co,1,xs)
    print(" arm L  x    hz    dy    cz    cy")
    for r in A[::2]: print("  ", r)
