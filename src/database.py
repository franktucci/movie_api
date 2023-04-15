import csv

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
