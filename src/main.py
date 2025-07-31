import requests
from links import proxy_HTTP, proxy_HTTPS, proxy_SOCKS4, proxy_SOCKS5
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

proxy_mapping = {
    1: "HTTP",
    2: "HTTPS",
    3: "SOCKS4",
    4: "SOCKS5"
}

def check_proxy(proxy, proxy_type, test_url="https://google.com/", timeout=1):
    """
    Checks the proxy's performance.

        :param proxy: string with IP:PORT, for example "190.13.147.93:5678"
    :param proxy_type: string 'HTTP', 'HTTPS', 'SOCKS4' or 'SOCKS5'
    :param test_url: URL for checking availability (default google.com )
    :param timeout: timeout in seconds for the request
    :return: True if the proxy is working, otherwise False
    """
    proxies = build_proxies(proxy, proxy_type)
    try:
        response = requests.get(test_url, proxies=proxies, timeout=timeout)
        return response.status_code == 200
    except Exception as e:
        return False
    
def check_proxies_multithread(proxies_list, proxy_type, max_workers=40):
    """
    Checks the proxy list multithreadedly.

        :param proxies_list: list of proxy strings with 'ip:port'
        :param proxy_type: proxy type ('HTTP', 'HTTPS', 'SOCKS4', 'SOCKS5')
    :param max_workers: maximum number of threads
    :return: list of working proxies
    """
    working_proxies = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_proxy = {executor.submit(check_proxy, proxy, proxy_type): proxy for proxy in proxies_list}

        for future in tqdm(as_completed(future_to_proxy), total=len(proxies_list), desc="Checking proxies", bar_format='\033[92m{l_bar}{bar}{r_bar}\033[0m'):
            proxy = future_to_proxy[future]
            try:
                if future.result():
                    working_proxies.append(proxy)
            except Exception as e:
                # Можно логировать ошибки, если нужно
                pass

    return working_proxies

def load_proxy(proxy_type):
    proxy_sources = {
        "HTTP": proxy_HTTP,
        "HTTPS": proxy_HTTPS,
        "SOCKS4": proxy_SOCKS4,
        "SOCKS5": proxy_SOCKS5,
    }

    sources = proxy_sources.get(proxy_type)
    if sources is None:
        print(f"Unknown proxy type: {proxy_type}")
        return
    
    proxies = []

    for link in tqdm(sources, desc="Downloading proxies list", bar_format='\033[92m{l_bar}{bar}{r_bar}\033[0m'):
        try:
            response = requests.get(url=link)
            if response.status_code == 200:
                proxies.extend(response.text.strip().splitlines())
        except requests.RequestException as e:
            print(f"Failed to fetch {link}: {e}")
    
    return proxies

def build_proxies(proxy_address, proxy_type):
    """
    Generates a proxies dictionary for requests by proxy type and address.

        proxy_address: str, for example '190.13.147.93:5678'
        proxy_type: str, one of ['HTTP', 'HTTPS', 'SOCKS4', 'SOCKS5']

        Returns a dict to be passed to requests, for example:
        {
        'http': 'http://190.13.147.93:5678',
        'https': 'http://190.13.147.93:5678'
        }
    """
    proxy_type = proxy_type.lower()

    if proxy_type in ['http', 'https']:
        proxies = {
            'http': f'{proxy_type}://{proxy_address}',
            'https': f'{proxy_type}://{proxy_address}',
        }
    elif proxy_type == 'socks4':
        proxies = {
            'http': f'socks4://{proxy_address}',
            'https': f'socks4://{proxy_address}',
        }
    elif proxy_type == 'socks5':
        proxies = {
            'http': f'socks5://{proxy_address}',
            'https': f'socks5://{proxy_address}',
        }
    else:
        raise ValueError("Unsupported proxy type. Use HTTP, HTTPS, SOCKS4 or SOCKS5")

    return proxies

def main():
    print("")
    print("")
    print("\033[1m\033[0;35m  ▄▄▄·▄▄▄        ▐▄• ▄  ▄· ▄▌.▄▄ ·  ▐ ▄ ▪  ·▄▄▄·▄▄▄▄▄▄ .▄▄▄  ")
    print("\033[0;35m ▐█ ▄█▀▄ █·▪      █▌█▌▪▐█▪██▌▐█ ▀. •█▌▐███ ▐▄▄·▐▄▄·▀▄.▀·▀▄ █·")
    print("\033[0;35m  ██▀·▐▀▀▄  ▄█▀▄  ·██· ▐█▌▐█▪▄▀▀▀█▄▐█▐▐▌▐█·██▪ ██▪ ▐▀▀▪▄▐▀▀▄ ")
    print("\033[0;35m ▐█▪·•▐█•█▌▐█▌.▐▌▪▐█·█▌ ▐█▀·.▐█▄▪▐███▐█▌▐█▌██▌.██▌.▐█▄▄▌▐█•█▌")
    print("\033[0;35m .▀   .▀  ▀ ▀█▄▀▪•▀▀ ▀▀  ▀ •  ▀▀▀▀ ▀▀ █▪▀▀▀▀▀▀ ▀▀▀  ▀▀▀ .▀  ▀")
    print("\033[0;35m                   Created by Nighty3098                     ")
    print("\033[1m")
    print(" 1 - HTTP ")
    print(" 2 - HTTPS")
    print(" 3 - SOCKS4")
    print(" 4 - SOCKS5")

    user_select = int(input("\033[0;35m[ SELECT A CATEGORY ] $ \033[0m"))
    list_limit = int(input("\033[0;35m[ ENTER LIMIT ] $  \033[0m"))
    
    print("")
    print("")
    
    proxy_type = proxy_mapping.get(user_select, "Unknown")
    proxies = load_proxy(proxy_type)

    limited_proxies = proxies[:list_limit]

    working_proxies = check_proxies_multithread(proxies_list=limited_proxies, proxy_type=proxy_type)

    print("")
    print(" 1 - Save to file")
    print(" 2 - Print to console")
    user_option = int(input("\033[0;35m[ SELECT AN OPTION ] $ \033[0m"))

    if user_option == 2:
        for ip in working_proxies:
            print(ip)

    if user_option == 1:
        text = ""

        for ip in working_proxies:
            text += f"{ip}\n"
            with open("proxies.txt", 'w') as file:
                file.write(text)
                file.close()

if __name__ == "__main__":
    main()
