# Visible Split Patterns

## Principle

Design the split after ground-truth queries are known. The split should force realistic data work while preserving deterministic solvability.

Use different DBMS types for the visible split. A dataset with two logical databases should normally use two different `db_type` values, for example DuckDB + SQLite or MongoDB + PostgreSQL. A dataset with three logical databases should use three different DBMS types when possible. Do not split a dataset into multiple SQLite files and call that sufficient DAB difficulty.

Every selected final query should need at least two logical databases. If a candidate can be solved from one visible DB, drop it unless the user explicitly asks for a legacy/simple RL-only variant. A simple variant still needs a complex join or semantic transformation and must be labeled as a variant in the manual notes.

### Worked example: the canonical DAB split (`bookreview`)

The paper's own walkthrough dataset is the clearest template to copy. Starting point: a single open-source table pair, `books_info` and `reviews`, both joinable on a clean numeric `id`.

The authors turned this into a DAB-style task in four steps:

1. **Collect.** One source with two tables: `books_info` (title, publishedDate, publisher, ...) and `reviews` (user_id, book_id, rating, ...), joined cleanly on `id` / `book_id`.
2. **Transform.** Two columns (`publishedDate`, `publisher`) are deleted from `books_info` and re-embedded as a sentence in a new free-text `details` column (e.g. *"On Oct 30, 2012, the book was first published by Kensington..."*). Separately, the join key is reformatted differently in each table: `id` → `bid_<n>` in `books_info`, `book_id` → `bref_<n>` in `reviews`. Same entity, two different string prefixes.
3. **Distribute.** `books_info` (now `books_database`) goes to PostgreSQL; `reviews` (now `review_database`) goes to SQLite. Two different DBMS types, as required.
4. **Describe.** A `description.txt` states each logical database's name, system type, and schema. A separate `hints.txt` notes (without resolving) that `bid` and `bref` need fuzzy matching and that `details` may hold information needed for some queries.

The result: a query as short as *"Which English-language books in the 'Literature & Fiction' category have a perfect average rating of 5.0?"* now forces a cross-DBMS join across reformatted keys plus a text scan of an unstructured field — none of which is visible from the question itself. This is the model to replicate: identify the columns that would make the query trivial, delete or reformat them, and push their information into a different shape or a different database.

## Common Patterns

### Fact/Context Split

- DuckDB: large event/fact table.
- SQLite: metadata, lookup tables, rules, descriptions.

Use when source has transactions, logs, reviews, sales, or measurements.

**DAB example:** `stockmarket` puts per-security daily price history across 2,754 DuckDB tables (one per security — a fact table at scale) while company/security metadata (exchange, security type, financial-status flags) lives in SQLite. A query like *"List all ETFs on NYSE Arca with adjusted close above $200 at any point in 2015"* forces the agent to first resolve "which securities are ETFs on NYSE Arca" from the metadata side before touching the (very large) fact side.

### Identifier Surface Split

Use different ID formats across DBs:

```text
pay-crossfit-hanna
MERCHANT::CROSSFIT_HANNA
```

**DAB examples of this exact pattern:**
- `bookreview`: `bid_123` (PostgreSQL) vs. `bref_123` (SQLite) — a fixed-prefix rename, resolvable by a deterministic string transform.
- `crmarenapro`: 25% of ID fields get random trailing whitespace injected (e.g. `"Lead123"` vs. `"Lead123 "`) — not a prefix change, but silent corruption that breaks naive equality joins and requires a `TRIM`/clean step.
- `stockindex`: full exchange names in one DB ("Tokyo Stock Exchange") must be mapped to abbreviated index symbols in another ("N225") — this is a *semantic* mapping, not a string transform, and per the paper it's deliberately left for the agent to infer rather than enumerated in hints, because there are too many entries to list exhaustively.

These three are progressively harder: fixed-prefix rename < whitespace corruption < open-ended semantic mapping. Pick the level of difficulty deliberately rather than defaulting to the easiest.

Document normalization in hints if it is required for more than one task.

### Rule/Manual Split

Put scalar rule fields in tables and explanatory domain rules in `manual_sections` or docs tables. Good for tasks requiring formulas, business conventions, or code-to-description lookup.

If the rule/manual material is long text or document-like, prefer MongoDB for documents and SQLite/PostgreSQL for structured metadata. If the rule material is small structured lookup data, SQLite is fine, but pair it with DuckDB, PostgreSQL, or MongoDB rather than another SQLite split.

