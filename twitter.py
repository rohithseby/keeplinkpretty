import requests
import json
import tweepy as tw
import datetime

client = tw.Client(
    r"AAAAAAAAAAAAAAAAAAAAAG%2FFiwEAAAAA5P8gm%2BzhuSLonYhDFtX5kOUWCbE%3DtYRaEnwoAFbMZ2JiZWsXiCKc2ZYtnsXvJbNdCGJXxBznfALWXd"
)

tweets_info = {}


def get_tweet_info(tweet_id):
    global tweets_info

    tweet = client.get_tweet(
        id=tweet_id,
        expansions=["author_id", "attachments.media_keys"],
        tweet_fields=["created_at"],
        user_fields=["username", "name"],
        media_fields=["preview_image_url", "url"],
    )

    tweet_info = {
        "name": "",
        "username": "",
        "text": "",
        "image_url": "",
        "preview_image_url": "",
    }

    if "media" in tweet.includes:
        tweet_info["preview_image_url"] = tweet.includes["media"][0].preview_image_url
        tweet_info["image_url"] = tweet.includes["media"][0].url

    tweet_info["name"] = tweet.includes["users"][0].name
    tweet_info["username"] = tweet.includes["users"][0].username
    tweet_info["text"] = tweet.data.text
    tweet_info["created_at"] = str(tweet.data.created_at.strftime("%m-%d-%Y %H:%M"))

    if str(tweet.data.id) == tweet_id:
        tweets_info[tweet_id] = tweet_info


def init_calls(ids):

    for id in ids:
        get_tweet_info(id)

    global tweets_info

    for info in tweets_info:
        for attr in tweets_info[info]:
            if tweets_info[info][attr] == None:
                tweets_info[info][attr] = ""

    with open("tweets.json", "w") as j:
        json.dump(tweets_info, j, indent=2)

    return tweets_info


# init_calls()