"""Paths, taxonomies and brand rules for the hook-intel system. Everything here is plain data."""
import os

PKG = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(PKG)                      # hook-intel/
PROJECT = os.path.dirname(ROOT)                  # moodius-aurelius/
DATA = os.path.join(ROOT, "data")
RAW = os.path.join(DATA, "raw")
DB_PATH = os.environ.get("HOOKINTEL_DB") or os.path.join(DATA, "hookintel.db")
EDITORIAL = os.path.join(DATA, "editorial")
SCRIPTS = os.path.join(DATA, "scripts")
IMPORTS = os.path.join(DATA, "imports")
REPORTS = os.path.join(ROOT, "reports")
EXPORTS = os.path.join(ROOT, "exports")
ENGINE = os.path.join(PROJECT, "reels-engine", "tools", "engine.py")   # existing renderer + QC gate

RESEARCH_WINDOW_DAYS = 90
SHORT_FORM_MAX_S = 180
MIN_BASELINE_N = 5          # creator baseline needs at least this many recent Shorts
OUTLIER_STRONG = 3.0        # same threshold instagram-agent-skill's swipe.py uses for "signal"
OUTLIER_ABOVE = 1.5
MIN_VIEWS_FOR_SIGNAL = 1000   # below this a ratio is noise (a 60-view Short on a 6-view channel is "10x")
MIN_BASELINE_MEDIAN = 100     # creators whose Shorts median under 100 views give no usable baseline
MAX_PER_CYCLE = 100           # the brief: up to 100 relevant videos per research cycle

# ---------- hook taxonomy (brief section 4) ----------
CATEGORIES = {
    "curiosity_gap": "Curiosity gap",
    "contrarian": "Contrarian statement",
    "psychological_revelation": "Psychological revelation",
    "uncomfortable_truth": "Uncomfortable truth",
    "identity_challenge": "Identity challenge",
    "emotional_recognition": "Emotional recognition",
    "philosophical_paradox": "Philosophical paradox",
    "visual_disruption": "Visual disruption",
    "story_opening": "Story opening",
    "unexpected_question": "Unexpected question",
}

