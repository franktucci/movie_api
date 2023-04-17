from fastapi import APIRouter, HTTPException
from enum import Enum
from collections import Counter

from fastapi.params import Query
from src import database as db

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

    line = db.lines.get(line_id)
    if line is None:
        raise HTTPException(status_code=404, detail="line not found.")

    if db.conversations[line['conversation_id']]['character1_id'] == line['character_id']:
        recipient_id = db.conversations[line['conversation_id']]['character2_id']
    else:
        recipient_id = db.conversations[line['conversation_id']]['character1_id']

    return {
        'line_id': int(line_id),
        'conversation_id': int(db.lines[line_id]['conversation_id']),
        'movie': db.movies[line['movie_id']]['title'],
        'character': db.characters[line['character_id']]['name'],
        'recipient': db.characters[recipient_id]['name'],
        'text': line['line_text']
    }

@router.get("/conversations/{conversation_id}", tags=["conversations"])
def get_conversation(conversation_id: str):
    """
    This endpoint returns a conversation by its identifier. For each conversation
    it returns:
    * `conversation_id`: the internal id of the conversation. Can be used to query the
      `/conversations/{conversation_id}` endpoint.
    * `movie`: The movie the line is from.
    * `lines`: A list of lines that are a part of the conversation. The lines
      are ordered by which the order they are said.

    Each line is represented by a dictionary with the following keys:
    * `line_id`: the internal id of the line.
    * `character`: The name of the character speaking.
    * `text`: The content of the line
    """

    conversation = db.conversations.get(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="line not found.")

    lines = []

    for line_id in db.lines:
        if db.lines[line_id]['conversation_id'] == conversation_id:
            lines.append(
                {
                    'line_id': int(line_id),
                    'character': db.characters[db.lines[line_id]['character_id']]['name'],
                    'text': db.lines[line_id]['line_text']
                }
            )

    return {
        'conversation_id': int(conversation_id),
        'movie': db.movies[db.conversations[conversation_id]['movie_id']]['title'],
        'lines': lines
    }
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

    lines = []

    for line_id in db.lines:
        if str.upper(db.lines[line_id]['line_text']).find(str.upper(text)) > -1 and db.characters[db.lines[line_id]['character_id']]['name'].find(str.upper(name)) > -1:
            lines.append(
                {
                    'line_id': int(line_id),
                    'movie_title': db.movies[db.lines[line_id]['movie_id']]['title'],
                    'character': db.characters[db.lines[line_id]['character_id']]['name'],
                    'text': db.lines[line_id]['line_text']
                }
            )

    if sort == line_sort_options.conversation:
        lines = sorted(lines, key=lambda x: db.lines[str(x['line_id'])]['conversation_id'])
    elif sort == line_sort_options.movie_title:
        lines = sorted(lines, key=lambda x: x['movie_title'])
    else:
        lines = sorted(lines, key=lambda x: x['character'])

    return lines[offset:offset + limit]
