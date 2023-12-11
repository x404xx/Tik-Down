import argparse
import os

from api import SnaptikDownloader


def parse_arguments():
    parser = argparse.ArgumentParser(description='Download TikTok videos using Snaptik')
    parser.add_argument(
        '-su',
        '--single_url',
        type=str,
        help='Single TikTok url'
    )
    parser.add_argument(
        '-fn',
        '--filename',
        type=str,
        help='Text file containing a list of TikTok urls to download (one URL per line)'
    )
    parser.add_argument(
        '-wk',
        '--worker',
        type=int,
        help='Workers for concurrency (If not set, it will be automatically set based on the length of [url_list])'
    )
    parser.add_argument(
        '-el',
        '--enable_log',
        action='store_true',
        help='For debugging'
    )
    parser.add_argument(
        '-ts',
        '--transient',
        action='store_true',
        help='Close the progress bar after all the downloads/tasks are finished'
    )
    parser.add_argument(
        '-ic',
        '--instant_clear',
        action='store_true',
        help='Close the progress bar immediately after one task is completed'
    )
    return parser.parse_args()


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    args = parse_arguments()
    if not args.single_url and not args.filename:
        os.system('python main.py -h' if os.name == 'nt' else 'python3 main.py -h')
        return

    snaptik_instance = SnaptikDownloader(args.transient, args.instant_clear, args.enable_log)
    sanitized_urls = snaptik_instance.url_sanitizer(args.filename, args.single_url)
    worker = args.worker or len(sanitized_urls)
    video_links = snaptik_instance.extract_multi_link(worker, sanitized_urls)
    snaptik_instance.video_downloader(worker, video_links)


if __name__ == '__main__':
    main()