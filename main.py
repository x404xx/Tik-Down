import os

from api import Colors, SnaptikDownloader

if __name__ == '__main__':
    """
    Supported TikTok URL;
     [>] https://vt.tiktok.com/ZSN9kJose
     [>] https://vm.tiktok.com/ZSNxSA1C4/
     [>] https://www.tiktok.com/@anttonraccaus/video/7279062551613246752?is_from_webapp=1&sender_device=pc
    """

    os.system('cls' if os.name == 'nt' else 'clear')

    logging_enabled = False
    tiktok_url = input(f'{Colors.GREEN}Tiktok target URL{Colors.END}: ')
    SnaptikDownloader(tiktok_url, logging_enabled).start_download()