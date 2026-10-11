import glob, uproot, numpy as np, sys
f=glob.glob("/exp/dune/data/users/smanthey/gun_test/"+sys.argv[1]+"/gun_*_hist.root")[0]
t=uproot.open(f)["solarnuana/MCTruthTree"]
a=t.arrays(["SignalParticleX","SignalParticleY","SignalParticleZ","SignalParticleTime","TSignalPDG","TSignalEndX","TSignalEndY","TSignalEndZ","TSignalE","TSignalMother"],library="np")
for i in range(t.num_entries):
    print(i, "vtx", round(float(a["SignalParticleX"][i]),1), round(float(a["SignalParticleY"][i]),1), round(float(a["SignalParticleZ"][i]),1), "t", a["SignalParticleTime"][i], "first end", np.round([a["TSignalEndX"][i][0],a["TSignalEndY"][i][0],a["TSignalEndZ"][i][0]],1), "daughters of primary:", [(int(p),round(float(e),2)) for p,e,m in zip(a["TSignalPDG"][i],a["TSignalE"][i],a["TSignalMother"][i]) if m==1][:6])
