import json, os, re, html, markdown
SRC = "/mnt/project-files/moodius-aurelius/strategy/21-stories-system"
OUT = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(SRC, "data.json")))

def md(name):
    t = open(os.path.join(SRC, name)).read()
    t = re.sub(r"^# .*\n", "", t, count=1)
    h = markdown.markdown(t, extensions=["tables", "fenced_code"])
    h = h.replace("<table>", '<div class="tw"><table>').replace("</table>", "</table></div>")
    h = re.sub(r'<a href="(http[^"]+)"', r'<a target="_blank" rel="noopener" href="\1"', h)
    return h

docs = {k: md(f) for k, f in [("research", "01-research.md"), ("conv", "04-conversation-system.md"), ("bank", "06-response-bank.md"),
                               ("work", "08-workflow.md"), ("tests", "10-ab-tests.md"), ("tpl", "11-templates.md")]}
templates = sorted(f for f in os.listdir(os.path.join(SRC, "templates")) if f.endswith(".jpg"))
tpl_show = [f for f in templates if not f.endswith("_hand.jpg")]

slim = dict(sequences=data["sequences"], calendar=data["calendar"], concepts=data["concepts"], questions=data["questions"],
            renders=[dict(seq=r["seq"], frame=r["frame"], mode=r["mode"], file=os.path.basename(r["file"]), part=r["part"]) for r in data["renders"]],
            pillars=data["pillars"], formats=data["formats"], templates=tpl_show)

page = open(os.path.join(OUT, "page.html")).read()
page = page.replace("/*DATA*/", "const DATA=" + json.dumps(slim, ensure_ascii=False).replace("</", "<\\/") + ";")
for k, v in docs.items():
    page = page.replace("<!--DOC:%s-->" % k, v)
open(os.path.join(OUT, "stories-system.html"), "w").write(page)
print(len(page))
