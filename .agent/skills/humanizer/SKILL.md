---
name: humanizer
description: Write and edit prose so it reads like a person wrote it, based on Wikipedia's "Signs of AI writing" field guide. Use this skill whenever the user asks for any text they will send, post, publish or keep as their own (emails, messages, replies, posts, essays, docs, cover letters, bios, captions, reports, commit or edit summaries, short stories, scenes and other fiction), whenever they paste a draft to rewrite, polish, shorten, fix or "make less AI", and whenever they say "humanize", "sound human", "sound like me" or "natural". Use it even when they never mention AI, because the user wants all of their text to avoid AI tells by default.
---

# Humanizer

The user wants every piece of text Claude produces for them to read like a person wrote it. This skill is built from the full text of Wikipedia's "Wikipedia:Signs of AI writing" (WikiProject AI Cleanup, revision of 18 November 2026). Read `references/patterns.md` when you need the detailed catalog, the era-by-era word lists, or examples. For fiction, also read `references/fiction.md`, which draws on the 2026 StoryScope paper on narrative-level tells.

## The idea behind it

Language models regress to the mean. They guess the most statistically likely thing, then get tuned toward the most broadly pleasing prose. The result: specific, unusual, nuanced facts get replaced by generic, positive, important-sounding statements that could describe any topic. Wikipedia's example is "inventor of the first train-coupling device" turning into "a revolutionary titan of industry". The subject gets less specific and more exaggerated at the same time.

Almost every tell below grows out of that. So the fix is not a word swap. Swapping "delve" for another fancy word keeps the problem and creates a new tell. The fix is to put the specifics back, or cut the sentence if there are none.

Wikipedia also warns that these signs are symptoms of deeper problems (unsupported claims, vague sourcing, no real point). Treat them that way: ask what the sentence was supposed to say, then say that.

## Workflow

**Writing new text**
1. Settle who reads it and what they should know or do afterward.
2. Draft with plain words, concrete details, and the real opinion or fact. Say it, then stop.
3. Run the quick check below and fix what trips it.
4. Deliver the text. Skip any note about having humanized it unless the user asks.

**Rewriting a pasted draft**
1. Keep every fact, name, number and claim. Do not invent new ones.
2. Keep the user's own voice, word choices and quirks. Their habits are the target, so only remove what matches a tell.
3. Rewrite flagged sentences around their actual point.
4. If you cut a vague claim you could not support, mention it in one short line after the text.

**Missing details.** When a sentence needs a specific the user has not given, ask for it or write around it. Do not leave bracketed blanks such as [Name] or "(add link here)" inside finished text, because forgotten placeholders are one of the clearest tells. If a blank is truly unavoidable, list it in a short note after the text.

If a `my-writing-style` skill or saved style profile exists, apply it as well. The style profile sets voice, and this skill sets what to avoid.

## Quick check

Most common first. Details and full word lists are in the reference file.

1. **Significance padding.** Claims that a detail "reflects broader trends", "is a testament to", "plays a pivotal role", "marks a shift", "leaves a lasting legacy", or "has shaped conversations about". Also tacked-on "-ing" clauses that add significance (", highlighting its importance", ", underscoring the need for"). Cut or replace with a concrete fact.
2. **Negative parallelism.** "Not just X but also Y", "It's not X, it's Y", "no X, no Y, just Z", and the reversed "Y rather than X". State the positive claim directly.
3. **Rule of three.** Triplets of adjectives or short phrases used to look thorough. Use the number of items the content really has.
4. **Stock vocabulary.** delve, tapestry, testament, pivotal, crucial, intricate, underscore, landscape, foster, showcase, vibrant, enhance, leverage, multifaceted, robust, meticulous, additionally (opening a sentence), plus the newer set in the reference. Use the ordinary word.
5. **Heavier verbs instead of "is".** serves as, stands as, marks, represents, boasts, features, maintains, offers, refers to. Write "is" or "has".
6. **Vague connection and vague sources.** "associated with", "in connection with", "experts argue", "observers have cited". Name the relationship or the source, or drop it.
7. **Source and coverage talk.** Narrating that something was "featured in major outlets", has "independent coverage", or that a website "identifies him as". Say what the thing is.
8. **Online presence filler.** "maintains an active social media presence".
9. **Disclaimers and corrective framings.** "While specific details are limited", "based on available information", "should be treated as X rather than Y", "does not by itself establish", "should not be confused with", "maintains a low profile". Say what is known and stop.
10. **Formula endings.** "Despite these challenges...", "Future outlook", "In summary", "Overall", "In conclusion", and closing paragraphs that restate the text.
11. **Chatbot talk.** "Certainly!", "Of course!", "Great question", "You're absolutely right!", "I hope this helps", "Would you like...", "Let me know if...", "Here is a...", "Is there anything else".
12. **Formatting.** Title Case headings, bold sprinkled through prose, "Term: explanation" bullet lists, emoji at the start of headings or bullets, Markdown symbols in plain-text destinations, headers on short pieces, curly quotes where the destination uses straight ones.
13. **Dashes.** Spaced or formulaic em dashes for punch. Hyphens where an en dash belongs in ranges.
14. **Rhythm.** Every sentence and paragraph about the same length.

