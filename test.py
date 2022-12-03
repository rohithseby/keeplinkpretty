from bs4 import BeautifulSoup as bs
import requests
import json


# def parse_link(url):
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
#     }

#     page = requests.get(url, headers=headers)

#     soup = bs(page.content, "html.parser")
#     return soup.title.get_text()


# print(
#     parse_link(
#         "https://www.reddit.com/r/Kerala/comments/yst48j/brazilian_shingari_melam_at_qatar_2022/"
#     )
# )

data = {"content": None}

data["content"] = (
    "**-----------------------------------------------------------------------------------------------------------------**\n\n>>> **"
    + "Add External Python Libraries to AWS Lambda using Lambda Layers"
    + "**\n\n"
    + "https://www.linkedin.com/pulse/add-external-python-libraries-aws-lambda-using-layers-gabe-olokun/"
)

headers = {"Content-Type": "application/json"}

requests.post(
    url="https://discord.com/api/webhooks/1040932743414034472/mdFPZZ2pCm2ppNYQDw08dazGHbG-HijG0h4j6T9WCxsqcfT6ptP--gqy8SZ89omZzWH6",
    data=json.dumps(data),
    headers=headers,
)
