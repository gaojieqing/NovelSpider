import os
import re
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup


class Spider(ABC):
    @abstractmethod
    def download(self, book_id):
        pass


# 书海阁
class ShuhaigeSpider(Spider):
    s = requests.Session()

    def download(self, book_id):
        super().download(book_id)
        book_title, chapters = self.fetch_book(book_id)
        print(f'{book_title} 开始下载')
        folder_path = os.path.dirname(os.path.abspath(__file__))
        while os.path.basename(folder_path) != "NovelSpider":
            folder_path = os.path.dirname(folder_path)
        file_path = os.path.join(folder_path, f'docs/{book_title}.md')
        with open(file_path, 'w') as f:
            for chapter_id in chapters.values():
                chapter_title, contents = self.fetch_chapter(book_id, chapter_id)
                f.write(f'# {chapter_title}\n')
                f.write('\n'.join(contents))
                f.write('\n\n')
                print(f'{chapter_title} 下载完成')

    def fetch_book(self, book_id: int):
        url = f'https://www.shuhaige.net/{book_id}/'
        response = self.get_retryable(url)

        book_title = ''
        chapters = {}
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            book_title = soup.find('meta', {'property': 'og:novel:book_name'}).get('content')
            for dd in soup.find('div', {'id': 'list'}).find_all('dd'):
                a = dd.find('a')
                chapters[a.text] = re.findall(r'\d+', a.get("href"))[1]
        return book_title, chapters

    def fetch_chapter(self, book_id: int, chapter_id: int):
        chapter_title = ''
        contents = []
        page = 1
        has_next = True
        while has_next:
            has_next = False
            url = f'https://www.shuhaige.net/{book_id}/{chapter_id}.html'
            if page > 1:
                url = f'https://www.shuhaige.net/{book_id}/{chapter_id}_{page}.html'
            print(url)
            response = self.get_retryable(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                chapter_title = soup.find('div', {'class': 'bookname'}).find('h1').text
                for p in soup.find('div', {'id': 'content'}).find_all('p'):
                    content = p.text
                    if '请点击下一页继续阅读' in content:
                        has_next = True
                    elif '请大家收藏：' not in content:
                        contents.append(content)
            else:
                print(f'{url} {response.status_code}')
            page += 1
        return chapter_title, contents

    def get_retryable(self, url: str):
        response = self.s.get(url)

        if response.status_code == 403:
            response = self.s.get(url)
        return response
