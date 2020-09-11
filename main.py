import sys

from bs4 import BeautifulSoup
from collections import deque

import json
import time
import requests


def parse_refs(page):
    response = requests.get(page)
    soup = BeautifulSoup(response.content, 'html.parser')
    basic_url = page[:page.find('/wiki/')]
    return set({basic_url + a['href'] for a in soup.select('p a[href]') if a['href'].startswith('/wiki/')})


def is_valid(start_page, end_page):
    for page in [start_page, end_page]:
        if page.find('https://en.wikipedia.org/wiki/') == -1:
            return False
    return True


def find_path(start_page, end_page):
    path = {start_page: [start_page]}
    ref_queue = deque([start_page])
    while len(ref_queue) != 0:
        page = ref_queue.popleft()
        refs = parse_refs(page)
        for ref in refs:
            if ref in end_page:
                return path[page] + [ref]
            if (ref not in path) and (ref != page):
                path[ref] = path[page] + [ref]
                ref_queue.append(ref)
    return None


def format_refs(end):
    end_soup = BeautifulSoup(requests.get(end).content, 'html.parser')
    title = end_soup.find('h1').text
    title = title.replace(' ', '_', len(title))
    basic_url = end[:end.find('/wiki/') + len('/wiki/')]
    return {end, basic_url + title}


def result(start_page, end_page, path):
    d = {"start_page": start_page, "end_page": end_page, "path": path if path else "Not found"}
    return json.dumps(d, indent=4)


def run_search(start_page, end_page):
    if is_valid(start_page, end_page):
        path = find_path(start_page, format_refs(end_page))
        json_result = result(start_page, end_page, path)
        return json_result
    else:
        print("Pages not valid!")


if __name__ == '__main__':
    '''
    Run with args, for example:   
    python main.py "https://en.wikipedia.org/wiki/Battle_of_Cr%C3%A9cy" "https://en.wikipedia.org/wiki/Wehrmacht"
    '''
    start = time.time()
    print(run_search(sys.argv[1], sys.argv[2]))
    print('Time: {:.2f} sec'.format((time.time() - start) % 60))
