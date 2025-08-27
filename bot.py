from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout,
    BasicAuth,
    FormData
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import to_hex
from datetime import datetime, timezone
from colorama import *
import asyncio, random, base64, uuid, json, re, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class PerspectiveAI:
    def __init__(self) -> None:
        self.PRIVY_API = "https://auth.privy.io/api/v1"
        self.BASE_API = "https://core-api.perspectiveai.xyz/api"
        self.PRIVY_HEADERS = {}
        self.BASE_HEADERS = {}
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.auth_tokens = {}
        self.access_tokens = {}
        self.min_delay = 0
        self.max_delay = 0

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Perspective AI {Fore.BLUE + Style.BRIGHT}Auto Ref BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
        
    def save_ref_wallets(self, private_key: str):
        filename = "ref_wallets.txt"
        try:
            with open(filename, "a") as f:
                f.write(f"{private_key}\n")
                self.log(f"{Fore.GREEN + Style.BRIGHT}Account Successfully Saved in {filename}{Style.RESET_ALL}")
        except Exception as e:
            return None
    
    async def load_proxies(self):
        filename = "proxy.txt"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                return
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def build_proxy_config(self, proxy=None):
        if not proxy:
            return None, None, None

        if proxy.startswith("socks"):
            connector = ProxyConnector.from_url(proxy)
            return connector, None, None

        elif proxy.startswith("http"):
            match = re.match(r"http://(.*?):(.*?)@(.*)", proxy)
            if match:
                username, password, host_port = match.groups()
                clean_url = f"http://{host_port}"
                auth = BasicAuth(username, password)
                return None, clean_url, auth
            else:
                return None, proxy, None

        raise Exception("Unsupported Proxy Type.")
    
    def decode_ref_code(self, ref_code: str):
        try:
            uuid_str = base64.b64decode(ref_code).decode("utf-8")
            return str(uuid.UUID(uuid_str))
        except Exception as e:
            raise Exception(f"Decode Ref Code Failed: {str(e)}")
        
    def generate_account(self):
        try:
            private_key = os.urandom(32).hex()
            account = Account.from_key(private_key)
            address = account.address
            
            return private_key, address
        except Exception as e:
            return None, None
    
    def generate_payload(self, private_key: str, address: str, nonce: str):
        try:
            timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            message = f"app.perspectiveai.xyz wants you to sign in with your Ethereum account:\n{address}\n\nBy signing, you are proving you own this wallet and logging in. This does not initiate a transaction or cost any fees.\n\nURI: https://app.perspectiveai.xyz\nVersion: 1\nChain ID: 2368\nNonce: {nonce}\nIssued At: {timestamp}\nResources:\n- https://privy.io"
            encoded_message = encode_defunct(text=message)
            signed_message = Account.sign_message(encoded_message, private_key=private_key)
            signature = to_hex(signed_message.signature)

            payload = {
                "message":message,
                "signature":signature,
                "chainId":"eip155:2368",
                "walletClientType":"metamask",
                "connectorType":"injected",
                "mode":"login-or-sign-up"
            }

            return payload
        except Exception as e:
            raise Exception(f"Generate Req Payload Failed: {str(e)}")
        
    async def print_timer(self):
        for remaining in range(random.randint(self.min_delay, self.max_delay), 0, -1):
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {remaining} {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Seconds For Next Accounts...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(1)

    def print_question(self):
        while True:
            try:
                accounts = int(input(f"{Fore.YELLOW + Style.BRIGHT}How Many Ref -> {Style.RESET_ALL}").strip())
                if accounts >= 0:
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Ref must be > 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                min_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Min Delay Each Process -> {Style.RESET_ALL}").strip())
                if min_delay >= 0:
                    self.min_delay = min_delay
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Min Delay must be >= 0.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                max_delay = int(input(f"{Fore.YELLOW + Style.BRIGHT}Max Delay Each Process -> {Style.RESET_ALL}").strip())
                if max_delay >= min_delay:
                    self.max_delay = max_delay
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Min Delay must be >= Min Delay.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run Without Proxy{Style.RESET_ALL}")
                proxy_choice = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2] -> {Style.RESET_ALL}").strip())

                if proxy_choice in [1, 2]:
                    proxy_type = (
                        "With" if proxy_choice == 1 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")

        rotate_proxy = False
        if proxy_choice == 1:
            while True:
                rotate_proxy = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate_proxy in ["y", "n"]:
                    rotate_proxy = rotate_proxy == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return accounts, proxy_choice, rotate_proxy
    
    async def check_connection(self, proxy_url=None):
        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.get(url="https://api.ipify.org?format=json", proxy=proxy, proxy_auth=proxy_auth) as response:
                    response.raise_for_status()
                    return True
        except (Exception, ClientResponseError) as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Connection Not 200 OK {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
        
        return None
    
    async def siwe_init(self, address: str, proxy_url=None, retries=5):
        url = f"{self.PRIVY_API}/siwe/init"
        data = json.dumps({"address":address})
        headers = {
            **self.PRIVY_HEADERS[address],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
        }
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Fetch Nonce Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def siwe_authenticate(self, private_key: str, address: str, nonce: str, proxy_url=None, retries=5):
        url = f"{self.PRIVY_API}/siwe/authenticate"
        data = json.dumps(self.generate_payload(private_key, address, nonce))
        headers = {
            **self.PRIVY_HEADERS[address],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
        }
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Authenticate Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def auth_login(self, address: str, auth_token: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/auth/login"
        data = FormData()
        data.add_field("token", auth_token)
        data.add_field("referred_by_user_id", self.REF_CODE)
        data.add_field("marketing_opt_in", "1")
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=self.BASE_HEADERS[address], data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Login Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def users_me(self, address: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/users/me"
        headers = {
            **self.BASE_HEADERS[address],
            "Authorization": f"Bearer {self.access_tokens[address]}"
        }
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   Status     : {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Fetch Profile Data Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def process_check_connection(self, address: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(proxy)
            if not is_valid:
                if rotate_proxy:
                    proxy = self.rotate_proxy_for_account(address)
                    await asyncio.sleep(1)
                    continue

                return False

            return True
    
    async def process_auth_login(self, private_key: str, address: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
        if is_valid:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None

            init = await self.siwe_init(address, proxy)
            if not init: return False

            nonce = init["nonce"]

            authenticate = await self.siwe_authenticate(private_key, address, nonce, proxy)
            if not authenticate: return False

            auth_token = authenticate["token"]
            
            login = await self.auth_login(address, auth_token, proxy)
            if not login: return False

            access_token = login["token"]
            self.access_tokens[address] = access_token

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Login Success {Style.RESET_ALL}"
            )

            return True
        
    async def process_accounts(self, private_key: str, address: str, use_proxy: bool, rotate_proxy: bool):
        is_logined = await self.process_auth_login(private_key, address, use_proxy, rotate_proxy)
        if not is_logined: return False

        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        self.log(f"{Fore.CYAN+Style.BRIGHT}Profile   :{Style.RESET_ALL}")

        profile = await self.users_me(address, proxy)
        if profile:
            user_id = profile.get("data", {}).get("id", None)
            email = profile.get("data", {}).get("email", None)
            wallet_address = profile.get("data", {}).get("wallet_address", None)
            balance = profile.get("data", {}).get("balance", 0)
            paid_reward = profile.get("data", {}).get("paid_reward", 0)
            subs_status = profile.get("data", {}).get("subscription_status", None)
            subs_type = profile.get("data", {}).get("subscription_type", None)
            trial_starts = profile.get("data", {}).get("trial_starts_at", None)
            trial_ends = profile.get("data", {}).get("trial_ends_at", None)
            referrals_count = profile.get("data", {}).get("referrals_count", 0)

            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   User Id    : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{user_id}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Email      : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{email}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Address    : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{wallet_address}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Balance    : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{balance}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Paid Reward: {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{paid_reward}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Subs Status: {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{subs_status}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Subs Type  : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{subs_type}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Trial Start: {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{trial_starts}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Trial End  : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{trial_ends}{Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.BLUE+Style.BRIGHT}   Ref Counts : {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{referrals_count}{Style.RESET_ALL}"
            )

        self.save_ref_wallets(private_key)
        return True

    async def main(self):
        try:
            accounts, proxy_choice, rotate_proxy = self.print_question()

            with open('ref_code.txt', 'r') as file:
                ref_code = file.read().strip()

            self.REF_CODE = self.decode_ref_code(ref_code)

            use_proxy = True if proxy_choice == 1 else False

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Referral Code: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{ref_code}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies()

            success = 0
            failed = 0

            separator = "=" * 25
            for i in range(accounts):
                private_key, address = self.generate_account()
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {i+1} {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}Of{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {accounts} {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                )

                if not private_key or not address:
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}Status    :{Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT} Library Version Not Supported {Style.RESET_ALL}"
                    )
                    continue

                user_agent = FakeUserAgent().random

                self.PRIVY_HEADERS[address] = {
                    "Accept": "application/json",
                    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Origin": "https://app.perspectiveai.xyz",
                    "Referer": "https://app.perspectiveai.xyz/",
                    "Privy-App-Id": "cmc373uuc01e9jp0m4px3rjcc",
                    "Privy-Ca-Id": str(uuid.uuid4()),
                    "Privy-Client": "react-auth:2.16.0",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "cross-site",
                    "User-Agent": user_agent
                }

                self.BASE_HEADERS[address] = {
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Origin": "https://app.perspectiveai.xyz",
                    "Referer": "https://app.perspectiveai.xyz/",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-site",
                    "User-Agent": user_agent
                }
                
                is_processed = await self.process_accounts(private_key, address, use_proxy, rotate_proxy)
                if is_processed: success += 1
                else: failed += 1 

                self.log(f"{Fore.CYAN+Style.BRIGHT}Info      :{Style.RESET_ALL}")
                self.log(
                    f"{Fore.GREEN+Style.BRIGHT}   Ref Success: {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{success}{Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.RED+Style.BRIGHT}   Ref Failed : {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{failed}{Style.RESET_ALL}"
                )

                await self.print_timer()

            self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*72)

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'ref_code.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = PerspectiveAI()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Perspective AI - BOT{Style.RESET_ALL}                                       "                              
        )