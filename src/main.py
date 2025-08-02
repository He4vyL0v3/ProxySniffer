import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import customtkinter as ctk
import requests

from links import proxy_HTTP, proxy_HTTPS, proxy_SOCKS4, proxy_SOCKS5

ctk.set_default_color_theme("green")

proxy_mapping = {
    "HTTP": proxy_HTTP,
    "HTTPS": proxy_HTTPS,
    "SOCKS4": proxy_SOCKS4,
    "SOCKS5": proxy_SOCKS5,
}


class ProxyCheckerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Proxy Checker")
        self.geometry("500x600")

        self.working_proxies = []
        self.running = False

        self.setup_ui()

    def setup_ui(self):
        self.header = ctk.CTkLabel(
            self, text="PROXY CHECKER", font=("Arial", 30, "bold")
        )
        self.header.pack(pady=(20, 10))

        ctk.CTkLabel(
            self,
            text="Proxy Type:",
            font=("Arial", 13),
        ).pack(anchor="w", padx=20, pady=5)

        self.proxy_type = ctk.CTkComboBox(
            self, values=["HTTP", "HTTPS", "SOCKS4", "SOCKS5"], state="readonly"
        )
        self.proxy_type.set("HTTP")
        self.proxy_type.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            self,
            text="Proxy Limit:",
            font=("Arial", 13),
        ).pack(anchor="w", padx=20, pady=5)

        self.limit_entry = ctk.CTkEntry(self, placeholder_text="Enter limit")
        self.limit_entry.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            self,
            text="Download Progress:",
            font=("Arial", 13),
        ).pack(
            anchor="w",
            padx=20,
            pady=(5, 0),
        )
        self.download_progress = ctk.CTkProgressBar(self)
        self.download_progress.pack(fill="x", padx=20, pady=5)
        self.download_progress.set(0)

        ctk.CTkLabel(
            self,
            text="Check Progress:",
            font=("Arial", 13),
        ).pack(anchor="w", padx=20, pady=(5, 0))
        self.check_progress = ctk.CTkProgressBar(self)
        self.check_progress.pack(fill="x", padx=20, pady=5)
        self.check_progress.set(0)

        self.status_label = ctk.CTkLabel(
            self,
            text="Ready to start",
        )
        self.status_label.pack(pady=5)

        self.start_btn = ctk.CTkButton(
            self,
            text="Start Checking",
            command=self.start_process,
        )
        self.start_btn.pack(pady=10, padx=20, fill="x")

        self.save_btn = ctk.CTkButton(
            self,
            text="Save Results",
            state="disabled",
            command=self.save_results,
        )
        self.save_btn.pack(pady=(0, 10), padx=20, fill="x")

        self.results = ctk.CTkTextbox(self, wrap="none")
        self.results.pack(pady=(0, 20), padx=20, fill="both", expand=True)
        self.results.insert("1.0", "Working proxies will appear here...")
        self.results.configure(state="disabled")

    def start_process(self):
        if self.running:
            return

        try:
            limit = int(self.limit_entry.get())
            if limit <= 0:
                self.update_status("Invalid limit value", "red")
                return
        except:
            self.update_status("Invalid limit value", "red")
            return

        proxy_type = self.proxy_type.get()
        self.running = True
        self.start_btn.configure(state="disabled")
        self.save_btn.configure(state="disabled")
        self.results.configure(state="normal")
        self.results.delete("1.0", "end")
        self.results.configure(state="disabled")
        self.update_status("Starting process...", "white")

        threading.Thread(
            target=self.run_checking_process, args=(proxy_type, limit), daemon=True
        ).start()

    def run_checking_process(self, proxy_type, limit):
        self.update_status(f"Downloading {proxy_type} proxies...", "cyan")
        proxies = self.load_proxy(proxy_type)

        if not proxies:
            self.update_status("No proxies found", "red")
            self.running = False
            self.start_btn.configure(state="normal")
            return

        limited_proxies = proxies[:limit]

        self.update_status(f"Checking {len(limited_proxies)} proxies...", "cyan")
        self.working_proxies = self.check_proxies_multithread(
            limited_proxies, proxy_type
        )

        self.update_status(
            f"Found {len(self.working_proxies)} working proxies", "green"
        )
        self.results.configure(state="normal")
        self.results.delete("1.0", "end")

        if self.working_proxies:
            for proxy in self.working_proxies:
                self.results.insert("end", proxy + "\n")
        else:
            self.results.insert("end", "No working proxies found")

        self.results.configure(state="disabled")
        self.save_btn.configure(state="normal")
        self.start_btn.configure(state="normal")
        self.running = False

    def load_proxy(self, proxy_type):
        sources = proxy_mapping.get(proxy_type, [])
        if not sources:
            return []

        proxies = []
        total = len(sources)

        for i, link in enumerate(sources):
            try:
                response = requests.get(url=link, timeout=10)
                if response.status_code == 200:
                    proxies.extend(response.text.strip().splitlines())
            except Exception as e:
                pass

            progress = (i + 1) / total
            self.download_progress.set(progress)
            self.update()

        return proxies

    def check_proxies_multithread(self, proxies_list, proxy_type, max_workers=40):
        working_proxies = []
        total = len(proxies_list)
        processed = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {
                executor.submit(self.check_proxy, proxy, proxy_type): proxy
                for proxy in proxies_list
            }

            for future in as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    if future.result():
                        working_proxies.append(proxy)
                except:
                    pass

                processed += 1
                progress = processed / total
                self.check_progress.set(progress)
                self.update()

        return working_proxies

    def check_proxy(
        self, proxy, proxy_type, test_url="https://www.example.com/", timeout=1
    ):
        proxies = self.build_proxies(proxy, proxy_type)
        try:
            response = requests.get(test_url, proxies=proxies, timeout=timeout)
            return response.status_code == 200
        except:
            return False

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
        else:
            raise ValueError("Unsupported proxy type")

    def save_results(self):
        if not self.working_proxies:
            return

        with open("proxies.txt", "w") as file:
            for proxy in self.working_proxies:
                file.write(f"{proxy}\n")

        self.update_status("Results saved to proxies.txt", "green")

    def update_status(self, message, color="white"):
        colors = {"red": "red", "green": "green", "cyan": "blue", "white": "white"}
        self.status_label.configure(
            text=message, text_color=colors.get(color, "#ffffff")
        )
        self.update()


if __name__ == "__main__":
    app = ProxyCheckerApp()
    app.mainloop()
