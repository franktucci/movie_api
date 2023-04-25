from fastapi import APIRouter, HTTPException
from src import database as db
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter()

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
        raise HTTPException(status_code=404, detail="conversation not found.")

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
# FastAPI is inferring what the request body should look like
# based on the following two classes.
class LinesJson(BaseModel):
    character_id: int
    line_text: str


class ConversationJson(BaseModel):
    character_1_id: int
    character_2_id: int
    lines: List[LinesJson]

@router.post("/movies/{movie_id}/conversations/", tags=["movies"])
def add_conversation(movie_id: int, conversation: ConversationJson):
    """
    This endpoint adds a conversation to a movie. The conversation is represented
    by the two characters involved in the conversation and a series of lines between
    those characters in the movie.

    The endpoint ensures that all characters are part of the referenced movie,
    that the characters are not the same, and that the lines of a conversation
    match the characters involved in the conversation.

    Line sort is set based on the order in which the lines are provided in the
    request body.

    The endpoint returns the id of the resulting conversation that was created.
    """

    # The problem with this implementation is that there would be data lost if
    # two writes were to happen at the same time. The most recent call would go through,
    # but the earlier call would be overwritten as the later character_id would be computed
    # before the earlier call was written to the database. In fact, this would have all
    # sorts of funky implications, like how that would mean that character line counts
    # would become desynced in this implementation. Of course, unless our api
    # is handling a bunch of api calls per second the probability of this happening
    # is likely pretty negligible. And besides, the "happy path" nature of this assignment
    # means the input validation is very sub-par, which I feel is a more pressing issue...

    character1 = db.characters.get(str(conversation.character_1_id))
    character2 = db.characters.get(str(conversation.character_2_id))

    if character1 is None or character2 is None:
        raise HTTPException(status_code=404, detail="character not found.")
    if character1 == character2:
        raise HTTPException(status_code=422, detail="can't have a character talk to themself!")
    if character1['movie_id'] != str(movie_id) or character2['movie_id'] != str(movie_id):
        raise HTTPException(status_code=422, detail="movie_id given does not include one or both characters.")
    if character1['movie_id'] != character2['movie_id']:
        raise HTTPException(status_code=422, detail="characters given come from different movies.")
    if len(conversation.lines) == 0:
        raise HTTPException(status_code=422, detail="can't add an empty conversation!")

    lines = []

    sort = 1
    conversation_id = int(list(db.conversations)[-1]) + 1
    line_id = int(list(db.lines)[-1]) + 1
    for line in conversation.lines:
        if str(line.character_id) != character1['character_id'] and str(line.character_id) != character2['character_id']:
            raise HTTPException(status_code=422, detail="conversation/line character_id mismatch.")
        lines.append(
            {
                "line_id": str(line_id),
                "character_id": str(line.character_id),
                "movie_id": str(movie_id),
                "conversation_id": str(conversation_id),
                "line_sort": sort,
                "line_text": line.line_text
            }
        )
        sort += 1
        line_id += 1

    db.upload('lines.csv', lines)
    for line in lines:
        db.lines[line['line_id']] = line
        db.line_counts[str(line['character_id'])] += 1

    conversation_data = {
        "conversation_id": str(conversation_id),
        "character1_id": str(conversation.character_1_id),
        "character2_id": str(conversation.character_2_id),
        "movie_id": str(movie_id)
    }
    db.upload("conversations.csv", [conversation_data])
    db.conversations[conversation_data['conversation_id']] = conversation_data

    log_data = {
        "post_call_time": datetime.now(),
        "movie_id_added_to": str(movie_id)
    }
    db.upload("movie_conversations_log.csv", [log_data])

    return {
        'conversation_id': conversation_id
    }