# (regex, weight). Matched on the lower-cased hook text. Evidence lists which cues fired.
CUES = {
    "curiosity_gap": [
        (r"\bthe (real )?reason\b", 2), (r"\bwhy (you|we|people|men|women|some)\b", 1.5), (r"\bwhat happens\b", 2),
        (r"\bnobody (tells|told|talks)\b", 2), (r"\bthe one thing\b", 2), (r"\bhere'?s (what|why|how)\b", 1.5),
        (r"\bthis is (why|what|how)\b", 1.5), (r"\bsecret\b", 1), (r"\bsays about you\b", 2), (r"\bwhat (it|this) means\b", 1.5),
        (r"\bsigns?\b", 1), (r"\bthe moment\b", 1), (r"\bhidden\b", 1), (r"\bmost people (don'?t|never)\b", 1.5),
        (r"\bwhat .{0,40}\bteach", 1.5), (r"\bthe job of\b", 1), (r"\bthe (hidden |real )?cost of\b", 1.5)],
    "contrarian": [
        (r"^stop\b", 2.5), (r"^don'?t\b", 2), (r"\bisn'?t\b", 1.5), (r"\bis not\b", 1.5), (r"\bwrong\b", 1.5),
        (r"\bmyth\b", 2), (r"\boverrated\b", 2), (r"\bactually\b", 1), (r"\b(a )?lie\b", 1.5), (r"\binstead\b", 1),
        (r"\bnot .{2,40}\bbut\b", 1.5), (r"\beveryone (thinks|says|tells)\b", 2), (r"\bunpopular\b", 2),
        (r"\bdoesn'?t (make|mean)\b", 1.5), (r"\bnever\b", 0.5),
        (r"\bstop (doing|treating|giving|trying|being)\b", 2)],
    "psychological_revelation": [
        (r"\bpsycholog", 2), (r"\byour brain\b", 2), (r"\b(sub|un)conscious", 2), (r"\battachment\b", 2),
        (r"\btrauma\b", 1.5), (r"\bshadow\b", 2), (r"\bprojection|project(ing)? onto\b", 2), (r"\bjung\b", 1.5),
        (r"\bpeople who\b", 1.5), (r"\b(avoidant|anxious|secure)\b", 1.5), (r"\bnarcissis", 1), (r"\bdefen[cs]e mechanism\b", 2),
        (r"\bpattern\b", 1)],
    "uncomfortable_truth": [
        (r"\b(hard|harsh|brutal|ugly|uncomfortable) truths?\b", 3), (r"\btruth\b", 1.5), (r"\bno ?one\b", 1),
        (r"\bnobody\b", 0.5), (r"\byou'?re not\b", 1.5), (r"\byou are not\b", 1.5), (r"\bthe problem (is|was) you\b", 2.5),
        (r"\bhonest(ly)?\b", 1), (r"\baccept\b", 1), (r"\byou (already )?know\b", 1), (r"\bwon'?t (save|fix|come)\b", 1.5),
        (r"\bisn'?t coming\b", 2), (r"\btoo late\b", 1.5), (r"\bcost of\b", 1)],
    "identity_challenge": [
        (r"\bif you'?re (the|a|someone)\b", 2), (r"\b(kind|type) of (man|person|people|woman)\b", 2), (r"\breal (man|men)\b", 2),
        (r"\bwho you (are|were|become)\b", 2), (r"\bthe (man|person) you\b", 2), (r"\bweak\b", 1), (r"\byour identity\b", 2),
        (r"\byou were never\b", 2), (r"\bbecome\b", 1), (r"\bself[- ]respect\b", 1.5), (r"\byou'?re the (problem|one)\b", 1.5)],
    "emotional_recognition": [
        (r"^when you\b", 2), (r"\byou feel\b", 2), (r"\bthat feeling\b", 2), (r"\blonel(y|iness)\b", 2), (r"\balone\b", 1.5),
        (r"\bmiss(ing)?\b", 1), (r"\bhurt", 1.5), (r"\b(tired|exhausted|numb)\b", 1.5), (r"\bheartbr", 2), (r"\bgrie(f|ve)\b", 2),
        (r"\bcry(ing)?\b", 1.5), (r"\boverthink", 1.5), (r"\banxi(ety|ous)\b", 1), (r"\bempty\b", 1.5), (r"\byou (still|keep)\b", 1.5),
        (r"\bsurrounded by people\b", 2), (r"\bunseen\b", 1.5), (r"\bfuneral|dies\b", 1)],
    "philosophical_paradox": [
        (r"\bthe more\b.{0,40}\bthe (less|more)\b", 3), (r"\bparadox\b", 3), (r"\babsurd", 2), (r"\bmeaning(less)?\b", 1),
        (r"\bonly when\b", 1.5), (r"\blos(e|ing) .{0,25}to (find|gain|keep)\b", 2.5), (r"\bfreedom\b", 1),
        (r"\b(both|and yet)\b", 1), (r"\bwithout .{0,20}there is no\b", 2), (r"\bcamus|nietzsche|kierkegaard|sartre\b", 1),
        (r"\b\w+ vs\.? \w+", 2), (r"\bfeel safer than\b", 2)],
    "visual_disruption": [],   # needs the visual_opening annotation; text alone cannot show it
    "story_opening": [
        (r"^(i|my|when i|one day|in \d{3,4}|there was|years ago|last (night|week|year))\b", 2.5), (r"^(he|she|they) (was|were|had|said|told)\b", 2.5),
        (r"\bstory\b", 1), (r"\bonce\b", 1), (r"\bwrote (to|this|a letter)\b", 1.5), (r"\b(was|were) (dying|exiled|sentenced)\b", 2)],
    "unexpected_question": [
        (r"\?\s*$", 2), (r"^(what|why|how|do|did|have|are|is|would|could|can|when did|who)\b", 1),
        (r"\b(you|your)\b.*\?", 1)],
}
VISUAL_DISRUPTION_CUES = r"\b(smash|sudden|cut to black|black screen|jump|slam|glitch|zoom punch|whip|flash|freeze)\b"

# structural shapes used to group hooks into patterns
STRUCTURES = [
    ("two_branch", r"\bif (it'?s|that'?s) (true|false)|\bif (true|false)\b|\beither\b.{0,40}\bor\b"),
    ("list_opener", r"^(\d+|three|five|seven|ten|two|four)\b|\b\d+ (things|signs|rules|ways|habits|reasons|lessons)\b"),
    ("question", r"\?\s*$"),
    ("negation_reframe", r"\b(isn'?t|is not|not)\b.{0,40}\b(it'?s|but|it is)\b|^it'?s not\b"),
    ("people_who", r"\bpeople who\b|\bmen who\b|\bthose who\b"),
    ("named_thinker", r"\b(marcus|aurelius|seneca|epictetus|jung|nietzsche|dostoevsky|camus|kafka|socrates|plato|aristotle|freud|kierkegaard|sartre|baldwin|frankl)\b"),
    ("second_person_scene", r"^(you|your|when you|you'?ve|you'?re)\b"),
    ("first_person_story", r"^(i|my|when i)\b"),
    ("statement", r".*"),
]

# account's own evidence (strategy/16-lessons-2026-10-22.md), used as priors, never as proof
OWN_EVIDENCE = {
    "other_person_conflict": {
        "cue": r"\b(someone|they|them|their|insult|argu|disrespect|angry|anger|approval|like you|people)\b",
        "note": "Moodius reels with other-person/conflict hooks: reach 106-122, 37-47% held past 3 s (n=5)."},
    "list_opener": {
        "cue": STRUCTURES[1][1],
        "note": "Moodius numbered-list openers: 25-29% held past 3 s, the three lowest (n=3)."},
    "two_branch": {
        "cue": STRUCTURES[0][1],
        "note": "The one Moodius two-branch reel held 16.5 s average watch vs 4.3 s median (n=1)."},
}

