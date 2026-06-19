# DB Description Examples

Use this reference when writing `db_description.txt` and `db_description_withhint.txt`.

## Rules

- `db_description.txt` describes logical database names, DBMS type, purpose, tables/collections, fields, and field types.
- `db_description_withhint.txt` is hints-only. It should start with `HINTS:` and should not repeat the database description or schema.
- Do not include physical paths, SQL snippets, solve strategy, or a "Useful links" section in either file.
- Do not provide explicit join maps such as `article_id links articles to article_metadata` in `db_description.txt`.
- Hints are dataset-level. They may describe semantic conventions, formulas, key normalization rules, or category definitions, but must not reveal final answers.

## One-Shot `db_description.txt`

```text
You are working with two databases to solve this query.

Here are the descriptions of these two databases:

1. articles_database
   - This database is stored in a MongoDB database and contains information about news articles. It serves as the primary source for the content of each article, including its title and description.
   - This database consists of one collection:
     - articles
       - This collection contains the actual news articles. Each document in the collection represents a single news article with its unique identifier, title, and description.
       - Fields:
         - _id
         - article_id (int): Unique identifier for the article
         - title (str): Title of the news article
         - description (str): Description of the news article

2. metadata_database
   - This database is stored in a SQLite database and contains metadata about the news articles. It includes information about the authors, the regions in which the articles were published, and the publication dates.
   - This database consists of two tables:
     - authors
       - This table contains information about all authors who contributed to the articles in the articles_database.
       - Fields:
         - author_id (int): Unique identifier for the author
         - name (str): Full name of the author

     - article_metadata
       - This table contains metadata linking each article to its author and providing details about its publication. Each row represents a single article and connects it to an author and publication information.
       - Fields:
         - article_id (int): Article identifier
         - author_id (int): Author identifier
         - region (str): Geographic region where the article was published
         - publication_date (str): Publication date in the format YYYY-MM-DD
```

## One-Shot `db_description_withhint.txt`

This file should contain only hints and nothing else. The runner appends it to `db_description.txt` when hints are enabled.

```text
HINTS:
- Determining an article's category requires understanding the meaning of its title and description.
- All articles belong to one of four categories: World, Sports, Business, or Science/Technology.
```
