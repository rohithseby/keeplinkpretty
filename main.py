import gkeepapi as k
from dotenv import load_dotenv
import os
import twitter as t
from datetime import datetime
from server import keepalive
import schedule
import time
import json
import requests
from bs4 import BeautifulSoup as bs


def twitter(keepObject, notes):

    ids, matching_id = [], {}

    keepObject.sync()

    twitter_label_id = keepObject.findLabel("Twitter").id

    twitter_label = keepObject.getLabel(twitter_label_id)

    for note in notes:
        if (
            note.text.strip().startswith("https://twitter.com")
            and note.labels.get(twitter_label_id) == None
        ):
            note.labels.add(twitter_label)

        if (
            note.text.strip().endswith("(/\)") == False
            and note.labels.get(twitter_label_id) != None
        ):
            current_link = note.text.strip()
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
            + " @"
            + selected_tweet["username"]
        )
        selected_note.text = matching_id[id]["cleaned_link"] + "\n(/\)"

    print("twitter() - done")

    keepObject.sync()


def web_links(keepObject, notes):

    keepObject.sync()

    match = ["twitter.com", "www.reddit.com", "github.com"]

    weblinks_label_id = keepObject.findLabel("Web links").id

    weblinks_label = keepObject.getLabel(weblinks_label_id)

    for note in notes:
        check = 0
        note_text = note.text.strip()

        if note_text.startswith("http") and note_text.endswith("(/\)") == False:
            domain = note_text.split("//")[1].split("/")[0]
            if domain in match:
                check = 0
            else:
                check = 1
                web_link = note_text

        if check == 1:
            page = requests.get(web_link)
            soup = bs(page.content, "html.parser")
            note.title = soup.title.get_text()
            note.text = note.text + "\n(/\)"
            note.labels.add(weblinks_label)

    print("web_links() - done")

    keepObject.sync()


def reddit(keepObject, notes):
    keepObject.sync()

    match = "reddit.com"

    reddit_label_id = keepObject.findLabel("Reddit").id

    reddit_label = keepObject.getLabel(reddit_label_id)

    for note in notes:
        check = 0
        note_text = note.text.strip()

        if note_text.startswith("http") and note_text.endswith("(/\)") == False:
            domain = note_text.split("//")[1].split("/")[0]
            if match in domain:
                check = 1
                web_link = note_text

        if check == 1:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
            }
            page = requests.get(web_link, headers=headers)
            soup = bs(page.content, "html.parser")
            note.title = soup.title.get_text()
            note.text = note.text + "\n(/\)"
            note.labels.add(reddit_label)

    print("reddit() - done")

    keepObject.sync()


def discord(keepObject, notes):
    keepObject.sync()
    url = "https://discord.com/api/webhooks/1040932743414034472/mdFPZZ2pCm2ppNYQDw08dazGHbG-HijG0h4j6T9WCxsqcfT6ptP--gqy8SZ89omZzWH6"

    with open("discord.json", "r") as d:
        sent_tracker = json.load(d)

    headers = {"Content-Type": "application/json"}
    to_send = []
    data = {"content": None}

    for note in notes:
        id = str(note.id)
        linkcheck = 0
        if note.text.strip().startswith("http"):
            linkcheck = 1

        if linkcheck == 1:
            if id in sent_tracker and sent_tracker[id] == 0:
                to_send.append(note.text.split("(")[0])
                sent_tracker[id] = 1
            elif id not in sent_tracker:
                sent_tracker[id] = 0
                to_send.append(note.text.split("(")[0])
                sent_tracker[id] = 1
        else:
            continue

    fin = [*set(to_send)]
    for f in fin:
        data["content"] = f
        requests.post(url=url, data=json.dumps(data), headers=headers)

    with open("discord.json", "w") as dw:
        json.dump(sent_tracker, dw, indent=2)

    print("discord() - done")


def main():
    load_dotenv()

    email_id = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    keep = k.Keep()
    success = keep.login(email=email_id, password=password)

    keepalive()

    all_notes = keep.all()

    twitter(keep, all_notes)
    web_links(keep, all_notes)
    reddit(keep, all_notes)
    discord(keep, all_notes)

    schedule.every(2).minutes.do(twitter, keep, all_notes)
    schedule.every(2).minutes.do(web_links, keep, all_notes)
    schedule.every(2).minutes.do(reddit, keep, all_notes)
    schedule.every(2).minutes.do(discord, keep, all_notes)

    while True:
        schedule.run_pending()
        time.sleep(90)
        keep.sync()


if __name__ == "__main__":
    main()
