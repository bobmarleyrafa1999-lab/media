import subprocess, textwrap, os, sys
OUT="/mnt/project-files/moodius-aurelius/reels"
SERIF="/usr/share/fonts/truetype/freefont/FreeSerif.ttf"
SERIFB="/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"
if not os.path.exists(SERIFB): SERIFB="/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
REELS={
 "reel-1-control":[
  ("You're stressed about things\nyou can't control.",3.2,True),
  ("Marcus Aurelius ruled an empire.",2.6,False),
  ("Plague. War. Betrayal.",2.4,False),
  ("So he wrote himself one rule:",2.6,False),
  ("Some things are up to you.\nMost aren't.",3.2,True),
  ("Your judgments. Your actions.\nYour effort.",3.0,False),
  ("Everything else?\nLet it go.",3.0,True),
  ("Follow for one Stoic rule a day.",3.0,False)],
 "reel-2-evening-review":[
  ("Marcus Aurelius did this every night.\nIt takes 5 minutes.",3.4,True),
  ("Before bed, ask yourself:",2.4,False),
  ("1. What did I do well today?",2.8,False),
  ("2. Where did I fall short?",2.8,False),
  ("3. What will I do differently\ntomorrow?",3.2,False),
  ("No guilt.\nJust honesty.",2.8,True),
  ("Save this for tonight.",3.0,False)],
 "reel-3-disrespect":[
  ("Someone disrespected you today?",3.0,True),
  ("The Stoics had a simple test.",2.6,False),
  ("Is what they said true?\nThen why be angry at the truth?",3.4,False),
  ("Is it false?\nThen it's their mistake, not yours.",3.4,False),
  ("Either way,\nyour peace stays yours.",3.2,True),
  ("Send this to someone who needs it.",3.0,False)],
}
def esc(s): return s.replace("\\","\\\\").replace(":","\\:").replace("'","\u2019").replace("%","\\%").replace(",","\\,")
for name,segs in REELS.items():
    total=sum(d for _,d,_ in segs)+0.5
    filt=[]
    # background: dark stone texture with slow drift and vignette
    bg=(f"color=c=0x1b1d1f:s=1080x1920:d={total},format=yuv420p,"
        f"noise=alls=28:allf=t,boxblur=6:1,eq=contrast=1.15:brightness=-0.02,"
        f"scale=1240:2204,crop=1080:1920:x='80+60*sin(t/9)':y='140+80*t/{total}',vignette=PI/4")
    v="[bg]"
    filt.append(bg+v)
    t=0.25; chain=v; i=0
    for text,d,big in segs:
        lines=text.split("\n")
        fs=78 if big else 64
        font=SERIFB if big else SERIF
        lh=fs*1.3
        y0=960-lh*len(lines)/2
        a=f"if(lt(t-{t:.2f},0.35),(t-{t:.2f})/0.35,if(gt(t-{t:.2f},{d-0.35:.2f}),({t+d:.2f}-t)/0.35,1))"
        for j,ln in enumerate(lines):
            nxt=f"[v{i}]"
            filt.append(f"{chain}drawtext=fontfile={font}:text='{esc(ln)}':fontsize={fs}:fontcolor=0xEDE6D6:"
                        f"x=(w-text_w)/2:y={y0+j*lh:.0f}:alpha='{a}':enable='between(t,{t:.2f},{t+d:.2f})':"
                        f"shadowcolor=black@0.6:shadowx=2:shadowy=3{nxt}")
            chain=nxt; i+=1
        t+=d
    # persistent identity: monogram rule + handle
    filt.append(f"{chain}drawtext=fontfile={SERIFB}:text='M · A':fontsize=44:fontcolor=0xC9A86A@0.85:x=(w-text_w)/2:y=230,"
                f"drawbox=x=440:y=300:w=200:h=2:color=0xC9A86A@0.7:t=fill,"
                f"drawtext=fontfile={SANS}:text='@moodiusaurelius':fontsize=38:fontcolor=0xEDE6D6@0.75:x=(w-text_w)/2:y=1640[vout]")
    # ambient drone audio, generated
    aud=(f"aevalsrc='0.10*sin(2*PI*55*t)*(0.7+0.3*sin(2*PI*0.2*t))+0.06*sin(2*PI*82.5*t)+0.03*sin(2*PI*110*t)':s=44100:d={total},"
         f"afade=t=in:d=1.5,afade=t=out:st={total-1.5}:d=1.5[aout]")
    filt.append(aud)
    cmd=["ffmpeg","-y","-loglevel","error","-filter_complex",";".join(filt),"-map","[vout]","-map","[aout]",
         "-r","30","-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","128k",
         "-movflags","+faststart",f"{OUT}/{name}.mp4"]
    r=subprocess.run(cmd,capture_output=True,text=True)
    print(name, total, r.returncode, r.stderr[-800:])
