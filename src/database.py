import csv
import os
import io
from supabase import Client, create_client
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

def upload(filename, content):
    file = (
        supabase.storage.from_("movie-api")
        .download(filename)
        .decode("utf-8")
    )

    data = []
    for row in csv.DictReader(io.StringIO(file), skipinitialspace=True):
        data.append(row)
    for row in content:
        data.append(row)

    output = io.StringIO()
    csv_writer = csv.DictWriter(output, fieldnames=list(content[0].keys()))
    csv_writer.writeheader()
    csv_writer.writerows(data)

    supabase.storage.from_("movie-api").upload(
        filename,
        bytes(output.getvalue(), "utf-8"),
        {"x-upsert": "true"},
    )

movies_file = supabase.storage.from_("movie-api").download("movies.csv").decode("utf-8")
movies = {
    movie['movie_id']: movie
    for movie in csv.DictReader(io.StringIO(movies_file), skipinitialspace=True)
}

characters_file = supabase.storage.from_("movie-api").download("characters.csv").decode("utf-8")
characters = {
    character['character_id']: character
    for character in csv.DictReader(io.StringIO(characters_file), skipinitialspace=True)
}

conversations_file = supabase.storage.from_("movie-api").download("conversations.csv").decode("utf-8")
conversations = {
    conversation['conversation_id']: conversation
    for conversation in csv.DictReader(io.StringIO(conversations_file), skipinitialspace=True)
}

lines_file = supabase.storage.from_("movie-api").download("lines.csv").decode("utf-8")
lines = {
    line['line_id']: line
    for line in csv.DictReader(io.StringIO(lines_file), skipinitialspace=True)
}

line_counts = {}

for conversation_id in conversations:
    line_counts[conversation_id] = 0

for line_id in lines:
    line_counts[lines[line_id]['conversation_id']] += 1
