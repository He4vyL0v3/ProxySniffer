from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from tqdm import tqdm
import os
import time
from links import proxy_HTTP, proxy_HTTPS, proxy_SOCKS4, proxy_SOCKS5

proxy_mapping = {1: "HTTP", 2: "HTTPS", 3: "SOCKS4", 4: "SOCKS5"}

class ProxyChecker:
    def __init__(self):
        self.working_proxies = []
        self.test_url = "https://www.example.com/"
        self.timeout = 5
        self.max_workers = 50

    def check_proxy(self, proxy, proxy_type):
        proxies = self.build_proxies(proxy, proxy_type)
        try:
            start_time = time.time()
            response = requests.get(self.test_url, proxies=proxies, 
                                  timeout=self.timeout, verify=False)
            response_time = round((time.time() - start_time) * 1000)  # в мс
            if response.status_code == 200:
                return True, response_time
        except Exception:
            pass
        return False, 0

    def check_proxies_multithread(self, proxies_list, proxy_type):
        self.working_proxies = []
        proxy_results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_proxy = {
                executor.submit(self.check_proxy, proxy, proxy_type): proxy
                for proxy in proxies_list
            }

            for future in tqdm(
                as_completed(future_to_proxy),
                total=len(proxies_list),
                desc="\033[34m[*] Checking proxies\033[0m",
                bar_format="\033[92m{l_bar}{bar}{r_bar}\033[0m",
                unit="proxy"
            ):
                proxy = future_to_proxy[future]
                try:
                    result, response_time = future.result()
                    if result:
                        self.working_proxies.append(proxy)
                        proxy_results.append((proxy, response_time))
                except Exception:
                    pass

        return proxy_results

    def build_proxies(self, proxy_address, proxy_type):
        proxy_type = proxy_type.lower()
        if proxy_type in ["http", "https"]:
            return {
                "http": f"{proxy_type}://{proxy_address}",
                "https": f"{proxy_type}://{proxy_address}",
            }
        elif proxy_type == "socks4":
            return {
                "http": f"socks4://{proxy_address}",
                "https": f"socks4://{proxy_address}",
            }
        elif proxy_type == "socks5":
            return {
                "http": f"socks5://{proxy_address}",
                "https": f"socks5://{proxy_address}",
            }
        return {}

    def load_proxies(self, proxy_type):
        proxy_sources = {
            "HTTP": proxy_HTTP,
            "HTTPS": proxy_HTTPS,
            "SOCKS4": proxy_SOCKS4,
            "SOCKS5": proxy_SOCKS5,
        }

        sources = proxy_sources.get(proxy_type, [])
        proxies = []

        for link in tqdm(
            sources,
            desc="\033[34m[*] Downloading proxies\033[0m",
            bar_format="\033[92m{l_bar}{bar}{r_bar}\033[0m",
            unit="source"
        ):
            try:
                response = requests.get(link, timeout=10)
                if response.status_code == 200:
                    proxies.extend(response.text.strip().splitlines())
            except Exception:
                continue

        return list(set(proxies))

def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\033[1;35m")
    print("")
    print("")
    print("  ▄▄▄·▄▄▄        ▐▄• ▄  ▄· ▄▌.▄▄ ·  ▐ ▄ ▪  ·▄▄▄·▄▄▄▄▄▄ .▄▄▄  ")
    print(" ▐█ ▄█▀▄ █·▪      █▌█▌▪▐█▪██▌▐█ ▀. •█▌▐███ ▐▄▄·▐▄▄·▀▄.▀·▀▄ █·")
    print("  ██▀·▐▀▀▄  ▄█▀▄  ·██· ▐█▌▐█▪▄▀▀▀█▄▐█▐▐▌▐█·██▪ ██▪ ▐▀▀▪▄▐▀▀▄ ")
    print(" ▐█▪·•▐█•█▌▐█▌.▐▌▪▐█·█▌ ▐█▀·.▐█▄▪▐███▐█▌▐█▌██▌.██▌.▐█▄▄▌▐█•█▌")
    print(" .▀   .▀  ▀ ▀█▄▀▪•▀▀ ▀▀  ▀ •  ▀▀▀▀ ▀▀ █▪▀▀▀▀▀▀ ▀▀▀  ▀▀▀ .▀  ▀")
    print("")
    print("" + "=" * 65)
    print("           PROXY CHECKER TOOL - By Nighty3098")
    print("=" * 65 + "\033[0m")

def main_menu():
    print("\n\033[1;33m[1] HTTP Proxy")
    print("[2] HTTPS Proxy")
    print("[3] SOCKS4 Proxy")
    print("[4] SOCKS5 Proxy\033[0m")
    print("\033[1;31m[0] Exit\033[0m")
    
    try:
        choice = int(input("\n\033[1;35m[SELECT OPTION] > \033[0m"))
        return choice
    except ValueError:
        return -1

def main():
    requests.packages.urllib3.disable_warnings()
    
    checker = ProxyChecker()
    
    while True:
        print_banner()
        choice = main_menu()
        
        if choice == 0:
            print("\n\033[1;31m[!] Exiting...\033[0m")
            break
        elif choice not in [1, 2, 3, 4]:
            print("\n\033[1;31m[!] Invalid option!\033[0m")
            time.sleep(1)
            continue
        
        proxy_type = proxy_mapping[choice]
        
        try:
            print_banner()
            list_limit = int(input("\n\033[1;35m[PROXY LIMIT] > \033[0m"))
        except ValueError:
            print("\n\033[1;31m[!] Invalid number!\033[0m")
            time.sleep(1)
            continue
        
        print_banner()
        print(f"\n\033[1;34m[*] Loading {proxy_type} proxies...\033[0m")
        proxies = checker.load_proxies(proxy_type)
        
        if not proxies:
            print("\n\033[1;31m[!] No proxies loaded from sources!\033[0m")
            time.sleep(2)
            continue
        
        proxies = proxies[:list_limit]
        print(f"\033[1;32m[+] Loaded {len(proxies)} proxies\033[0m")
        
        print(f"\033[1;34m[*] Checking {proxy_type} proxies...\033[0m")
        results = checker.check_proxies_multithread(proxies, proxy_type)
        
        print(f"\n\033[1;32m[+] Found {len(results)} working proxies\033[0m")
        
        print("\n\033[1;36m[1] Save to file")
        print("[2] Show in console")
        print("[3] Back to main menu\033[0m")
        
        try:
            output_choice = int(input("\n\033[1;35m[OUTPUT OPTION] > \033[0m"))
        except ValueError:
            output_choice = 3
        
        if output_choice == 1:
            filename = f"working_{proxy_type.lower()}_proxies.txt"
            with open(filename, 'w') as f:
                for proxy, response_time in results:
                    f.write(f"{proxy} | {response_time}ms\n")
            print(f"\n\033[1;32m[+] Results saved to {filename}\033[0m")
            time.sleep(2)
        elif output_choice == 2:
            print("\n\033[1;36m" + "=" * 40)
            print("WORKING PROXIES (IP:PORT | RESPONSE TIME)")
            print("=" * 40 + "\033[0m")
            for proxy, response_time in results:
                print(f"\033[1;32m{proxy} | {response_time}ms\033[0m")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
