import glob, uproot, numpy as np
f=glob.glob("/exp/dune/data/users/smanthey/gun_test/"+__import__("sys").argv[1]+"/gun_*_hist.root")[0]; print(f)
r=uproot.open(f); c=r["solarnuana/ConfigTree"]
print({k: c[k].array(library="np")[0] for k in ["SignalLabel","SaveClusterEDep","SaveSignalEDep","ClusterAlgoTime","ClusterAlgoAdjChannel","AdjClusterRad","OpFlashAlgoPE"] if k in c.keys()})
t=r["solarnuana/MCTruthTree"]; print("MCTruth entries", t.num_entries)
a=t.arrays(["SignalParticleK","SignalHitEDep","SignalHitNElectrons","TSignalEDepList","TSignalPDG","TSignalMother","SignalIDEEDep","SignalIDENElectrons"],library="np")
for i in range(t.num_entries):
    print(" ev",i,"K",round(float(a["SignalParticleK"][i]),3),"EDep(IDE sum)",round(float(np.sum(a["TSignalEDepList"][i])),3),"HitEDep",np.round(a["SignalHitEDep"][i],3),"IDEEDep",np.round(a["SignalIDEEDep"][i],3),"nPart",len(a["TSignalPDG"][i]),"PDGs",sorted(set(a["TSignalPDG"][i].tolist())))
s=r["solarnuana/SolarNuAnaTree"]; print("clusters", s.num_entries)
b=s.arrays(["Event","Primary","NHits","Charge","SignalEDep","SignalNElectrons","Purity"],library="np")
for i in range(s.num_entries): print("  cl ev",b["Event"][i],"prim",b["Primary"][i],"nh",b["NHits"][i],"Q",round(float(b["Charge"][i]),1),"EDep",round(float(b["SignalEDep"][i]),3),"Nel",round(float(b["SignalNElectrons"][i])),"pur",round(float(b["Purity"][i]),2))
