import gkeepapi as k
from dotenv import load_dotenv
import os
import twitter as t
from datetime import datetime
from server import keepalive
import schedule
import time


def twitter(keepObject):

    all_notes = keepObject.all()

    ids = []

    matching_id = {}

    keepObject.sync()

    twitter_label_id = keepObject.findLabel("Twitter").id

    for note in all_notes:
        if (
            note.text.strip().endswith("(/\)") == False
            and note.labels.get(twitter_label_id) != None
        ):
            current_link = note.text
            current_tweet_id = current_link.split("status/")[1].split("?")[0]
            cleaned_link = current_link.split("?")[0]
            current_note_id = note.id
            ids.append(current_tweet_id)

            matching_id[current_note_id] = {
                "tweet_id": current_tweet_id,
                "cleaned_link": cleaned_link,
            }

    dump = t.init_calls(ids)

    for id in matching_id:
        selected_tweet = dump[matching_id[id]["tweet_id"]]
        selected_note = keepObject.get(id)

        selected_note.title = (
            selected_tweet["text"].split("https://")[0]
            + "@"
            + selected_tweet["username"]
        )
        selected_note.text = matching_id[id]["cleaned_link"] + " \n(/\)"

    keepObject.sync()


def link_cleanup(keepObject):
    return None


def main():
    load_dotenv()

    email_id = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    keep = k.Keep()
    success = keep.login(email=email_id, password=password)

    keepalive()

    twitter(keep)

    schedule.every(30).seconds.do(twitter, keep)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
