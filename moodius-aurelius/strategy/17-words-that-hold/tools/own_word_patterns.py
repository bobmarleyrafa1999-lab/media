import re,statistics as st
# hook, reach, 3s%, avgwatch, likes, saves, shares (Metricool pull 24 Oct 2026)
R=[("They got away with it. You didn't.",159,23.7,2.53,2,0,0),
("Asking for help isn't weak.",126,22.1,2.94,7,1,0),
("Three signs you're regulating, not suppressing.",189,29.7,4.21,5,1,0),
("It's not what happened that hurts. It's the story you tell about it.",141,43.1,4.4,7,2,1),
("Busy all day. Nothing done.",23,31.8,3.89,4,0,0),
("You can't make everyone like you.",106,46.8,5.41,11,0,0),
("The fastest way to lose an argument? Get angry.",109,45.5,4.22,5,1,0),
("Marcus Aurelius said this to himself every morning, before he saw anyone.",140,25.2,3.92,7,0,0),
("5 things you can't control",211,17.9,2.83,4,0,1),
("Motivation isn't coming.",20,29.2,4.39,3,0,0),
("Not every insult deserves a reply.",121,43.1,5.04,7,1,1),
("3 Stoic rules for overthinkers.",122,24.8,5.73,4,0,0),
("Marcus Aurelius did this every night. It takes 5 minutes.",32,30.3,4.28,3,0,0),
("Someone disrespected you today?",117,37.0,16.54,4,0,0),
("Some things are up to you. Most aren't.",114,34.7,5.43,4,2,4)]
F={'second person (you/your)':r"\byou",'negation (not/isn\'t/can\'t/no)':r"\b(not|isn't|can't|didn't|nothing|no)\b|n't",
'other person / conflict':r"(someone|insult|argument|everyone|they|angry|disrespect|like you|got away)",
'named thinker':r"(marcus|stoic|epictetus|seneca)",'number / list':r"(\b\d\b|three|five)",
'question mark':r"\?",'two-beat turn (. then short line)':r"\.\s+\S",'abstract self-help noun':r"(motivation|busy|rules|signs|things)"}
for k,p in F.items():
  w=[r for r in R if re.search(p,r[0],re.I)]; wo=[r for r in R if not re.search(p,r[0],re.I)]
  m=lambda xs,i: round(st.median([x[i] for x in xs]),1) if xs else None
  print(f"{k:38} n={len(w):2} 3s={m(w,2)} vs {m(wo,2)} | watch={m(w,3)} vs {m(wo,3)} | reach={m(w,1)} vs {m(wo,1)}")
