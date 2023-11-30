import logging
import os
import re

import execjs
from httpx import Client
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TransferSpeedColumn
)
from user_agent import generate_user_agent


class Colors:
    GREEN = '\033[38;5;121m'
    DARKBLUE = '\033[38;5;20m'
    LPURPLE = '\033[38;5;141m'
    END = '\033[0m'


class SnaptikDownloader:
    TIMEOUT = 10
    DECODER_FILE = 'decoder.js'
    DIRECTORY = 'Tiktok Videos'
    HEADERS = {'User-Agent': generate_user_agent()}

    def __init__(self, tiktok_url, logging_enabled=True):
        self.tiktok_url = tiktok_url
        self.logging_enabled = logging_enabled
        self.client = Client(headers=self.HEADERS, timeout=self.TIMEOUT)
        self.token = None
        self.video_link = None
        self.video_id = None

        if self.logging_enabled:
            logging.basicConfig(level=logging.INFO)

    def __del__(self):
        self.client.close()

    def _get_token(self):
        response = self.client.get('https://snaptik.app/')
        response.raise_for_status()
        matches = re.search(r'name="token" value="(.*?)"', response.text)
        self.token = matches.group(1) if matches else None

    def _get_variable(self):
        data = {'url': self.tiktok_url, 'token': self.token}
        response = self.client.post('https://snaptik.app/abc2.php', data=data)
        response.raise_for_status()
        return response.text

    def _extract_variable(self, variable_text):
        pattern = r'\("(\w+)",(\d+),"(\w+)",(\d+),(\d+),(\d+)\)'
        return re.search(pattern, variable_text).groups()

    def _variable_decoder(self, variable_tuple):
        with open(self.DECODER_FILE, 'r') as file:
            javascript_code = file.read()

        context = execjs.compile(javascript_code)
        return context.call('result', *variable_tuple)

    def _match_pattern(self, pattern, html_source):
        matches = re.search(pattern, html_source)
        return matches.group(1) if matches else None

    def _contains_string(self, video_link, substring):
        return video_link if substring in video_link else None

    def _extract_snaptik_link(self, html_source):
        pattern = r'href=\\"([^\\"]+)\\"'
        matched_link = self._match_pattern(pattern, html_source)
        return self._contains_string(matched_link, 'snaptik') if matched_link else None

    def _video_downloader(self):
        with self.client.stream('GET', self.video_link) as response:
            response.raise_for_status()

            os.makedirs(self.DIRECTORY, exist_ok=True)
            filename = f'{self.DIRECTORY}/Snaptik.app_{self.video_id}.mp4'

            total_size = int(response.headers.get('content-length', 0))
            with Progress(
                    TextColumn('[cyan]{task.description}'),
                    BarColumn(),
                    DownloadColumn(),
                    TransferSpeedColumn()
                ) as progress:

                task = progress.add_task('Downloading...', total=total_size)

                with open(filename, 'wb') as file:
                    for data in response.iter_bytes(chunk_size=1024):
                        file.write(data)
                        progress.update(task, advance=len(data))

            print(f'Video has been saved in {Colors.LPURPLE}{filename}{Colors.END}\n')

    def _get_video_id(self):
        if self.tiktok_url.startswith('https://v'):
            self.video_id = self.tiktok_url.split('/')[-1]
        elif self.tiktok_url.startswith('https://www'):
            self.video_id = self.tiktok_url.split('/')[5].split('?')[0]
        elif not self.tiktok_url.startswith('https://'):
            raise ValueError('Check your URL!')

    def start_download(self):
        self._get_token()
        variable_text = self._get_variable()
        fetch_variable = self._extract_variable(variable_text)
        html_source = self._variable_decoder(fetch_variable)
        self.video_link = self._extract_snaptik_link(html_source)
        self._get_video_id()
        self._video_downloader()

