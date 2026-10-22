---
description: Export an approved essay to Substack-ready HTML plus a preview, and print the paste checklist
argument-hint: moodius-aurelius/substack/essays/NN-slug.md
---
1. Confirm **$ARGUMENTS** has status "approved" in `moodius-aurelius/substack/queue/approval-queue.csv` (approved_by filled). If not, stop and say so.
2. Run `python3 moodius-aurelius/substack/scripts/qc.py $ARGUMENTS` (must pass) and `python3 moodius-aurelius/substack/scripts/export_substack.py $ARGUMENTS`.
3. Print the paste checklist from `moodius-aurelius/substack/09-setup.md` §3 with this essay's title, subtitle, slug, SEO description and section filled in from `exports/<slug>/meta.txt`.
4. Never publish or schedule on Substack. If Surafel has set up python-substack and asks for it explicitly, you may create an **unpublished draft** only.
