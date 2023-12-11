import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from httpx import Client
from rich import print
from rich.box import HEAVY
from rich.console import Group
from rich.live import Live
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn
)
from rich.traceback import install
from user_agent import generate_user_agent

from decoder import deobfuscator
from exception import InvalidUrl, UrlNotFound

install(theme='fruity')


class SnaptikDownloader:
    TIMEOUT = 10
    DIRECTORY = 'Tiktok Videos'
    BASE_URL = 'https://snaptik.app'
    HEADERS = {'User-Agent': generate_user_agent()}

    def __init__(self, transient: bool, instant_clear: bool, enable_log: bool):
        self.transient = transient
        self.instant_clear = instant_clear
        self.enable_log = enable_log
        self.client = Client(headers=self.HEADERS, timeout=self.TIMEOUT)

        if self.enable_log:
            self._setup_logging()

    def __del__(self):
        self.client.close()

    def _setup_logging(self):
        logging.basicConfig(
            level='INFO',
            format='%(message)s',
            datefmt='[%I:%M:%S %p]',
            handlers=[RichHandler()]
        )

    def _get_token(self):
        response = self.client.get(self.BASE_URL)
        response.raise_for_status()
        matches = re.search(r'name="token" value="(.*?)"', response.text)
        return matches.group(1) if matches else None

    def _get_variable(self, tiktok_url, token):
        data = {'url': tiktok_url, 'token': token}
        response = self.client.post(f'{self.BASE_URL}/abc2.php', data=data)
        response.raise_for_status()
        return response.text

    def _extract_variable(self, variable_text):
        pattern = r'\("(\w+)",\d+,"(\w+)",(\d+),(\d+),\d+\)'
        return re.search(pattern, variable_text).groups()

    def _variable_decoder(self, variable_tuple):
        con_var = [int(x) if x.isdigit() else x for x in variable_tuple]
        return deobfuscator(*con_var)

    def _match_pattern(self, pattern, html_source):
        matches = re.search(pattern, html_source)
        return matches.group(1) if matches else None

    def _contains_string(self, video_link, substring):
        return video_link if substring in video_link else None

    def _extract_snaptik_link(self, html_source):
        pattern = r'href=\\"([^\\"]+)\\"'
        matched_link = self._match_pattern(pattern, html_source)
        return self._contains_string(matched_link, 'snaptik') if matched_link else None

    def _extract_single_link(self, tiktok_url):
        token = self._get_token()
        variable_text = self._get_variable(tiktok_url, token)
        fetch_variable = self._extract_variable(variable_text)
        html_source = self._variable_decoder(fetch_variable)
        return self._extract_snaptik_link(html_source)

    def _download_single_video(self, progress, task_id, video_link, filename, overall_progress, overall_task):
        try:
            with self.client.stream('GET', video_link) as response:
                response.raise_for_status()
                self._process_response(progress, task_id, response, filename, overall_progress, overall_task)
        except Exception as exc:
            self._handle_download_error(filename, exc)
        finally:
            self._handle_progress_clear(progress, task_id)

    def _process_response(self, progress, task_id, response, filename, overall_progress, overall_task):
        total_size = int(response.headers.get('content-length', 0))
        progress.update(task_id, total=total_size)

        with open(filename, 'wb') as file:
            progress.start_task(task_id)
            for data in response.iter_bytes(chunk_size=1024):
                file.write(data)
                progress.update(task_id, advance=len(data))

            print(f'Video has been saved in [magenta]{filename}[/]')
            overall_progress.update(overall_task, advance=1)

    def _handle_download_error(self, filename, error):
        print(f'Download failed: [magenta]{filename}[/]: [bold red1]{type(error).__name__}[/]')

    def _handle_progress_clear(self, progress, task_id):
        if self.instant_clear:
            progress.remove_task(task_id)

    def _load_urls(self, filename):
        with open(filename, 'r') as file:
            urls = [x.strip() for x in file]
            if not urls:
                raise UrlNotFound(f'No URLs found in file "{filename}".')
            return urls

    def _sanitize_tiktok_url(self, url):
        tiktok_patterns = [
            r'https://vt\.tiktok\.com/\w+',
            r'https://vm\.tiktok\.com/\w+/',
            r'https://www\.tiktok\.com/@\w+/video/\w+',
        ]
        return any(re.match(pattern, url) for pattern in tiktok_patterns)

    def _setup_progress_bars(self):
        job_progress = Progress(
            TextColumn('[blue_violet]{task.percentage:.0f}%'),
            BarColumn(),
            DownloadColumn(),
            '•',
            TransferSpeedColumn(),
            '•',
            TimeRemainingColumn(compact=True, elapsed_when_finished=True)
        )
        overall_progress = Progress(
            TextColumn('{task.description}'),
            BarColumn(),
            TextColumn('([blue1]{task.completed}[/] of {task.total} videos downloaded)'),
        )
        return job_progress, overall_progress

    def _create_progress_panel(self, job_progress, overall_progress):
        return Panel(
            Group(job_progress, overall_progress),
            border_style='purple',
            box=HEAVY,
            expand=False
        )

    def _download_video_in_executor(self, video_link, executor, job_progress, overall_progress, overall_task):
        timestamp = datetime.now().strftime('%d%m%y_%I%M%S_%f')
        filename = f'{self.DIRECTORY}/Snaptik.app_{timestamp}.mp4'
        task_id = job_progress.add_task('', start=False)
        executor.submit(
            self._download_single_video,
            job_progress,
            task_id,
            video_link,
            filename,
            overall_progress,
            overall_task
        )

    def extract_multi_link(self, worker, tiktok_urls):
        with ThreadPoolExecutor(max_workers=worker) as executor:
            video_links = list(executor.map(self._extract_single_link, tiktok_urls))
        return video_links

    def url_sanitizer(self, arg_filename=None, args_single_url=None):
        tiktok_url = self._load_urls(arg_filename) if arg_filename else [args_single_url]
        sanitized_urls = [url for url in tiktok_url if self._sanitize_tiktok_url(url)]
        if not sanitized_urls:
            raise InvalidUrl('No valid TikTok URLs found.')
        return sanitized_urls

    def video_downloader(self, worker, video_links):
        os.makedirs(self.DIRECTORY, exist_ok=True)
        job_progress, overall_progress = self._setup_progress_bars()
        overall_task = overall_progress.add_task('[bold yellow]Overall Progress', total=len(video_links))
        with Live(self._create_progress_panel(job_progress, overall_progress), refresh_per_second=10, transient=self.transient):
            with ThreadPoolExecutor(max_workers=worker) as executor:
                for video_link in video_links:
                    self._download_video_in_executor(video_link, executor, job_progress, overall_progress, overall_task)
