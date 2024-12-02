from aiohttp import ClientSession
from bs4 import BeautifulSoup as bs
import asyncio
from typing import Set


async def fetch(url, session: ClientSession):
    async with session.get(url) as response:
        return await response.content.read()


async def get_urls(html: str, scraped_urls: Set[str]):
    soup = bs(html, "html.parser")
    # sidebar-content is the id of the sidebar in the docs
    elm = soup.find("div", {"id": "sidebar-content"})
    for a in elm.find_all("a", href=True):
        href = a["href"]
        if href.startswith("http"):
            scraped_urls.add(href)
        else:
            scraped_urls.add("https://docs.permify.co" + href)


async def main():
    async with ClientSession() as session:
        urls = [
            "https://docs.permify.co/permify-overview/intro",
            "https://docs.permify.co/getting-started/examples/intro",
            "https://docs.permify.co/modeling-guides/rbac/global-roles",
            "https://docs.permify.co/modeling-guides/abac/public-private",
            "https://docs.permify.co/modeling-guides/rebac/user-groups",
            "https://docs.permify.co/setting-up/installation/intro",
        ]
        set_urls = set()
        for url in urls:
            html = await fetch(url, session)
            # print(html)
            await get_urls(html, set_urls)
        print(set_urls)
        
        # write the urls to a file
        with open("urls.txt", "w") as f:
            for url in set_urls:
                f.write(url + "\n")
                


asyncio.run(main())
