# Prompt Templates

These are manual operator prompts. Do not run an LLM pipeline automatically unless the user explicitly asks.

## Dataset Brief Prompt

```text
Given this dataset profile, summarize the domain, important entities, likely joins,
text fields, numeric fields, time fields, and any columns that look like IDs.

Return:
1. Entity map
2. Likely join keys
3. Important measures
4. Possible domain formulas
5. Columns that should not appear directly in final visible DBs
```

## Candidate Query Prompt

```text
Given the schema profile and DAB task style, propose 10 candidate natural-language queries.

Constraints:
- Each final-worthy query must require at least two logical databases after the visible split.
- Each final-worthy query must require key normalization/fuzzy matching, text extraction/classification, domain knowledge/formula, or another semantic transformation.
- Avoid SQL-like wording.
- Prefer real analytical questions.
- Include expected answer type.
- Note which tables/databases would be needed.
- Note the challenge property: key repair / text extraction / domain formula / semantic transformation.
- Mark likely difficulty: easy / medium / hard.
```

## Selection Review Prompt

```text
Review these candidate queries for DAB-style training use.

For each query, assess:
- Is it solvable deterministically?
- Is the answer unique or does it need tie-breaking?
- Is it too easy?
- Is it too brittle?
- Which two or more logical DBs must be required after splitting?
- Which non-aggregation DAB challenge property does it require?
- What hint, if any, is needed?

Pick 3-5 final queries.
```

## Split Design Prompt

```text
For each selected query, propose a visible database split.

Required:
- Which tables go into which logical DB.
- Which DBMS type each logical DB uses. Do not repeat DBMS types.
- Which identifiers should be reformatted.
- Which lookup/domain information should be separated.
- Which raw columns should be hidden or transformed.
- Why the query remains solvable.
- What validation script should check.
- How every selected query requires at least two DBs.
```

## Hint Review Prompt

```text
Review these hints.

Classify each as:
- Necessary semantic convention
- Schema/navigation help
- Answer leak
- Unnecessary

Keep necessary conventions like formulas, bucket meanings, ID normalization,
and null/list matching behavior. Remove answer-specific hints.
```

## DB Description Prompt

```text
Write db_description.txt and db_description_withhint.txt in DAB style.

Constraints:
- In db_description.txt, use numbered logical databases.
- In db_description.txt, for each database, state the DBMS type, purpose, tables/collections, and fields with types.
- In db_description.txt, do not include physical paths, SQL snippets, "Useful links", explicit join maps, or solve strategy.
- db_description_withhint.txt must be hints-only. Start it with HINTS: and include only dataset-level semantic conventions, formulas, or transformation rules.
- Do not repeat the database description or schema in db_description_withhint.txt.
- Hints must not reveal any final query answer or name a winning row.
```
