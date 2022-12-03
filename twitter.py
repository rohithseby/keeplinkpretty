import requests
import os
from dotenv import load_dotenv
import tweepy as tw
import json
import datetime


def auth():
    API_KEY = os.getenv("API_KEY")

    client = tw.Client(API_KEY)

    return client


def get_tweet_info(tweet_id):
    tweet_info = {}
    # print(tweet_id)
    client = auth()

    tweet = client.get_tweet(
        id=tweet_id,
        expansions=["author_id", "attachments.media_keys"],
        tweet_fields=["created_at"],
        user_fields=["username", "name"],
        media_fields=["preview_image_url", "url"],
    )

    tweet_info = {}

    if "media" in tweet.includes:
        tweet_info["preview_image_url"] = tweet.includes["media"][0].preview_image_url
        tweet_info["image_url"] = tweet.includes["media"][0].url

    tweet_info["name"] = tweet.includes["users"][0].name
    tweet_info["username"] = tweet.includes["users"][0].username
    tweet_info["text"] = tweet.data.text
    tweet_info["created_at"] = str(tweet.data.created_at.strftime("%m-%d-%Y %H:%M"))

    return tweet_info
