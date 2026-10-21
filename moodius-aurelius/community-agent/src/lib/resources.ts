// Free resources sent by keyword DM (JOURNAL / READ / REFLECT). Original writing; book details
// are bibliographic facts only, no quotations.
export interface Resource { slug: string; title: string; intro: string; sections: { h: string; items: string[] }[]; note?: string }

export const RESOURCES: Record<string, Resource> = {
  "journal-worksheet": {
    slug: "journal-worksheet",
    title: "A guided journaling worksheet",
    intro: "Fifteen minutes, one page, pen and paper. You don't need to answer every question. Stop at the one that makes you hesitate; that's usually the one.",
    sections: [
      { h: "1. What happened (facts only)", items: ["Write today's hardest moment as a camera would record it. No adjectives, no motives.", "Now underline every word you'd have to remove for a stranger to agree with your version."] },
      { h: "2. What I told myself about it", items: ["What story did I add to the facts?", "Which part of it is a judgement, and which part is a fact?", "If a friend told me this story about themselves, what would I point out?"] },
      { h: "3. What I felt, precisely", items: ["Name the feeling with a more exact word than \"bad\" or \"stressed\" (for example: slighted, exposed, restless, envious, ashamed, lonely).", "Where did I notice it in my body?", "What did the feeling want me to do? Did I do it?"] },
      { h: "4. What was in my control", items: ["Draw two columns: up to me / not up to me. Sort everything from section 1.", "From the first column, pick one small action for tomorrow."] },
      { h: "5. One honest sentence", items: ["Finish this: \"The thing I'm not admitting is…\"", "Close the notebook. You don't have to solve it tonight."] },
    ],
    note: "This is a reflective exercise, not therapy. If writing brings up something heavy, put the pen down and talk to someone you trust or a professional.",
  },
  "reading-list": {
    slug: "reading-list",
    title: "A reading list for the inner life",
    intro: "Short to long, roughly in the order I'd read them. Where a free public-domain translation exists, it's named.",
    sections: [
      { h: "Start here (Stoicism)", items: [
        "Epictetus, Enchiridion (the \"Handbook\"). Shortest door in. Free in George Long's translation.",
        "Marcus Aurelius, Meditations. Private notes, not a treatise. Free in George Long's translation; Gregory Hays's modern translation (Modern Library, 2002) reads more easily.",
        "Seneca, Letters to Lucilius. Free in Richard Mott Gummere's translation; Penguin's selection \"Letters from a Stoic\" (trans. Robin Campbell) is a good first pick.",
      ] },
      { h: "Meaning and suffering", items: [
        "Viktor Frankl, Man's Search for Meaning.",
        "Albert Camus, The Myth of Sisyphus.",
        "Søren Kierkegaard, The Sickness unto Death.",
        "Simone de Beauvoir, The Ethics of Ambiguity.",
      ] },
      { h: "The self, the shadow, other people", items: [
        "C. G. Jung, Modern Man in Search of a Soul.",
        "Erich Fromm, The Art of Loving.",
        "bell hooks, The Will to Change: Men, Masculinity, and Love.",
        "Ichiro Kishimi and Fumitake Koga, The Courage to Be Disliked.",
      ] },
      { h: "One novel", items: ["Fyodor Dostoevsky, Notes from Underground. The 2am argument, written in 1864."] },
    ],
  },
  "reflection-exercise": {
    slug: "reflection-exercise",
    title: "The evening review",
    intro: "Seneca describes reviewing his whole day each night before sleep, without excuses and without cruelty (On Anger, book 3, section 36). Here's a ten-minute version.",
    sections: [
      { h: "Three questions", items: ["What did I do well today, even slightly?", "Where did I fall short of who I want to be? (One example, not a list.)", "What will I do differently the next time it happens?"] },
      { h: "Rules", items: ["Write it down; thinking it doesn't count.", "Speak to yourself the way you'd speak to a friend you respect: honest, not harsh.", "End with the first question again. The review is for practice, not punishment."] },
    ],
    note: "A reflective practice, not a treatment for anything.",
  },
};
