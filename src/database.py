import csv
import os
import io
from supabase import Client, create_client
import dotenv
from sqlalchemy import create_engine
import os
import dotenv
import sqlalchemy
import dotenv

# DO NOT CHANGE THIS TO BE HARDCODED. ONLY PULL FROM ENVIRONMENT VARIABLES.
dotenv.load_dotenv()
supabase_api_key = os.environ.get("SUPABASE_API_KEY")
supabase_url = os.environ.get("SUPABASE_URL")

if supabase_api_key is None or supabase_url is None:
    raise Exception(
        "You must set the SUPABASE_API_KEY and SUPABASE_URL environment variables."
    )

supabase: Client = create_client(supabase_url, supabase_api_key)
sess = supabase.auth.get_session()
def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("POSTGRES_USER")
    DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    DB_PORT: str = os.environ.get("POSTGRES_PORT")
    DB_NAME: str = os.environ.get("POSTGRES_DB")
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

# Create a new DB engine based on our connection string
engine = sqlalchemy.create_engine(database_connection_url())

movies = sqlalchemy.Table("movies", sqlalchemy.MetaData(), autoload_with=engine)
characters = sqlalchemy.Table("characters", sqlalchemy.MetaData(), autoload_with=engine)
conversations = sqlalchemy.Table("conversations", sqlalchemy.MetaData(), autoload_with=engine)
lines = sqlalchemy.Table("lines", sqlalchemy.MetaData(), autoload_with=engine)

# Create a single connection to the database. Later we will discuss pooling connections.
# conn = engine.connect()


# def upload(filename, content):
#     file = (
#         supabase.storage.from_("movie-api")
#         .download(filename)
#         .decode("utf-8")
#     )
#
#     data = []
#     for row in csv.DictReader(io.StringIO(file), skipinitialspace=True):
#         data.append(row)
#     for row in content:
#         data.append(row)
#
#     output = io.StringIO()
#     csv_writer = csv.DictWriter(output, fieldnames=list(content[0].keys()))
#     csv_writer.writeheader()
#     csv_writer.writerows(data)
#
#     supabase.storage.from_("movie-api").upload(
#         filename,
#         bytes(output.getvalue(), "utf-8"),
#         {"x-upsert": "true"},
#     )
#
# movies_file = supabase.storage.from_("movie-api").download("movies.csv").decode("utf-8")
# movies = {
#     movie['movie_id']: movie
#     for movie in csv.DictReader(io.StringIO(movies_file), skipinitialspace=True)
# }
#
# characters_file = supabase.storage.from_("movie-api").download("characters.csv").decode("utf-8")
# characters = {
#     character['character_id']: character
#     for character in csv.DictReader(io.StringIO(characters_file), skipinitialspace=True)
# }
#
# conversations_file = supabase.storage.from_("movie-api").download("conversations.csv").decode("utf-8")
# conversations = {
#     conversation['conversation_id']: conversation
#     for conversation in csv.DictReader(io.StringIO(conversations_file), skipinitialspace=True)
# }
#
# lines_file = supabase.storage.from_("movie-api").download("lines.csv").decode("utf-8")
# lines = {
#     line['line_id']: line
#     for line in csv.DictReader(io.StringIO(lines_file), skipinitialspace=True)
# }
#
# line_counts = {}
#
# with engine.begin() as conn:
#     result = conn.execute(
#         sqlalchemy.select().where(db.characters.c.character_id == id)
#     )

