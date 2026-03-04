import requests
import os
import sys

from tqdm import tqdm
from bs4 import BeautifulSoup

def get_links(url):
    link_arr = []
    web_page = requests.get(url=url)
    content = BeautifulSoup(web_page.text, 'html.parser')

    for tags in content.find_all('td', {"class": "link"}): # Get links but skip 'parent', '.', and '..'
        tag = tags.select('a')[0]
        title = tag.get('title')
        if title is None or title == '.'or title == '..':
            continue
        
        link = url + tag.get('href')
        if link.endswith('/'): # Create subdirectories if found
            if not os.path.exists(title):
                os.mkdir(title)
            os.chdir(title)
            link_arr += get_links(link) # Recursive call for subdirectories
            os.chdir('..')
        else:
            link_arr.append((link, title, os.getcwd()))
    
    return link_arr

def download(link, title, folder):
    title_unicode = title.encode(encoding='utf-8') # Required due to some file names using non-ASCII characters
    file_path = f'{folder}/{title}'

    if os.path.exists(file_path):
        print(f'{title_unicode} already exists, skipping')
    else:
        response = requests.get(link, stream = True)

        total_size = int(response.headers.get("content-length", 0))
        block_size = 1024

        print(f"Downloading {title} ({total_size})")

        with tqdm(total=total_size, unit="B", unit_scale=True) as progress_bar:
            with open(file_path, "wb") as f:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    f.write(data)

        print(f"{title_unicode} finished downloading.\n")

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print("URL required")
        exit()

    url = sys.argv[1]
    links = get_links(url)
    progress = 0

    for link in links:
        download(link[0], link[1], link[2])
        progress += 1
        print(f'                 Progress: {progress}/{len(links)}')

    print("Done")
