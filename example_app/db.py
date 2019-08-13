from databases import Database


database = Database("sqlite:///example_app/test.db")


async def create_tables() -> None:
    # Create Authors
    query = """
        CREATE TABLE IF NOT EXISTS authors(
            id INTEGER PRIMARY KEY,
            name VARCHAR(128)
        );
    """
    await database.execute(query=query)

    # Create Posts
    query = """
        CREATE TABLE IF NOT EXISTS posts(
            id INTEGER PRIMARY KEY,
            title VARCHAR(128),
            text VARCHAR(512),
            author_id INTEGER,
            FOREIGN KEY (author_id) REFERENCES authors(id)
        );
    """
    await database.execute(query=query)

    # Create comments
    query = """
        CREATE TABLE IF NOT EXISTS comments(
            id INTEGER PRIMARY KEY,
            text VARCHAR(512),
            author_id INTEGER,
            post_id INTEGER,
            FOREIGN KEY (author_id) REFERENCES authors(id),
            FOREIGN KEY (post_id) REFERENCES posts(id)
        );"""
    await database.execute(query=query)


async def drop_tables() -> None:
    for table in ["authors", "posts", "comments"]:
        query = f"DROP TABLE IF EXISTS {table}"
        await database.execute(query)


async def insert_data() -> None:
    # Insert authors
    query = """INSERT INTO authors(id, name) VALUES (:id, :name)"""
    values = [
        {"id": 1, "name": "Author 1"},
        {"id": 2, "name": "Author 2"},
        {"id": 3, "name": "Author 3"},
    ]
    await database.execute_many(query=query, values=values)

    # Insert posts
    query = """
        INSERT INTO posts(id, title, text, author_id) VALUES (:id, :title, :text, :author_id)
    """
    values = [
        {"id": 1, "title": "Title 1", "text": "Post 1", "author_id": "1"},
        {"id": 2, "title": "Title 2", "text": "Post 2", "author_id": "1"},
        {"id": 3, "title": "Title 3", "text": "Post 3", "author_id": "2"},
        {"id": 4, "title": "Title 4", "text": "Post 4", "author_id": "2"},
        {"id": 5, "title": "Title 5", "text": "Post 5", "author_id": "3"},
        {"id": 6, "title": "Title 6", "text": "Post 6", "author_id": "3"},
    ]
    await database.execute_many(query=query, values=values)

    # Insert comments
    query = """
        INSERT INTO comments(id, text, author_id, post_id) VALUES (:id, :text, :author_id, :post_id)
    """
    values = [
        {"id": 1, "post_id": 1, "text": "Comment 1", "author_id": "2"},
        {"id": 2, "post_id": 1, "text": "Comment 2", "author_id": "3"},
        {"id": 3, "post_id": 2, "text": "Comment 3", "author_id": "2"},
        {"id": 4, "post_id": 2, "text": "Comment 4", "author_id": "3"},
        {"id": 5, "post_id": 3, "text": "Comment 5", "author_id": "1"},
        {"id": 6, "post_id": 3, "text": "Comment 6", "author_id": "2"},
        {"id": 7, "post_id": 3, "text": "Comment 7", "author_id": "3"},
    ]
    await database.execute_many(query=query, values=values)

    # # Run a database query.
    # query = "SELECT * FROM HighScores"
    # rows = await database.fetch_all(query=query)
    # print('High Scores:', rows)


async def truncate_tables() -> None:
    for table in ["authors", "posts", "comments"]:
        query = f"DELETE FROM {table}"
        await database.execute(query)
