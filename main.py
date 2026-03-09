import requests
import os
import sys
import json

from math import ceil
from bs4 import BeautifulSoup

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
            link_data.append(get_links(url, directory + title))
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
                'link': link,
                'directory': directory,
                'file_size': file_size,
                'Status': 'Not downloaded'
            }
    
    return link_data

def download(link, title, folder):
    title_unicode = title.encode(encoding='utf-8') # Required due to some file names using non-ASCII characters
    file_path = f'{folder}/{title}'

    if os.path.exists(file_path):
        print(f'{title_unicode} already exists, skipping')
    else:
        response = requests.get(link, stream = True)

        total_size = int(response.headers.get("content-length", 0))
        block_size = 1024

        print(f"Downloading {title_unicode} ({total_size})")

        try:
            with tqdm(total=total_size, unit="B", unit_scale=True) as progress_bar:
                with open(file_path, "wb") as f:
                    for data in response.iter_content(block_size):
                        progress_bar.update(len(data))
                        f.write(data)
        except:
            with open('Errors.txt', 'a') as error_file:
                error_file.write(f'{link}\n{file_path}\n')


        print(f"{title_unicode} finished downloading.\n")

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print("URL required")
        exit()

    url = sys.argv[1]

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
        if len(integer) > 4 and not i == 'GiB':
            total_size = total_size / 1024
        else:
            total_size = ceil(total_size * 100) / 100.0
            total_size = f'{total_size} {i}'
            break
    print(total_size)

    # for link in links:
    #     download(link[0], link[1], link[2])
    #     progress += 1
    #     print(f'                 Progress: {progress}/{len(links)}')

    print("Done")
