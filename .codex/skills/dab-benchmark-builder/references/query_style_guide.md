# Query Style Guide

## Target Style

Write natural analyst questions, not SQL paraphrases. Mention business/domain concepts, not table mechanics, unless the benchmark source naturally exposes those names.

Good:

```text
Which store earned the most revenue in USD from Brucqe Maginnis' song 'Street Hype' across all countries?
```

Too SQL-like:

```text
Join songs with revenue, filter where artist = 'Brucqe Maginnis' and song = 'Street Hype', group by store name, sum revenue_usd across all countries, order by total revenue descending, and return the first row.
```

More good examples, pulled from the DAB benchmark (Ma et al., 2026), spanning different domains and difficulty levels:

```text
Which English-language books in the 'Literature & Fiction' category have a perfect average rating of 5.0? Return all matching books.
```

```text
Among repos not using Python, what proportion of README.md files include copyright information?
```

```text
Identify CPC areas with the highest EMA of patent filings (smoothing 0.2); return level-5 codes whose best year is 2022.
```

```text
Which stock index in Asia has the highest average intraday volatility since 2020?
```

Notice what these have in common: they read like something a real analyst, engineer, or business user would type, they name domain concepts (a category, a license, a smoothing factor) rather than column names, and the "how" (joins, regex extraction, fuzzy matching) is left entirely implicit — the agent has to discover it.

## Useful Task Properties

Final selected queries must require:

1. at least two logical databases after the visible split, and
2. at least one DAB-style challenge beyond ordinary aggregation:
   key normalization/fuzzy entity matching, unstructured text extraction/classification,
   domain knowledge/formula, semi-structured parsing, or another documented semantic transformation.

Prefer candidates that require at least two of:

- Cross-table or cross-DB joining.
- ID/entity normalization.
- Aggregation, ranking, tie-breaking.
- Domain formula or business rule.
- Text/manual extraction.
- Counterfactual transformation.
- Date/time filtering or bucketing.
- Semi-structured field parsing.

Do not select a final query that can be answered from one visible database unless the user explicitly asks for a simple RL-only variant. If such a variant is kept, record why it is a variant and make sure it still has a complex join or semantic transformation.

### Worked example: how one DAB query stacks properties

Take the `bookreview` dataset's hardest query:

```text
Which English-language books in the 'Literature & Fiction' category have a perfect average rating of 5.0? Return all matching books.
```

This single sentence quietly requires:

- **Cross-DB join** — book metadata lives in a PostgreSQL `books_info` table; ratings live in a SQLite `review` table.
- **ID normalization** — `book_id` (e.g. `bid_1`) and `purchase_id` (e.g. `bref_1`) refer to the same book but use different prefixes, so a naive equality join silently returns nothing.
- **Text extraction** — "English-language" isn't a column; it's a substring buried inside a free-text `details` field (e.g. *"On Oct 30, 2012, the book was first published by Kensington..."* with a language mention elsewhere in the sentence), requiring something like a `LIKE '%English%'` scan rather than a clean filter.
- **Aggregation with exact-match threshold** — average rating must equal exactly 5.0, not merely "high," which is an easy constraint to silently drop (this is exactly the FM2 "missing operations" failure mode the paper documents).

That's four stacked properties in a 20-word question. This is the bar to aim for — not necessarily four every time, but the question should never reveal which of these moves is required. The difficulty lives in the data model and the schema, not in the wording.

A second example, from `patents`, showing how a domain-formula property looks in practice:

```text
Identify CPC technology areas with the highest exponential moving average of patent filings each year (smoothing factor 0.2), and return only the CPC group codes at level 5 whose best year is 2022.
```

Here the EMA formula and "level-5 code" terminology are domain knowledge the agent must already know or infer from hints — the query doesn't explain what an EMA is or how to compute it.

## Query Count and Difficulty

For RL training datasets, use 3-5 final queries per dataset unless the user asks otherwise. More than that can make one dataset overrepresented.

Keep a difficulty ladder:

- One medium cross-DB aggregate/reconciliation query with key repair or text extraction.
- One rules/manual or domain-formula query that uses another DB for facts.
- One heavier composition query with ranking, date logic, or conflict detection.
- Optional easier training query only if it still crosses DBs and uses a challenge property.

### Worked example: a difficulty ladder from one real DAB dataset (`yelp`)

DAB's own `yelp` queries (DuckDB + MongoDB) illustrate this ladder well:

1. **Medium, single challenge property (text/field extraction across DBs):**
   ```text
   During 2018, how many reviewed businesses offered either business parking or bike parking?
   ```
   (Parking attributes live nested inside a semi-structured MongoDB document, not as a flat column.)

2. **Medium-heavy, ranking + cross-DB join:**
   ```text
   Which U.S. state has the highest number of businesses that offer WiFi, and what is the average rating for those businesses?
   ```

3. **Heavier, date bucketing + tie-breaking + a minimum-support filter:**
   ```text
   Which business received the highest average rating between January 1, 2016 and June 30, 2016, and what category does it belong to? Consider only businesses with at least 5 reviews.
   ```
   (The "at least 5 reviews" clause is the deterministic tie-breaker/noise filter — without it, a business with one 5-star review trivially "wins.")

4. **Heaviest, cohort definition + multi-hop aggregation:**
   ```text
   Among users who registered on Yelp in 2016, which 5 business categories have received the most total reviews from those users since 2016?
   ```
   (Requires first defining a user cohort by registration date, then joining that cohort's reviews to businesses to categories — three logical hops.)

Notice the ladder doesn't escalate by making the prose more complicated — it escalates by adding more required hops, more filters that can be silently dropped, and tighter tie-breaking. Avoid making all tasks variants of the same computation (e.g. don't write five "top-N by average rating" queries against the same two tables).

If smoke testing gives 5/5 across all queries for a strong model, first inspect whether the split exposes clean keys, direct answer columns, or explicit join maps. Increase difficulty through the data model, not by making the question wording vague.

## Tie-Breaking

If a result may tie, specify a deterministic tie-breaker in the query or guarantee uniqueness in ground truth. Examples:

```text
If tied, return the lexicographically smallest merchant name.
```

DAB queries often build the tie-breaker into a support threshold instead of stating it explicitly — e.g. `bookreview`'s decade-rating query:

```text
Which decade of publication (e.g., 1980s) has the highest average rating among decades with at least 10 distinct books that have been rated? Return the decade with the highest average rating.
```

The "at least 10 distinct books" clause exists specifically so a decade with one perfectly-rated book can't trivially win — this is a tie-breaker disguised as a business rule, and it's a good pattern to imitate. Either approach (explicit tie-break instruction, or a support/minimum-count threshold) is acceptable, but pick one; do not leave ties unresolved.

Do not hide tie-breaking in validation only.

## Answer Format

Tell the agent what to return:

- `Return the merchant name and amount rounded to two decimals.`
- `Return all matching IDs in ascending order.`
- `Return the country code and count.`

DAB examples of this same instinct:

```text
... Return only the two-letter abbreviation of the most matching state (eg. CA).
```

```text
... Return only the Id of the agent.
```

```text
List all ETFs on NYSE Arca with adjusted close above $200 at any point in 2015; report the total count.
```

Keep final wording concise.

“Preprint PDF.” n.d. Accessed June 7, 2026. http://arxiv.org/pdf/2603.20576v1.