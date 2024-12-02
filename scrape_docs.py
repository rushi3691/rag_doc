from aiohttp import ClientSession
from bs4 import BeautifulSoup as bs
import asyncio


async def fetch(url, session: ClientSession):
    async with session.get(url) as response:
        return await response.content.read()


async def get_content(html: str):
    soup = bs(html, "html.parser")
    
    title = soup.title.string
    print(title)
    
    # content-area is the id of the main content area in the docs
    content = soup.find("div", {"id": "content-area"})
    all_text = content.get_text()
    return all_text, title


async def main():
    async with ClientSession() as session:
        with open("urls.txt", "r") as f:
            urls = f.readlines()
            urls = [url.strip() for url in urls]

        for id, url in enumerate(urls):
            html = await fetch(url, session)
            content, title = await get_content(html)
            safe_title = title.replace("/", "_")

            # print(title)
            # write the content to a file
            with open(f"docs/{safe_title}.txt", "w") as f:
                f.write("\n")
                f.write(url)
                f.write("\n")
                f.write(content)
                


asyncio.run(main())
