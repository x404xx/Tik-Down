<div align="center">

# Tik-Down <img src="https://github.com/x404xx/Tik-Down/assets/114883816/05bb5343-bd6d-494c-ad1d-5eb85bd3fed2" width="35px">

**Tik-Down** is a downloader specifically designed for downloading TikTok videos. It features concurrency and multi-URL downloading capabilities. (https://snaptik.app)

<img src="https://github.com/x404xx/Tik-Down/assets/114883816/b88c972c-4c71-465e-803e-7e47de052452" width="700" height="auto">

</div>

## Git Clone

```
git clone https://github.com/x404xx/Tik-Down.git
```

## Installation

To use _**Tik-Down**_, open your terminal and navigate to the folder that contains _**Tik-Down**_ content ::

```bash
pip install -r requirements.txt
```

## Supported URL

```
[>] https://vt.tiktok.com/ZSN9kJose
[>] https://vm.tiktok.com/ZSNxSA1C4/
[>] https://www.tiktok.com/@anttonraccaus/video/7279062551613246752?is_from_webapp=1&sender_device=pc
```

## Usage

```
usage: main.py [-h] [-su SINGLE_URL] [-fn FILENAME] [-wk WORKER] [-el] [-ts] [-ic]

Download TikTok videos using Snaptik

options:
  -h, --help            show this help message and exit
  -su SINGLE_URL, --single_url SINGLE_URL
                        Single TikTok URL
  -fn FILENAME, --filename FILENAME
                        Text file containing a list of TikTok URLs to download (one URL per line)
  -wk WORKER, --worker WORKER
                        Workers for concurrency (If not set, it will be automatically set based on the length of [url_list])
  -el, --enable_log     For debugging
  -ts, --transient      Close the progress bar after all the downloads/tasks are finished
  -ic, --instant_clear  Close the progress bar immediately after one task is completed
```

-   **Download from MULTIPLE-URL using a text file:**

    > If you have more than **_1000 TikTok URLs_**, it is recommended to set the worker manually by using the command, example `-wk 300` to prevent exceeding memory limits if you have a low-spec device. If you don't set it manually, it will automatically be set to **_1000_** because the worker is configured based on the length of the [url_list].

    ```
    python main.py -fn multi_url.txt
    ```

-   **Download using a SINGLE-URL:**
    ```
    python main.py -su https://vt.tiktok.com/ZSN9kJose
    ```

## Example

```python
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
```

## **Legal Disclaimer**

> This was made for educational purposes only, nobody which directly involved in this project is responsible for any damages caused. **_You are responsible for your actions._**
