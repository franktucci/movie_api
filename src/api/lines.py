from fastapi import APIRouter, HTTPException
from enum import Enum
from collections import Counter
from fastapi.params import Query
from src import database as db
import sqlalchemy as s

router = APIRouter()

@router.get("/lines/{line_id}", tags=["lines"])
def get_lines(line_id: str):
    """
    This endpoint returns a single line by its identifier. For each line
    it returns:
    * `line_id`: the internal id of the line. Can be used to query the
      `/lines/{line_id}` endpoint.
    * `conversation_id`: the internal id of the conversation the line is said
      in. Can be used to query the `/convsersations/{coversation_id}` endpoint.
    * `movie`: The movie the line is from.
    * `character`: The name of the character speaking.
    * `recipient`: The name of the character being talked to.
    * `text`: The text of the line
    """

    stmt = (
        s.select(
            db.lines.c.line_id,
            db.lines.c.conversation_id,
            db.movies.c.title,
            db.characters.c.character_id,
            db.characters.c.name,
            db.lines.c.line_text
        )
        .select_from(db.lines.join(db.characters, db.lines.c.character_id == db.characters.c.character_id).join(db.movies, db.lines.c.movie_id == db.movies.c.movie_id))
        .where(db.lines.c.line_id == line_id)
    )
    with db.engine.connect() as conn:
        lines_result = conn.execute(stmt)

    line = lines_result.first()

    if line is None:
         raise HTTPException(status_code=404, detail="line not found.")

    stmt = (
        s.select(
            db.lines.c.line_id,
            db.conversations.c.character1_id,
            db.conversations.c.character2_id,
            db.characters.c.character_id,
            db.characters.c.name
        )
        .where(db.lines.c.line_id == line_id)
        .join(db.conversations, db.lines.c.conversation_id == db.conversations.c.conversation_id).join(db.characters, db.conversations.c.character1_id == db.characters.c.character_id)
        .filter(db.conversations.c.character1_id != line.character_id)
        .union(
            s.select(
                db.lines.c.line_id,
                db.conversations.c.character1_id,
                db.conversations.c.character2_id,
                db.characters.c.character_id,
                db.characters.c.name
            )
            .where(db.lines.c.line_id == line_id)
            .join(db.conversations, db.lines.c.conversation_id == db.conversations.c.conversation_id).join(db.characters, db.conversations.c.character2_id == db.characters.c.character_id)
            .filter(db.conversations.c.character2_id != line.character_id)
        )
    )

    with db.engine.connect() as conn:
        receiving_result = conn.execute(stmt)

    recipient = receiving_result.first()

    return {
        'line_id': line.line_id,
        'conversation_id': line.conversation_id,
        'movie': line.title,
        'character': line.name,
        'recipient': recipient.name,
        'text': line.line_text
    }

    # line = db.lines.get(line_id)
    # if line is None:
    #     raise HTTPException(status_code=404, detail="line not found.")
    #
    # if db.conversations[line['conversation_id']]['character1_id'] == line['character_id']:
    #     recipient_id = db.conversations[line['conversation_id']]['character2_id']
    # else:
    #     recipient_id = db.conversations[line['conversation_id']]['character1_id']
    #
    # return {
    #     'line_id': int(line_id),
    #     'conversation_id': int(db.lines[line_id]['conversation_id']),
    #     'movie': db.movies[line['movie_id']]['title'],
    #     'character': db.characters[line['character_id']]['name'],
    #     'recipient': db.characters[recipient_id]['name'],
    #     'text': line['line_text']
    # }

class line_sort_options(str, Enum):
    character = "character"
    movie_title = "movie"
    conversation = "conversation"

@router.get("/lines/", tags=["lines"])
def lines(
    text: str = "",
    name: str = "",
    limit: int = 50,
    offset: int = 0,
    sort: line_sort_options = line_sort_options.movie_title,
):
    """
    This endpoint returns a list of lines. For each line it returns:
    * `line_id`: the internal id of the line. Can be used to query the
      `/lines/{line_id}` endpoint.
    * `movie_title`: The movie the line is from.
    * `character`: The name of the character speaking.
    * `text`: The text of the line

    You can filter for the text of a line by using the `text` query
    parameter and/or the character speaking using the `name` query parameter

    You can also sort the results by using the `sort` query parameter:
    * `character` - Sort by character name alphabetically.
    * `movie` - Sort by movie title alphabetically.
    * `conversation` - Sort by conversation id numerically.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """

    if sort is line_sort_options.movie_title:
        order_by = db.movies.c.title
    elif sort is line_sort_options.conversation:
        order_by = db.lines.c.conversation_id
    elif sort is line_sort_options.character:
        order_by = db.characters.c.name
    else:
        assert False

    stmt = (
        s.select(
            db.lines.c.line_id,
            db.lines.c.conversation_id,
            db.movies.c.title,
            db.characters.c.name,
            db.lines.c.line_text,
        )
        .select_from(db.lines.join(db.movies, db.lines.c.movie_id == db.movies.c.movie_id).join(db.characters, db.lines.c.character_id == db.characters.c.character_id))
        .limit(limit)
        .offset(offset)
        .order_by(order_by, db.lines.c.line_id)
    )

    if name != "":
        stmt = stmt.where(db.characters.c.name.ilike(f"%{name}%"))

    if text != "":
        stmt = stmt.where(db.lines.c.line_text.ilike(f"%{text}%"))

    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        for row in result:
            json.append(
                {
                    'line_id': row.line_id,
                    'movie_title': row.title,
                    'character': row.name,
                    'text': row.line_text
                }
            )

    print(json)
    return json

    # lines = []
    #
    # for line_id in db.lines:
    #     if str.upper(db.lines[line_id]['line_text']).find(str.upper(text)) > -1 and db.characters[db.lines[line_id]['character_id']]['name'].find(str.upper(name)) > -1:
    #         lines.append(
    #             {
    #                 'line_id': int(line_id),
    #                 'movie_title': db.movies[db.lines[line_id]['movie_id']]['title'],
    #                 'character': db.characters[db.lines[line_id]['character_id']]['name'],
    #                 'text': db.lines[line_id]['line_text']
    #             }
    #         )
    #
    # if sort == line_sort_options.conversation:
    #     lines = sorted(lines, key=lambda x: db.lines[str(x['line_id'])]['conversation_id'])
    # elif sort == line_sort_options.movie_title:
    #     lines = sorted(lines, key=lambda x: x['movie_title'])
    # else:
    #     lines = sorted(lines, key=lambda x: x['character'])
    #
    # return lines[offset:offset + limit]