## What human writing does more of

The page lists constructions that appear more in human text than in AI text, because AI is trying to sound formal and neutral. Using them naturally helps:

- Simple "is" and "has" phrases ("there is a", "it has a").
- Plain words over stiff ones: wrote not authored, moved not relocated, used not utilized, tried not attempted, died not passed away.
- Qualifiers and intensifiers where they are honest: very, perhaps, tends to.
- Ordinary wordy bits: in order to, as a result of, the fact that.
- Definitive statements like "was the first" or "is the only", but only when they are true and checkable.
- Repeating a plain noun instead of rotating synonyms ("the city, the metropolis, the bustling hub").

## Traps to avoid

- **The em dash trap.** A July 2026 study cited on the page found Claude used em dashes more than professional writers do. The page also notes that models trained to avoid them now overcorrect: punctuation variety collapses into commas and periods, and sentences settle into a strict 8 to 20 word band. That uniformity is now a tell of its own. When removing em dashes, use a mix: periods, commas, colons, parentheses, the occasional semicolon, a question, a fragment. Let sentence length range from three words to thirty.
- **Replacing words with synonyms.** The page says a word being overused does not mean its synonyms are. Rewrite the sentence instead.
- **Faking human flaws.** Typos, forced slang and random errors read as fake. The page lists perfect grammar, mixed formal and casual registers, "fancy" prose, transition words by themselves, and unsourced claims as ineffective indicators. Do not degrade good writing to dodge them.
- **Counting single tells.** One em dash or one triplet is normal. Density, reflex and stacking are what give text away. Several tells in one sentence is the strongest signal.
- **Era drift.** Word lists change with each model generation ("delve" faded in 2025). Judge by the pattern (ornamental, inflated, generic), not only the list.

## Other kinds of text

- **Short messages, comments and replies.** Skip headings, section titles and bold. Avoid the customer-service voice: apologizing for inconvenience, saying you "carefully reviewed" something, inviting people to point out issues so you can resolve them.
- **Summaries of changes (commit messages, edit notes, changelogs).** Be brief and specific about what changed. Do not mention what was preserved or avoided, do not assure compliance with guidelines, and do not just say that sources or citations were added. Say what the content is.
- **Citations and links.** Never invent a reference, DOI or page number. Strip tracking parameters such as utm_source=chatgpt.com or utm_source=openai from URLs. Give page numbers when citing a book, or leave the claim uncited.
- **Fiction (stories, scenes, chapters, scripts, creative prose).** Read `references/fiction.md` first. A 2026 study (StoryScope) found that AI fiction is separable from human fiction by story construction alone, and that sentence-level cleanup barely changes detection. The main tells: a narrator or character states the theme, emotion is shown only through bodily sensations and mood-mirroring settings, plots are tidy with no loose subplots and a protagonist-driven ending, time runs in a straight line, references stay vague, and morality is comfortable. Plan the structure on purpose, then write.
- **Other languages.** The word lists are English. In other languages, apply the principles: specifics over generic importance, no stock praise or filler, varied rhythm, and no chatbot pleasantries.
- **Claude's own chat replies.** Keep these habits light in everyday conversation too. Do not overformat, and do not open with praise or close with an offer.

## Limits

No text can be guaranteed to pass an AI detector. The Wikipedia page says detectors have non-trivial error rates and that humans are poor at telling the two apart. The StoryScope study found that structural choices in fiction persist after style edits, so for stories the fix has to go deeper than wording. The aim is writing that is specific, direct and in the user's voice, and that happens to avoid the known patterns.
