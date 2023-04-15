from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db

router = APIRouter()


@router.get("/characters/{id}", tags=["characters"])
def get_character(id: str):
    """
    This endpoint returns a single character by its identifier. For each character
    it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `gender`: The gender of the character.
    * `top_conversations`: A list of characters that the character has the most
      conversations with. The characters are listed in order of the number of
      lines together. These conversations are described below.

    Each conversation is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `gender`: The gender of the character.
    * `number_of_lines_together`: The number of lines the character has with the
      originally queried character.
    """

    character = db.characters.get(id)
    if character is None:
        raise HTTPException(status_code=404, detail="movie not found.")

    gender = None
    if character['gender'] != '':
        gender = character['gender']

    conversations = {}

    for conversation_id in db.conversations:
        if db.conversations[conversation_id]['character1_id'] == id:
            recipient_id = db.conversations[conversation_id]['character2_id']
        elif db.conversations[conversation_id]['character2_id'] == id:
            recipient_id = db.conversations[conversation_id]['character1_id']
        else:
            continue

        if conversations.get(recipient_id) is None:
            conversations[recipient_id] = [db.conversations[conversation_id]]
        else:
            conversations[recipient_id].append(db.conversations[conversation_id])

    top_conversations = []

    for recipient_id in conversations:
        recipient_gender = None
        if db.characters[recipient_id]['gender'] != '':
            recipient_gender = db.characters[recipient_id]['gender']

        count = 0
        for conversation in conversations[recipient_id]:
            count += db.line_counts[conversation['conversation_id']]

        top_conversations.append(
            {
                'character_id': int(recipient_id),
                'character': db.characters[recipient_id]['name'],
                'gender': recipient_gender,
                'number_of_lines_together': count
            }
        )
    top_conversations = sorted(top_conversations, key=lambda x: x['number_of_lines_together'], reverse=True)

    return {
        'character_id': int(id),
        'character': character['name'],
        'movie': db.movies[character['movie_id']]['title'],
        'gender': gender,
        'top_conversations': top_conversations,
    }

class character_sort_options(str, Enum):
    character = "character"
    movie = "movie"
    number_of_lines = "number_of_lines"


@router.get("/characters/", tags=["characters"])
def list_characters(
    name: str = "",
    limit: int = 50,
    offset: int = 0,
    sort: character_sort_options = character_sort_options.character,
):
    """
    This endpoint returns a list of characters. For each character it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `number_of_lines`: The number of lines the character has in the movie.

    You can filter for characters whose name contains a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `character` - Sort by character name alphabetically.
    * `movie` - Sort by movie title alphabetically.
    * `number_of_lines` - Sort by number of lines, highest to lowest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """

    line_counts = {}

    for line_id in db.lines:
        if line_counts.get(db.lines[line_id]['character_id']) is None:
            line_counts[db.lines[line_id]['character_id']] = 1
        else:
            line_counts[db.lines[line_id]['character_id']] += 1

    characters = []

    for character_id in db.characters:
        if db.characters[character_id]['name'].find(str.upper(name)) > -1:
            characters.append(
                {
                    'character_id': int(character_id),
                    'character': db.characters[character_id]['name'],
                    'movie': db.movies[db.characters[character_id]['movie_id']]['title'],
                    'number_of_lines': line_counts[character_id]
                }
            )

    if sort == character_sort_options.character:
        characters = sorted(characters, key=lambda x: x['character'])
    elif sort == character_sort_options.movie:
        characters = sorted(characters, key=lambda x: x['movie'])
    else:
        characters = sorted(characters, key=lambda x: x['number_of_lines'], reverse=True)

    return characters[offset:offset + limit]