**DAB example:** `crmarenapro` (6 logical DBs across DuckDB, PostgreSQL, and SQLite) embeds company policy in its hints/knowledge-article tables rather than in the query — e.g. a "Sales Cycle Policy" defining sales cycle as "the number of days between an opportunity's creation date and the company signed date on the corresponding contract." The query itself just asks *"Who had the quickest average turnaround from opening to closing opportunities among agents in April 2023?"* — the formula lives in the rules table, not the question.

### Lookup Removal

Remove direct answer columns from the fact DB and require lookup through context DB. Example: store MCC code in merchant context, not on each payment.

**DAB example:** in `bookreview`, the `details` column is the only place a book's language is recorded after `publishedDate`/`publisher`-style columns are stripped from the clean schema — there is no `language` column anywhere. The agent must derive it via `LIKE '%English%'`-style scanning of free text instead of a column lookup.

### Text Extraction

Put relevant definitions in document/manual sections rather than as clean columns, but keep text deterministic and parseable.

MongoDB is the preferred visible target for descriptions, reviews, reports, transcripts, article bodies, support tickets, and other document-shaped text. SQL engines are preferred for facts, metrics, registries, and lookup tables.

**DAB example:** `yelp` (DuckDB + MongoDB) injects restaurant location into review text rather than keeping it as a column, so *"During 2018, how many reviewed businesses offered either business parking or bike parking?"* requires reading nested/free-text attributes out of MongoDB documents rather than filtering a flat field. Contrast with `patents` (PostgreSQL + SQLite), which embeds publication dates in varied natural-language formats ("dated 5th March 2019", "March the 18th, 2019") inside text fields — this is the property that caused every evaluated agent to score 0% on that dataset, because all of them reached for a single regex that couldn't handle the format variety. When designing a text-extraction split, decide up front whether you want "regex-solvable" (data-independent transformation, e.g. extracting a star count with `(\d+) stars`) or "regex-resistant" (data-dependent, requiring per-row judgment) — both are legitimate, but know which one you're building, since regex-resistant tasks are dramatically harder and should be used sparingly and intentionally.

## Description Discipline

`db_description.txt` should describe:

- logical database name,
- DBMS type,
- purpose,
- tables or collections,
- fields and field types,
- brief field-level descriptions.

Do not include a "Useful links" section, explicit join-key map, physical file paths, or solve strategy. The agent should infer cross-database interaction from field names, task wording, and optional dataset-level hints.

**Reference example (abbreviated from DAB's actual `bookreview` description):**

```text
1. books_database
   System: PostgreSQL. Contains Amazon book information including
   descriptions, price, details, title, etc., up to 2023.
   Tables:
   - books_info (Book information): title, subtitle, author,
     rating_number, features, description, price, store,
     categories, details, book_id

2. review_database
   System: SQLite. Contains Amazon book review information including
   ratings, review text, helpfulness votes, etc., up to 2023.
   Tables:
   - review (Review information): rating, title, text, purchase_id,
     review_time, helpful_vote, verified_purchase
```

Notice what's absent: no statement that `book_id` and `purchase_id` are joinable, no mention that `details` contains language info, no SQL hints. That information goes in `hints.txt` instead (see below), not the description.

## Avoid

- Ambiguous joins with no canonical resolution path.
- Unstated formulas or bucket semantics.
- Splits that require internet access.
- Multiple visible databases with the same DBMS type.
- Explicit join maps in `db_description.txt`, especially sections named "Useful links".
- One query per database; prefer 3-5 queries over the same split when the dataset is rich enough.
- MongoDB for arbitrary difficulty only; use it when documents, nested records, or text extraction are central to the task.

## Hints

DAB-style hints may explain:

- ID normalization rules.
- Formula definitions.
- Bucket/range semantics.
- Null/list matching behavior.
- Which DB contains which class of information.

**Reference example (DAB's actual `bookreview` hints.txt, in full):**

```text
- book_id (in books_info) and purchase_id (in review) refer to the
  same book entities and can be matched via fuzzy join despite
  differences in formats.
- Some queries may require information from details or categories
  in books_info.
```

Notice the calibration: the hint says fuzzy matching is *needed* and *where* the relevant text lives, but it doesn't give the prefix pattern (`bid_` vs `bref_`), doesn't give a regex, and doesn't say which specific query needs which hint. That's the right level of assistance — enough that a capable agent isn't stuck on context it has no way to discover (e.g. "this requires fuzzy matching" is fair; "the language is in details" is fair), but never the resolution itself.

Hints should not say which row wins or what numeric answer to expect.