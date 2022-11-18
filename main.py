import gkeepapi as k
from dotenv import load_dotenv
import os
import twitter as t
from server import keepalive
import schedule
from keyring import get_keyring
import time
import json
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime


def twitter(keepObject, notes):

    ids, matching_id = [], {}

    keepObject.sync()

    twitter_label_id = keepObject.findLabel("Twitter").id

    twitter_label = keepObject.getLabel(twitter_label_id)
    notes = sorted(notes, key=lambda x: x.timestamps.created)

    for note in notes:
        if (
            note.text.startswith("http")
            and "-tw" not in note.text.split("|-|")[1]
            and note.text.split("//")[1].split("/")[0] == "twitter.com"
        ):
            current_link = note.text.strip()
            current_tweet_id = current_link.split("status/")[1].split("|")[0].strip()
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
            + " @"
            + selected_tweet["username"]
        )
        selected_note.text = matching_id[id]["cleaned_link"] + "-tw"

    print("twitter() - done @", datetime.now())

    keepObject.sync()


def discord(keepObject, notes, url):
    keepObject.sync()

    with open("discord.json", "r") as d:
        sent_tracker = json.load(d)

    headers = {"Content-Type": "application/json"}
    to_send = {}
    data = {"content": None}

    notes = sorted(notes, key=lambda x: x.timestamps.created)

    for note in notes:

        id = str(note.id)
        if id in sent_tracker and sent_tracker[id] == 0:
            to_send[note.title] = note.text.split("|-|")[0].strip()
            sent_tracker[id] = 1
        elif id not in sent_tracker:
            sent_tracker[id] = 0
            to_send[note.title] = note.text.split("|-|")[0].strip()
            sent_tracker[id] = 1
        else:
            continue

    for send in to_send:
        data["content"] = (
            "**-----------------------------------------------------------------------------------------------------------------**\n\n>>> **"
            + send
            + "**\n\n"
            + to_send[send]
        )
        requests.post(url=url, data=json.dumps(data), headers=headers)
        time.sleep(3)

    with open("discord.json", "w") as dw:
        json.dump(sent_tracker, dw, indent=2)

    keepObject.sync()

    print("discord() - done @", datetime.now())

    keepObject.sync()


def sort(keepObject, notes):
    keepObject.sync()

    text_label_id = keepObject.findLabel("Text").id
    text_label = keepObject.getLabel(text_label_id)

    twitter_label_id = keepObject.findLabel("Twitter").id
    twitter_label = keepObject.getLabel(twitter_label_id)

    reddit_label_id = keepObject.findLabel("Reddit").id
    reddit_label = keepObject.getLabel(reddit_label_id)

    weblinks_label_id = keepObject.findLabel("Web links").id
    weblinks_label = keepObject.getLabel(weblinks_label_id)

    youtube_label_id = keepObject.findLabel("Youtube").id
    youtube_label = keepObject.getLabel(youtube_label_id)

    github_label_id = keepObject.findLabel("GitHub").id
    github_label = keepObject.getLabel(github_label_id)

    matching = {
        "twitter.com": twitter_label,
        "youtube.com": youtube_label,
        "www.reddit.com": reddit_label,
        "web_link": weblinks_label,
        "github.com": github_label,
        "youtu.be": youtube_label,
    }

    for note in notes:
        note_text = note.text
        domain_name = ""
        if note.text.startswith("http") and "-s" not in note_text.split("|-|")[1]:
            domain_name = note_text.split("//")[1].split("/")[0]
            if domain_name in matching:
                note.labels.add(matching[domain_name])
                note.text = note_text + "-s"
            else:
                note.labels.add(matching["web_link"])
                note.text = note_text + "-s"
        elif "-s" not in note_text:
            note.labels.add(text_label)
            note.text = note_text + "-s"

    print("sort() - done @", datetime.now())

    keepObject.sync()


def get_title(keepObject, notes):
    keepObject.sync()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    }
    for note in notes:
        note_text = note.text

        if (
            note_text.startswith("http")
            and note_text.split("//")[1].split("/")[0] != "twitter.com"
            and "-ti" not in note_text.split("|-|")[1]
        ):
            web_link = note_text.split("|")[0].strip()
            page = requests.get(web_link, headers=headers)
            soup = bs(page.content, "html.parser")
            note.title = soup.title.get_text()
            note.text = note_text + "-ti"
        else:
            continue

    keepObject.sync()

    print("get_title() = done @", datetime.now())


def removes(keepObject, notes):
    keepObject.sync()

    for note in notes:
        if note.text.strip().endswith("-t"):
            note.text = note.text.split("-t")[0].strip()

    keepObject.sync()


def add_seperator(keepObject, notes):
    keepObject.sync()
    for note in notes:
        if "|-|" not in note.text:
            note.text = note.text + "\n|-|"
    keepObject.sync()

    print("add_seperator() - done @", datetime.now())


def main():
    load_dotenv()
    email_id = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    url = os.getenv("DISCORD_URL")
    keep = k.Keep()
    success = keep.login(email=email_id, password=password)

    keepalive()

    all_notes = keep.all()

    add_seperator(keep, all_notes)
    get_title(keep, all_notes)
    twitter(keep, all_notes)
    # removes(keep, all_notes)
    sort(keep, all_notes)
    discord(keep, all_notes, url)

    schedule.every(20).seconds.do(add_seperator, keep, all_notes)
    schedule.every(20).seconds.do(get_title, keep, all_notes)
    schedule.every(120).seconds.do(twitter, keep, all_notes)
    schedule.every(120).seconds.do(sort, keep, all_notes)
    schedule.every(120).seconds.do(discord, keep, all_notes, url)

    while True:
        schedule.run_pending()
        time.sleep(10)
        keep.sync()


if __name__ == "__main__":
    main()
