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

# TODO: Below is purely an example of reading and then writing a csv from supabase.
# You should delete this code for your working example.

# START PLACEHOLDER CODE

# Reading in the log file from the supabase bucket
log_csv = (
    supabase.storage.from_("movie-api")
    .download("movie_conversations_log.csv")
    .decode("utf-8")
)

logs = []
for row in csv.DictReader(io.StringIO(log_csv), skipinitialspace=True):
    logs.append(row)


# Writing to the log file and uploading to the supabase bucket
def upload_new_log():
    output = io.StringIO()
    csv_writer = csv.DictWriter(
        output, fieldnames=["post_call_time", "movie_id_added_to"]
    )
    csv_writer.writeheader()
    csv_writer.writerows(logs)
    supabase.storage.from_("movie-api").upload(
        "movie_conversations_log.csv",
        bytes(output.getvalue(), "utf-8"),
        {"x-upsert": "true"},
    )


# END PLACEHOLDER CODE

def try_parse(type, val):
    try:
        return type(val)
    except ValueError:
        return None

with open("movies.csv", mode="r", encoding="utf8") as csv_file:
    movies = {
        movie['movie_id']: movie
        for movie in csv.DictReader(csv_file, skipinitialspace=True)
    }

with open("characters.csv", mode="r", encoding="utf8") as csv_file:
    characters = {
        character['character_id']: character
        for character in csv.DictReader(csv_file, skipinitialspace=True)
    }

with open("conversations.csv", mode="r", encoding="utf8") as csv_file:
    conversations = {
        conversation['conversation_id']: conversation
        for conversation in csv.DictReader(csv_file, skipinitialspace=True)
    }

with open("lines.csv", mode="r", encoding="utf8") as csv_file:
    lines = {
        line['line_id']: line
        for line in csv.DictReader(csv_file, skipinitialspace=True)
    }

line_counts = {}

for conversation_id in conversations:
    line_counts[conversation_id] = 0

for line_id in lines:
    line_counts[lines[line_id]['conversation_id']] += 1
