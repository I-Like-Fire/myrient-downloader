import requests
import os
import sys
import json
import tempfile
import shutil

from math import ceil
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

temp_dir = tempfile.TemporaryDirectory()

def get_links(url, directory):
    link_data = {}
    web_page = requests.get(url=url)
    content = BeautifulSoup(web_page.text, 'html.parser')

    rows = content.find_all('tr')

    for r in rows:
        tag = r.select('a')[0]
        title = tag.get('title')
        
        if title is None or title == '.'or title == '..':
            continue
        
        link = url + tag.get('href')
        file_size = r.find_all('td', {'class': 'size'})[0].get_text()

        if link.endswith('/'):
            sub_data = get_links(link, directory + title)
            link_data = {**link_data, **sub_data}
        else:
            if file_size.endswith('GiB'):
                file_size = ((float(file_size[:-4]) * 1024) * 1024) * 1024
            elif file_size.endswith('MiB'):
                file_size = (float(file_size[:-4]) * 1024) * 1024
            elif file_size.endswith('KiB'):
                file_size = float(file_size[:-4]) * 1024
            elif file_size.endswith('B'):
                file_size = float(file_size[:-2])
            
            link_data[title] = {
                'title': title,
                'link': link,
                'directory': directory,
                'file_size': file_size
            }
    
    return link_data

def download(item):
    title = item['title']
    link = item['link']
    file_path = item['directory']

    if os.path.exists(f'{file_path}/{title}'):
        print(f'{title} already exists, skipping')
    else:
        response = requests.get(link, stream = True)

        total_size = int(response.headers.get("content-length", 0))
        block_size = 1024

        print(f"Downloading {title} ({total_size})")

        try:
            with open(f'{temp_dir.name}/{title}', "wb") as f:
                for data in response.iter_content(block_size):
                    f.write(data)
            if not os.path.exists(file_path):
                os.mkdir(file_path)
            shutil.move(f'{temp_dir.name}/{title}', f'{file_path}/{title}')
        except e:
            with open('Errors.txt', 'a') as error_file:
                error_file.write(f'{link}\n{file_path}\n')
                error_file.write(e + '\n')

        print(f"{title_unicode} finished downloading.\n")

def main(url):
    if os.path.exists('links.json'):
        print('Loading from file')
        with open('links.json', 'r') as f:
            links = json.load(f)       
    else:
        print('Getting links')
        links = get_links(url, os.getcwd() + '/')
        with open('links.json', 'w') as f:
            json.dump(links, f, ensure_ascii=False, indent=4)
        print('Links obtained')
    
    total_size = 0
    for key in links:
        total_size += links[key]['file_size']
    
    for i in ['B', 'KiB', 'MiB', 'GiB']:
        integer = str(total_size).split('.')[0]
        if len(integer) >= 4 and not i == 'GiB':
            total_size = total_size / 1024
        else:
            total_size = ceil(total_size * 100) / 100.0
            total_size = f'{total_size} {i}'
            break

    user_input = ''
    while user_input != 'y' and user_input != 'n':
        user_input = input(f"You're about to download approximately {total_size} of data. Continue? (Y/N): ")
        if user_input.lower() == 'y':
            threads = 6
            with ThreadPoolExecutor(max_workers=threads) as tpe:
                tpe.map(download, links.values())
        elif user_input.lower() != 'n':
            print('Choices are Y or N.')

    temp_dir.cleanup()
    print("Done")

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print("URL required")
        exit()
    
    main(sys.argv[1])
