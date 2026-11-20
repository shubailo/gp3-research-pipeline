# Fiction and story writing

Source: "StoryScope: Investigating idiosyncrasies in AI fiction" (Russell, Rajendhran, Pham, Iyyer, Wieting; COLM 2026). It compared 10,272 published human stories (Books3) with stories from five models (Claude Sonnet 4.6, GPT-5.4, Gemini 3 Flash, DeepSeek V3.2, Kimi K2.5) written from the same prompts, about 5,000 words each.

Contents
1. Why word-level fixes fail here
2. The tells and the human alternative
3. Model fingerprints
4. How to apply this
5. Limits

---

## 1. Why word-level fixes fail here

A classifier using only narrative choices (plot, agents, time, revelation, setting, perspective) separated human from AI fiction at 93.2% macro-F1, with no style features at all. A rewriter that stripped clichés and purple prose from AI stories lowered detection by only 1.6 points. So polishing sentences does little. The difference sits in how the story is built, and the fix has to happen at that level: plan the story differently, then write it.

Another finding explains the goal. The five models cluster tightly in narrative space, while human stories are spread out and rarer (mean rarity percentile 0.71 against 0.49). Being human here means being varied and specific to the story. Applying a fixed checklist of "human" moves to every piece would produce a new uniform pattern, so choose moves that this story needs.

## 2. The tells and the human alternative

Numbers are prevalence or 1-to-5 scale means, human against AI.

**Over-explained theme**
- A narrator states the story's theme: 52% vs 77%.
- Dialogue works as philosophical debate: 34% vs 59%.
- Moral and philosophical weighting: 3.26 vs 3.68. Thematic unity: 4.41 vs 4.74.
- Typical shape: a grieving character's arc ends with someone stating the lesson learned.
- Alternative: end on an image, an action or a line of dialogue that carries the theme without naming it. Let some threads bear no theme at all.

**Emotion performed through bodies and rooms**
- Emotion conveyed by bodily metaphor or physical sensation: 38% vs 81%. Fear becomes a tightening chest, cold sweat, a dimming lamp.
- Smell as a main sense: 57% vs 82%.
- Setting mirrors the character's inner state: 3.58 vs 4.07. Ecological or environmental emphasis: 2.83 vs 3.21.
- Plain emotion labels ("she felt afraid"): 29% human vs 8% AI.
- Alternative: say the feeling directly when that is the clearest thing. Show behavior (a character changes the subject, takes the long way home) instead of sensations. Let the weather be weather.

**Tidy, single-track plot**
- No subplots: 57% vs 79%. Subplots that run parallel to the main theme: 42% vs 21%.
- Resolution driven by the protagonist's choice: 46% vs 69%.
- Resolution through internal understanding or acceptance: 27% vs 47%.
- Causal chain continuity: 3.92 vs 4.20.
- Characters introduced through external description: 30% vs 52%. Humans introduce them in dialogue more often.
- Alternative: let events, other people or luck decide some outcomes. Leave a thread loose. Add a subplot that does not tie back.

**Linear time**
- Humans use more jumps, flashbacks and flash-forwards: chronological discontinuity 2.40 vs 2.12, anachrony 2.58 vs 2.31, nonlinear framing to delay a reveal 1.96 vs 1.68.
- Humans more often recast earlier scenes after a surprise: 3.28 vs 2.95.
- Alternative: open at the funeral and spiral backward, withhold a fact until late, or let the reader reinterpret an early scene.

**Vague references and a closed fourth wall**
- Specific named works, authors, brands and places: 47% vs 24%. A balanced mix of explicit and implicit references: 37% vs 16%. AI prefers unnamed echoes (72% vs 50%).
- Narration breaks the fourth wall: 67% vs 39%. Direct address to the reader: 28% vs 7%.
- Alternative: name the real thing (the brand of cigarette, the actual song). Address the reader once in a while if the voice allows.

**Comfortable morality and narrow range**
- Morally ambiguous or mixed protagonists: 59% vs 38%.
- Humans use more locations (1.34 vs 1.08 on the paper's scale) and more dialogue relative to narration (2.95 vs 2.70).
- Alternative: let the protagonist do something the story does not fully forgive. Move the story through more than one place.

## 3. Model fingerprints

Each model also has habits of its own. The tested versions are older than some current models, so treat these as examples of the kind of habit to watch for.

- Claude (Sonnet 4.6): the flattest event escalation of any source, restrained stories, epilogues and flash-forward endings, no dream sequences, quiet endings, deference to literary convention (62% vs 39 to 56%), uncanny or haunted moods.
- GPT-5.4: gossip and rumor driving the plot (64% vs 44 to 55%), a narrator looking back from a distance, subverted expectations (41% vs 27 to 36%), ambiguous reconciliations.
- Gemini 3 Flash: the tidiest endings, long denouements, the bleakest settings (88%), characters described from outside.
- DeepSeek V3.2: key context placed up front, a visible narrator, emotion shown through behavior, stories inside stories.
- Kimi K2.5: opens in the middle of the action, labels no character traits outright, and otherwise sits at the generic center.

If Claude is writing, it should watch the Claude list in particular: stories that never escalate, epilogues, and reverence for convention.

## 4. How to apply this

1. Before drafting, make three structural decisions on purpose, based on what this story needs: how time moves, who decides the ending, and what the reader is left to infer.
2. Draft with specific names, places and objects. Real brands and works where they fit.
3. After drafting, check the ending against the over-explained theme and the tidy-plot lists. Cut the closing paragraph that states what the story meant.
4. Check that feelings are not all delivered through body sensations.
5. Keep sentence-level rules from SKILL.md in force. Style cues still help detectors, and they are the cheapest to fix.
6. If the user supplies the premise and characters, keep them. The moves above change structure and delivery, not the user's story.

## 5. Limits

- The human stories are published fiction, so they reflect professional writers.
- Models were given one prompt each and no instruction to avoid these habits.
- Narrative features were labeled by an LLM, with 0.84 agreement with human annotators.
- Plain text classifiers still beat the narrative model on raw detection. The narrative signal is useful because it is interpretable and survives editing.
- Individual features overlap a lot between humans and AI. Treat them as tendencies, never as proof about one story.
