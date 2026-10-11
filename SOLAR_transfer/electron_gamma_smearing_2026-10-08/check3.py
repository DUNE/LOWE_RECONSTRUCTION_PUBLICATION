import glob, uproot, numpy as np, sys
f=glob.glob("/exp/dune/data/users/smanthey/gun_test/"+sys.argv[1]+"/gun_*_hist.root")[0]
r=uproot.open(f); t=r["solarnuana/MCTruthTree"]
a=t.arrays(["SignalParticleX","SignalParticleY","SignalParticleZ","TSignalPDG","TSignalE","TSignalK","TSignalMother","TSignalID","TSignalT","TSignalEndX","SignalIDEEDep","SignalHitEDep"],library="np")
for i in range(t.num_entries):
    pdg=a["TSignalPDG"][i]; mom=a["TSignalMother"][i]; K=a["TSignalK"][i]; T=a["TSignalT"][i]; ids=a["TSignalID"][i]
    # capture gammas: gammas whose mother is the neutron track (ID 1)
    g=(pdg==22)&(mom==1)
    nuc=[(int(p),round(float(tt)/1e3,1)) for p,m,tt in zip(pdg,mom,T) if m==1 and p>1000000000]
    print(i,"vtx",np.round([a["SignalParticleX"][i],a["SignalParticleY"][i],a["SignalParticleZ"][i]],0),"n end x",round(float(a["TSignalEndX"][i][0]),0),
          "capture gammas",np.round(np.sort(K[g])[::-1],3).tolist(),"sum",round(float(K[g].sum()),3),"t_capture(us)",np.round(T[g][:1]/1e3,1),"nuclei",nuc[:3],
          "IDE col",round(float(a["SignalIDEEDep"][i][2]),2),"Hits col",round(float(a["SignalHitEDep"][i][2]),2))
s=r["solarnuana/SolarNuAnaTree"]; b=s.arrays(["Event","Primary","NHits","Charge","SignalEDep","Time","MainTime"],library="np")
for i in range(s.num_entries): print("  cl ev",b["Event"][i],"prim",b["Primary"][i],"nh",b["NHits"][i],"Q",round(float(b["Charge"][i]),0),"EDep",round(float(b["SignalEDep"][i]),2),"T",round(float(b["Time"][i]),0),"MainT",round(float(b["MainTime"][i])/1e3,0))
