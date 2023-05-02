from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
import sqlalchemy as s

router = APIRouter()

@router.get("/movies/{movie_id}", tags=["movies"])
def get_movie(movie_id: str):
    """
    This endpoint returns a single movie by its identifier. For each movie it returns:
    * `movie_id`: the internal id of the movie.
    * `title`: The title of the movie.
    * `top_characters`: A list of characters that are in the movie. The characters
      are ordered by the number of lines they have in the movie. The top five
      characters are listed.

    Each character is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `num_lines`: The number of lines the character has in the movie.

    """

    stmt = (
        s.select(
            db.movies.c.movie_id,
            db.movies.c.title,
        )
        .where(db.movies.c.movie_id == movie_id)
    )
    with db.engine.connect() as conn:
        movies_result = conn.execute(stmt)

    movie = movies_result.first()

    if movie is None:
         raise HTTPException(status_code=404, detail="movie not found.")

    stmt = (
        s.select(
            db.characters.c.character_id,
            db.characters.c.name,
            s.func.count(db.lines.c.line_id).label('line_count')
        )
        .select_from(db.characters.join(db.lines, db.lines.c.character_id == db.characters.c.character_id).join(db.movies, db.movies.c.movie_id == db.characters.c.movie_id))
        .where(db.movies.c.movie_id == movie_id)
        .group_by(db.characters.c.character_id)
        .order_by(s.desc('line_count'))
        .limit(5)
    )

    with db.engine.connect() as conn:
        characters_result = conn.execute(stmt)

    top_characters = []

    for character in characters_result:
        top_characters.append(
            {
                'character_id': character.character_id,
                'character': character.name,
                'num_lines': character.line_count
            }
        )

    return {
        'movie_id': movie.movie_id,
        'title': movie.title,
        'top_characters': top_characters
    }

    # movie = db.movies.get(movie_id)
    # if movie is None:
    #     raise HTTPException(status_code=404, detail="movie not found.")
    #
    # line_counts = {}
    #
    # for line_id in db.lines:
    #     if db.lines[line_id]['movie_id'] == movie_id:
    #         if line_counts.get(db.lines[line_id]['character_id']) is None:
    #             line_counts[db.lines[line_id]['character_id']] = 1
    #         else:
    #             line_counts[db.lines[line_id]['character_id']] += 1
    #
    # top_characters = []
    #
    # for character_id in line_counts:
    #     top_characters.append(
    #         {
    #             'character_id': int(character_id),
    #             'character': db.characters[character_id]['name'],
    #             'num_lines': line_counts[character_id]
    #         }
    #     )
    # top_characters = sorted(top_characters, key=lambda x: x['num_lines'], reverse=True)
    # top_characters = top_characters[:5]
    # return {
    #     'movie_id': int(movie_id),
    #     'title': movie['title'],
    #     'top_characters': top_characters
    # }


class movie_sort_options(str, Enum):
    movie_title = "movie_title"
    year = "year"
    rating = "rating"


# Add get parameters
@router.get("/movies/", tags=["movies"])
def list_movies(
    name: str = "",
    limit: int = 50,
    offset: int = 0,
    sort: movie_sort_options = movie_sort_options.movie_title,
):
    """
    This endpoint returns a list of movies. For each movie it returns:
    * `movie_id`: the internal id of the movie. Can be used to query the
      `/movies/{movie_id}` endpoint.
    * `movie_title`: The title of the movie.
    * `year`: The year the movie was released.
    * `imdb_rating`: The IMDB rating of the movie.
    * `imdb_votes`: The number of IMDB votes for the movie.

    You can filter for movies whose titles contain a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `movie_title` - Sort by movie title alphabetically.
    * `year` - Sort by year of release, earliest to latest.
    * `rating` - Sort by rating, highest to lowest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """

    if sort is movie_sort_options.movie_title:
        order_by = db.movies.c.title
    elif sort is movie_sort_options.year:
        order_by = db.movies.c.year
    elif sort is movie_sort_options.rating:
        order_by = s.desc(db.movies.c.imdb_rating)
    else:
        assert False

    stmt = (
        s.select(
            db.movies.c.movie_id,
            db.movies.c.title,
            db.movies.c.year,
            db.movies.c.imdb_rating,
            db.movies.c.imdb_votes,
        )
        .limit(limit)
        .offset(offset)
        .order_by(order_by, db.movies.c.movie_id)
    )

    if name != "":
        stmt = stmt.where(db.movies.c.title.ilike(f"%{name}%"))

    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        for row in result:
            json.append(
                {
                    "movie_id": row.movie_id,
                    "movie_title": row.title,
                    "year": row.year,
                    "imdb_rating": row.imdb_rating,
                    "imdb_votes": row.imdb_votes,
                }
            )

    return json

    # movies = []
    #
    # for movie_id in db.movies:
    #     if str.upper(db.movies[movie_id]['title']).find(str.upper(name)) > -1:
    #         movies.append(
    #             {
    #                 'movie_id': int(movie_id),
    #                 'movie_title': db.movies[movie_id]['title'],
    #                 'year': db.movies[movie_id]['year'],
    #                 'imdb_rating': float(db.movies[movie_id]['imdb_rating']),
    #                 'imdb_votes': int(db.movies[movie_id]['imdb_votes'])
    #             }
    #         )
    #
    # if sort == movie_sort_options.movie_title:
    #     movies = sorted(movies, key=lambda x: x['movie_title'])
    # elif sort == movie_sort_options.year:
    #     movies = sorted(movies, key=lambda x: x['year'])
    # else:
    #     movies = sorted(movies, key=lambda x: x['imdb_rating'], reverse=True)
    #
    # return movies[offset:offset + limit]
