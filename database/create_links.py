import requests
from bs4 import BeautifulSoup


def create_links():
    link_page = requests.get("https://webrobots.io/kickstarter-datasets/")
    bs_object = BeautifulSoup(link_page.text, 'html.parser')
    bs_links = bs_object.find_all("a")
    bs_links = [str(link.get("href")) for link in bs_links]
    csv_links = [link for link in bs_links if link.endswith('Z.zip')]
    json_links = [link for link in bs_links if "kickstarter_old" in link]
    full_links = csv_links + json_links
    return full_links