# ---------- brand ----------
PILLARS = {
    "Stoicism & classics": r"\b(stoic|stoicism|marcus|aurelius|seneca|epictetus|socrates|plato|aristotle|virtue|meditations)\b",
    "Jung & the unconscious": r"\b(jung|shadow|unconscious|subconscious|archetype|projection|persona|dream)\b",
    "Masculinity & emotional maturity": r"\b(men|man|male|masculin|father|brother|son|emotional maturity|boys)\b",
    "Relationships & attachment": r"\b(relationship|attachment|love|partner|ex\b|breakup|friend|avoidant|anxious|dating|marriage|people)\b",
    "Existentialism & loneliness": r"\b(lonel|alone|meaning|absurd|camus|nietzsche|kierkegaard|sartre|dostoevsky|kafka|death|existential)\b",
    "Discipline & self-respect": r"\b(discipline|self[- ]respect|resilien|habit|routine|courage|boundar)\b",
    "Journaling & self-awareness": r"\b(journal|self[- ]aware|reflect|write it down|notice|truth|honest)\b",
}
EMOTIONS = {
    "anger": r"\b(anger|angry|rage|disrespect|insult|furious)\b",
    "loneliness": r"\b(lonel|alone|isolat|no one|nobody)\b",
    "shame": r"\b(shame|ashamed|embarrass|guilt|not enough|failure)\b",
    "longing": r"\b(love|miss|ex\b|heartbr|longing|attach)\b",
    "fear": r"\b(fear|afraid|anxi|scared|worry|overthink|panic)\b",
    "grief": r"\b(grie|loss|death|dying|mourn)\b",
    "calm": r"\b(calm|peace|still|quiet|silence)\b",
    "defiance": r"\b(stop|never|refuse|enough|wrong)\b",
}
OFF_BRAND = [r"\balpha\b", r"\bsigma\b", r"\bhigh[- ]value\b", r"\bred ?pill\b", r"\bgrindset\b", r"\bhypergam",
             r"\bfemale nature\b", r"\bwomen (are|always|never|love)\b", r"\bnever argue with a woman\b", r"\bsimp\b",
             r"\bbeta male\b", r"\bget rich\b", r"\bmillionaire\b", r"\bdark psychology\b", r"\bmanipulat(e|ion) (her|them|anyone)\b"]
CLICHES = [r"\bthis will change your life\b", r"\bwatch (this|till the end)\b", r"\bwait for it\b", r"\byou won'?t believe\b",
           r"\bmind[- ]?blowing\b", r"\blevel up\b", r"\bunlock\b", r"\bgame[- ]changer\b", r"\bmindset\b", r"\bin today'?s world\b",
           r"\bjourney\b", r"\bhustle\b", r"\bkings?\b"]
ABSTRACT = r"\b(life|success|everything|things|stuff|mindset|motivation|happiness|greatness|growth|potential)\b"
CONCRETE = (r"\b(\d+|phone|text|room|door|kitchen|car|street|window|bed|mirror|friend|father|mother|brother|ex|"
            r"boss|morning|night|sunday|monday|3am|2am|shower|bus|train|desk|coffee|letter|profile|message|call|"
            r"supermarket|office|funeral|wedding|birthday|minutes?|hours?|years?|days?)\b")
FACE_DEPENDENT = r"\b(watch me|look at me|my face|i'?m going to show|let me show|duet|stitch|react)\b"
SCENE_WORDS = r"\b(room|street|window|rain|night|city|sea|road|door|kitchen|mirror|train|bench|field|light|dark|empty)\b"

# a video is "relevant" when its title, hook or channel name hits one of these (or a pillar)
NICHE = (r"\b(stoic|philosoph|psycholog|jung|shadow|attachment|relationship|lonel|emotion|anxi|therap|mind|"
         r"nietzsche|camus|dostoevsky|kafka|seneca|marcus|epictetus|existential|meaning|journal|self[- ]?aware|"
         r"masculin|men\b|man\b|father|love|heart|trauma|narciss|introvert|overthink|grief|anger|discipline|"
         r"self[- ]?respect|wisdom|literature|book|poet|depress|healing|soul|ego|identity|purpose)")

SAFE_SOURCES_FOOTAGE = [
    "Library of Congress (loc.gov) Prints & Photographs: no known restrictions items only",
    "Internet Archive Prelinger Archives (public domain films)",
    "Wikimedia Commons, public-domain paintings (PD-Art)",
    "The Met / Rijksmuseum / Art Institute of Chicago Open Access (CC0)",
    "NASA image library (public domain)",
    "Pexels / Unsplash licence (check each clip; no people as identifiable endorsers)",
    "Own footage shot by the owner (no face; anonymous brand)",
]
