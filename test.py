from bs4 import BeautifulSoup as bs
import requests


def parse_link(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    }

    page = requests.get(url, headers=headers)

    soup = bs(page.content, "html.parser")
    return soup.title.get_text()


print(
    parse_link(
        "https://www.reddit.com/r/Kerala/comments/yst48j/brazilian_shingari_melam_at_qatar_2022/"
    )
)
