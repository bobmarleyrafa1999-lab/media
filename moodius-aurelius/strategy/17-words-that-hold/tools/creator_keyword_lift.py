import sqlite3,re,statistics as st,sys,json
c=sqlite3.connect(sys.argv[1])
rows=c.execute("""select v.creator,v.outlier_ratio,coalesce(h.hook_text,v.title,'') ,v.title,v.cover_text from videos v left join hooks h on h.video_id=v.id
 where v.outlier_ratio is not null and h.relevant=1""").fetchall()
print('n',len(rows))
# cap extreme outliers via log
import math
data=[(cr,min(o,50),(t or '')+' ') for cr,o,t,ti,cv in rows]
allmed=st.median([o for _,o,_ in data]); print('median all',allmed)
feat={
 'you/your (2nd person)':r'\byou(r|\'re)?\b',
 'why':r'\bwhy\b','how':r'\bhow\b','what':r'\bwhat\b','question mark':r'\?',
 'stop / never / don\'t':r'\b(stop|never|don.?t)\b',
 'secret / truth / real / actually':r'\b(secret|truth|real|actually|really)\b',
 'named thinker':r'(marcus|aurelius|seneca|epictetus|jung|nietzsche|machiavelli|stoic)',
 'number / list':r'\b(\d+|three|five|seven|ten)\b',
 'hurt/pain/lonely (pain words)':r'(hurt|pain|lonel|broken|alone|ignored|sabotage|hatred|hate)',
 'vs / more than':r'(\bvs\b|more than)',
 'people / someone / they':r'\b(people|someone|they|them|manipulator|others)\b',
 'psycholog/brain/therap':r'(psycholog|brain|therap|science|stud)',
 'cost / why it still':r'(cost|still)',
 'lonely/alone':r'(lonel|alone)','why you keep / why you':r'why you','silence/quiet':r'(silence|quiet)','ALL CAPS word':r'\b[A-Z]{4,}\b',
}
out=[]
for k,p in feat.items():
  w=[o for _,o,t in data if re.search(p,t,re.I if k!='ALL CAPS word' else 0)]
  wo=[o for _,o,t in data if not re.search(p,t,re.I if k!='ALL CAPS word' else 0)]
  creators=len({cr for cr,o,t in data if re.search(p,t,re.I if k!='ALL CAPS word' else 0)})
  if len(w)>=3: out.append((k,len(w),creators,round(st.median(w),2),round(st.median(wo),2)))
for r in sorted(out,key=lambda r:-r[3]): print(r)
