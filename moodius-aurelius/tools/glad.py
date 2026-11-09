import numpy as np, wave, sys
SR=44100
def hz(m): return 440*2**((m-69)/12)
def env(n,a,r):
    e=np.ones(n); ai=min(int(a*SR),n); ri=min(int(r*SR),n)
    e[:ai]=np.linspace(0,1,ai)
    if ri: e[-ri:]*=np.linspace(1,0,ri)
    return e
def smooth(x,k): return np.convolve(x,np.ones(k)/k,mode="same")
def osc(freq_curve,weights,ph=0.0):
    phase=2*np.pi*np.cumsum(freq_curve)/SR+ph
    s=np.zeros_like(freq_curve)
    for k,w in enumerate(weights,1):
        if w: s+=w*np.sin(k*phase)
    return s
SAW=[1/k for k in range(1,11)]
def formant_weights(f0,formants=((700,1.0),(1150,0.6),(2800,0.15)),nh=14):
    w=[]
    for k in range(1,nh+1):
        f=k*f0; g=sum(a*np.exp(-((f-fc)/180)**2) for fc,a in formants)+0.08/k
        w.append(g)
    w=np.array(w); return list(w/w.max())
def make(var,dur,seed):
    rng=np.random.default_rng(seed)
    L=int(dur*SR); out=np.zeros(L); t_all=np.arange(L)/SR
    def add(sig,start,g=1.0):
        i=int(start*SR); j=min(L,i+len(sig))
        if j>i: out[i:j]+=g*sig[:j-i]
    if var=="A":   # Elysium-like: drone + choir + vocal lead, D minor
        bpm=66; chords=[[50,53,57],[46,50,53],[48,52,55],[50,53,57],[46,50,53],[43,46,50],[45,49,52],[50,53,57]]
        lead=[(0,74,3),(3,72,1),(4,70,2),(6,69,2),(8,70,3),(11,69,1),(12,67,2),(14,69,2),(16,65,4),(20,67,2),(22,69,2),(24,74,4),(28,72,4)]
        lead_start=2; ostinato=False; boom=False; lead_voice="vocal"
    elif var=="B": # intimate: F major / D dorian, cello lead, slower
        bpm=58; chords=[[53,57,60],[50,53,57],[46,50,53],[48,52,55],[53,57,60],[50,53,57],[46,50,53],[48,52,55]]
        lead=[(0,57,2),(2,60,2),(4,62,4),(8,60,2),(10,57,2),(12,55,4),(16,57,2),(18,62,2),(20,65,4),(24,64,2),(26,62,2),(28,60,4)]
        lead_start=1; ostinato=False; boom=False; lead_voice="cello"
    else:          # driving: D minor ostinato, low heartbeat boom, horns
        bpm=76; chords=[[50,53,57],[50,53,57],[46,50,53],[48,52,55],[50,53,57],[46,50,53],[43,46,50],[45,49,52]]
        lead=[(0,62,2),(2,65,2),(4,69,4),(8,67,2),(10,65,2),(12,64,4),(16,65,2),(18,69,2),(20,74,4),(24,72,2),(26,70,2),(28,69,4)]
        lead_start=1; ostinato=True; boom=True; lead_voice="horn"
    beat=60/bpm; bar=4*beat
    # low drone on D throughout
    drone=osc(np.full(L,hz(38)),[1,0.5,0.25,0.12])+osc(np.full(L,hz(45)),[0.5,0.2])
    out+=drone*0.05*env(L,3.0,0.01)
    # strings / choir pad
    nb=int(np.ceil(dur/bar))+1
    for b in range(nb):
        ch=chords[b%len(chords)]; st=b*bar; d=bar+1.2; n=int(d*SR); t=np.arange(n)/SR
        sw=0.55+0.45*min(1,b/3)
        for m in ch+[ch[0]+12]:
            for det in (-0.07,0.0,0.06):
                f=hz(m+det)*(1+0.004*np.sin(2*np.pi*(5+rng.random())*t+rng.random()*6))
                if var=="B": s=osc(f,SAW[:6])
                else: s=osc(f,formant_weights(hz(m)))   # choir-ish "aah"
                add(smooth(s,7)*env(n,1.2,1.2),st,0.028*sw)
    # lead melody with portamento + vibrato
    lv_oct={"vocal":0,"cello":-12,"horn":-12}[lead_voice]
    notes=[(lead_start*bar+b4*beat,m+lv_oct,ln*beat) for b4,m,ln in lead]
    if notes:
        s0=notes[0][0]; e0=min(dur,notes[-1][0]+notes[-1][2])
        n=int((e0-s0)*SR); t=np.arange(n)/SR
        fc=np.zeros(n); amp=np.zeros(n)
        for st,m,ln in notes:
            i=int((st-s0)*SR); j=min(n,int((st-s0+ln)*SR)); 
            if i>=n: break
            fc[i:j]=hz(m); seg=j-i
            a=np.ones(seg); ai=min(int(0.15*SR),seg); ri=min(int(0.2*SR),seg)
            a[:ai]=np.linspace(0.3,1,ai); a[-ri:]*=np.linspace(1,0.55,ri); amp[i:j]=a
        fc[fc==0]=np.nan
        idx=np.arange(n); good=~np.isnan(fc); fc=np.interp(idx,idx[good],fc[good])
        fc=smooth(fc,int(0.09*SR))  # glide between notes
        vib=1+0.006*np.sin(2*np.pi*5.3*t)*np.clip(t/0.8,0,1)
        f=fc*vib
        if lead_voice=="vocal": w=formant_weights(np.median(fc),((800,1.0),(1200,0.5),(2900,0.12)))
        elif lead_voice=="cello": w=[1,0.7,0.5,0.35,0.25,0.18,0.12,0.08]
        else: w=[1,0.8,0.55,0.35,0.2,0.1]
        s=smooth(osc(f,w),9)*smooth(amp,int(0.05*SR))
        add(s,s0,0.11 if lead_voice!="horn" else 0.09)
        if lead_voice=="horn": add(smooth(osc(f/2,w),11)*smooth(amp,int(0.05*SR)),s0,0.06)
    # cello ostinato (variation C)
    if ostinato:
        for b in range(1,nb):
            ch=chords[b%len(chords)]
            for e8 in range(8):
                st=b*bar+e8*beat/2; n=int(beat/2*0.8*SR); t=np.arange(n)/SR
                m=ch[0]-12 if e8 not in (3,6) else ch[0]-5
                s=osc(np.full(n,hz(m)),SAW[:8])*env(n,0.01,0.08)*np.exp(-t*2.5)
                add(smooth(s,5),st,0.075*(1.0 if e8%2==0 else 0.7))
    # soft low heartbeat boom, pure tone, no noise/snare (variation C)
    if boom:
        for b in range(2,nb):
            for off in (0,beat*0.6):
                n=int(0.9*SR); t=np.arange(n)/SR
                f=hz(26)*(1+0.5*np.exp(-t*18))
                s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*4.5)
                add(s,b*bar+off,0.32 if off==0 else 0.2)
    # hall reverb
    irn=int(2.6*SR); ti=np.arange(irn)/SR
    ir=rng.standard_normal(irn)*np.exp(-ti*2.2); ir=smooth(ir,24); ir/=np.abs(ir).sum()/6
    nfft=1<<int(np.ceil(np.log2(L+irn)))
    wet=np.fft.irfft(np.fft.rfft(out,nfft)*np.fft.rfft(ir,nfft),nfft)[:L]
    mix=out*0.7+wet*0.5
    # no ending: gentle 1.2s fade-out only, plus 0.6s fade-in
    mix*=env(L,0.6,1.2)
    mix/=np.max(np.abs(mix))/0.89
    st=np.stack([mix,np.roll(mix,int(0.011*SR))],1)
    return st
var,dur,seed,path=sys.argv[1],float(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
st=make(var,dur,seed)
w=wave.open(path,"wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((st*32767).astype(np.int16).tobytes()); w.close(); print(path,dur)
