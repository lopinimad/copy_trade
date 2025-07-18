import re
import json
import sys
import asyncio
from pathlib import Path
from pyquotex.http.navigator import Browser
from datetime import datetime


class Login(Browser):
    """Class for Quotex login resource."""

    url = ""
    cookies = None
    ssid = None
    base_url = 'qxbroker.com'
    https_base_url = f'https://{base_url}'
    Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]Quotex: ")

    def __init__(self, api, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = api
        self.html = None
        self.headers = self.get_headers()
        self.full_url = f"{self.https_base_url}/{api.lang}"

    def get_token(self):
        self.headers["Connection"] = "keep-alive"
        self.headers["Accept-Encoding"] = "gzip, deflate, br, zstd"
        self.headers["Accept-Language"] = "en-US,en;q=0.8"
        self.headers["Accept"] = (
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
        )
        self.headers["Referer"] = f"{self.full_url}/sign-in"
        self.headers["Upgrade-Insecure-Requests"] = "1"
        self.headers["Sec-Ch-Ua"] = '"Not)A;Brand";v="8", "Chromium";v="138", "Brave";v="138"'
        self.headers["Sec-Ch-Ua-Mobile"] = "?0"
        self.headers["Sec-Ch-Ua-Platform"] = '"Linux"'
        self.headers["Sec-Fetch-Site"] = "same-origin"
        self.headers["Sec-Fetch-User"] = "?1"
        self.headers["Sec-Fetch-Dest"] = "document"
        self.headers["Sec-Fetch-Mode"] = "navigate"
        self.headers["sec-gpc"] = "1"
        #self.headers["Dnt"] = "1"
        self.send_request(
            "GET",
            f"{self.full_url}/sign-in/modal/"
        )
        html = self.get_soup()
        match = html.find(
            "input", {"name": "_token"}
        )
        token = None if not match else match.get("value")
        return token

    async def awaiting_pin(self, data, input_message):
        Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]Quotex: ")
        self.headers["Content-Type"] = "application/x-www-form-urlencoded"
        self.headers["Referer"] = f"{self.full_url}/sign-in/modal"
        data["keep_code"] = 1
        try:
            code = input(input_message)
            if not code.isdigit():
                print(str(Timen) + " Please enter a valid code.")
                await self.awaiting_pin(data, input_message)
            data["code"] = code
        except KeyboardInterrupt:
            print(str(Timen) + " Closing program.")
            sys.exit()

        await asyncio.sleep(1)
        self.send_request(
            method="POST",
            url=f"{self.full_url}/sign-in/modal",
            data=data
        )

    def get_profile(self):
        self.response = self.send_request(
            method="GET",
            url=f"{self.full_url}/trade"
        )
        if self.response:
            script = self.get_soup().find_all(
                "script",
                {"type": "text/javascript"}
            )
            script = script[0].get_text() if script else "{}"
            match = re.sub(
                "window.settings = ",
                "",
                script.strip().replace(";", "")
            )
            self.cookies = self.get_cookies()
            self.ssid = json.loads(match).get("token")
            self.api.session_data["cookies"] = self.cookies
            self.api.session_data["token"] = self.ssid
            self.api.session_data["user_agent"] = self.headers["User-Agent"]
            output_file = Path(f"{self.api.resource_path}/settings/session.json")
            output_file.parent.mkdir(exist_ok=True, parents=True)
            output_file.write_text(
                json.dumps({
                    "cookies": self.cookies,
                    "token": self.ssid,
                    "user_agent": self.headers["User-Agent"]
                }, indent=4)
            )
            return self.response, json.loads(match)

        return None, None

    def _get(self):
        return self.send_request(
            method="GET",
            url=f"f{self.full_url}/trade"
        )

    async def _post(self, data):
        """Send get request for Quotex API login http resource.
        :returns: The instance of :class:`requests.Response`.
        """
        Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]Quotex: ")
        self.response = self.send_request(
            method="POST",
            url=f"{self.full_url}/sign-in/",
            data=data
        )
        required_keep_code = self.get_soup().find(
            "input", {"name": "keep_code"}
        )
        if required_keep_code:
            auth_body = self.get_soup().find(
                "main", {"class": "auth__body"}
            )
            input_message = (
                f'{auth_body.find("p").text}: ' if auth_body.find("p")
                else str(Timen) + " Enter Code PIN "
                     "Sended to your e-mail: "
            )
            await self.awaiting_pin(data, input_message)
        await asyncio.sleep(1)
        success = self.success_login()
        return success

    def success_login(self):
        Timen = datetime.now().strftime("%Y-%m-%d %H:%M:%S [Client]Quotex: ")
        if "trade" in self.response.url:
            return True, str(Timen) + " Login successful."
        html = self.get_soup()
        match = html.find(
            "div", {"class": "hint--danger"}
        ) or html.find(
            "div", {"class": "input-control-cabinet__hint"}
        )
        message_in_match = match.text.strip() if match else ""
        return False, str(Timen) + f" Login failed. {message_in_match}"

    async def __call__(self, username, password, user_data_dir=None):
        """Method to get Quotex API login http request.
        :param str username: The username of a Quotex server.
        :param str password: The password of a Quotex server.
        :param str user_data_dir: The optional value for path userdata.
        :returns: The instance of :class:`requests.Response`.
        """
        data = {
            "_token": self.get_token(),
            "email": username,
            "password": password,
            "remember": 1,

        }
        status, msg = await self._post(data)
        if not status:
            print(msg)
            exit(0)

        self.get_profile()

        return status, msg
