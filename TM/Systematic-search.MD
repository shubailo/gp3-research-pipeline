---
description: "Instructions for constructing a systematic search query, database selection, and Boolean operators."
---

# Systematic Search

The systematic search must capture **all** relevant studies ever published, not just those with positive results or consistent with current trends. 

## 1. Primary Databases
- **MANDATORY:** MEDLINE, Embase, and CENTRAL (Cochrane) are the standard databases strongly recommended for meta-analyses.
- **Interventional Reviews:** Must include ClinicalTrials.gov and the WHO ICTRP portal.
- **Note:** Google Scholar and TRIP are search engines (mostly for finding citing articles), not proper electronic databases for systematic primary searches.

## 2. Gray Literature
- **Definition:** Literature that has not been peer-reviewed (e.g., conference abstracts, personal emails, poster presentations).
- **Rule:** It is generally **NOT RECOMMENDED** to use gray literature due to lower quality.
- **Exception:** Conference abstracts may be used *only* if no other evidence is available, and this MUST be pre-specified in the protocol. Avoid the BIOSIS database unless specifically hunting for gray literature.

## 3. Constructing the Search Query
A comprehensive query combines free-text terms and database-specific hierarchical terms.
- **MeSH (MEDLINE) & EMTREE (Embase):** Hierarchical systems. Use these to find synonyms and related terminology.
- **Automatic Explosion:** When you include a MeSH term, the database automatically includes all more specific subjects below it in the hierarchy.
- **Free-Text Terms:** Always include synonyms, related words, and spelling variations.
  - *Truncation (`*`):* Putting an asterisk at the end of a word stem provides all variations.
  - *Quotation Marks (`" "`):* Finds exact phrases in that exact order (Note: automatic explosion does *not* happen within quotation marks).

## 4. Boolean Operators
- **AND:** Narrows the search. Finds articles containing *both* terms (e.g., "peanut butter" AND "jelly"). Connect different PICO concepts using AND.
- **OR:** Expands the search. Finds articles containing *either* term (e.g., "peanut butter" OR "jelly"). Combine synonyms within the same PICO concept using OR.
- **NOT:** **DANGEROUS**. It is highly recommended to *avoid* using NOT in a meta-analysis search, as it can accidentally exclude highly relevant articles that merely mention the excluded term.

## 5. Structuring by PICO
To construct the final search key, group synonyms using `OR`, and connect the PICO concepts using `AND`.
*Example:* `(Term related to Population OR Synonym) AND (Term related to Intervention OR Synonym) AND (Term related to Outcome OR Synonym)`

## Agent Directives
- **MANDATORY:** Warn users against using the `NOT` Boolean operator during systematic search query formulation.
- **MANDATORY:** Recommend MEDLINE, Embase, and CENTRAL as the baseline databases.
- **MANDATORY:** Advise the user to consult an expert librarian or search specialist when finalizing the systematic search strategy.
