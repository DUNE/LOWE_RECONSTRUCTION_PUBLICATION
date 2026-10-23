"""Statistical precision on the hep normalisation mu (Asimov Fisher information).
n_i = mu s_i + beta b_i, beta with Gaussian prior sigma_b; all bins (0-30 MeV) with raw b_i>0 (MC-supported, as the hep mask).
Inputs: plotting-repo HEP_Counts.pkl (raw spectra at the selected cuts, events/MeV/20 yr)."""
import pickle, numpy as np
base='input/data/studies/truncated/default/'
cfgs=['hd_1x2x6_centralAPA','hd_1x2x6_lateralAPA','vd_1x8x14_3view_30deg_nominal','vd_1x8x14_3view_30deg_shielded']
for sb in (0.02,):
  for T in (5,10,20,100/4.56):
    Itot=0
    for c in cfgs:
        d=pickle.load(open(base+c+'_marley_HEP_Counts.pkl','rb')); r=d[d.SpectrumType=='Raw']
        E=np.array(r.iloc[0].Energy); comp={x.Component:np.array(x.Counts)*T/20 for x in r.itertuples()}
        s=comp['hep']; b=sum(v for k,v in comp.items() if k!='hep')
        m=(b>0); s,b=s[m],b[m]; n=s+b
        F=np.array([[np.sum(s*s/n),np.sum(s*b/n)],[np.sum(s*b/n),np.sum(b*b/n)+1/sb**2]])
        sig=np.sqrt(np.linalg.inv(F)[0,0]); Itot+=1/sig**2
        print(f'T={T} {c:32s} N_hep={s.sum():7.2f} sigma_mu={sig:.3f}')
    print(f'T={T} combined sigma_mu={1/np.sqrt(Itot):.3f}')
