from os import environ
from time import time
from typing import Optional
from platform import system
from logging import DEBUG, Formatter, StreamHandler, getLogger
from asyncio import sleep
from re import match
from bs4 import BeautifulSoup

from inscriptis import get_text

import zendriver

from .internal.objects import Response, SearchResult
from .internal.selectors import DeepSeekSelectors as DSS
from .internal.exceptions import MissingCredentials, InvalidCredentials, ServerDown

class DeepSeek:
    def __init__(
        self,
        token: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        chat_id: Optional[str] = None,
        headless: bool = True,
        verbose: bool = False,
        chrome_args: list = [],
        attempt_cf_bypass: bool = True
    ) -> None:
        """Initializes the DeepSeek object.

        Args
        ---------
        token: Optional[str]
            The token of the user.
        email: Optional[str]
            The email of the user.
        password: Optional[str]
            The password of the user.
        chat_id: str
            The chat id.
        headless: bool
            Whether to run the browser in headless mode.
        verbose: bool
            Whether to log the actions.
        chrome_args: list
            The arguments to pass to the Chrome browser.
        attempt_cf_bypass: bool
            Whether to attempt to bypass the Cloudflare protection.

        Raises
        ---------
        ValueError:
            Either the token or the email and password must be provided.
        """
        if not token and not (email and password):
            raise MissingCredentials("Either the token alone or the email and password both must be provided")

        self._email = email
        self._password = password
        self._token = token
        self._chat_id = chat_id
        self._headless = headless
        self._verbose = verbose
        self._chrome_args = chrome_args
        self._attempt_cf_bypass = attempt_cf_bypass

        self._deepthink_enabled = False
        self._search_enabled = False

    async def initialize(self) -> None:
        """Initializes the DeepSeek session.

        This method sets up the logger, starts a virtual display if necessary, and launches the browser.
        It also navigates to the DeepSeek chat page and handles the login process using either a token
        or email and password.

        Raises
        ---------
        ValueError:
            PyVirtualDisplay is not installed.
        ValueError:
            Xvfb is not installed.
        """

        # Initilize the logger
        self.logger = getLogger("DeeperSeek")
        self.logger.setLevel(DEBUG)

        if self._verbose:
            handler = StreamHandler()
            handler.setFormatter(Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%H:%M:%S"))
            self.logger.addHandler(handler)

        # Start the virtual display if the system is Linux and the DISPLAY environment variable is not set
        if system() == "Linux" and "DISPLAY" not in environ:
            self.logger.debug("Starting virtual display...")
            try:
                from pyvirtualdisplay.display import Display

                self.display = Display()
                self.display.start()
            except ModuleNotFoundError:
                raise ValueError(
                    "Please install PyVirtualDisplay to start a virtual display by running `pip install PyVirtualDisplay`"
                )
            except FileNotFoundError as e:
                if "No such file or directory: 'Xvfb'" in str(e):
                    raise ValueError(
                        "Please install Xvfb to start a virtual display by running `sudo apt install xvfb`"
                    )
                raise e

        # Start the browser
        self.browser = await zendriver.start(
            chrome_args = self._chrome_args,
            headless = self._headless
        )

        self.logger.debug("Navigating to the chat page...")
        await self.browser.get("https://chat.deepseek.com/" if not self._chat_id \
            else f"https://chat.deepseek.com/a/chat/s/{self._chat_id}")

        if self._attempt_cf_bypass:
            try:
                self.logger.debug("Verifying the Cloudflare protection...")
                await self.browser.main_tab.verify_cf()
            except: # It times out if there was no need to verify
                pass
        
        if self._token:
            await self._login()
        else:
            await self._login_classic()
        
    async def _login(self) -> None:
        """Logs in to DeepSeek using a token.

        This method sets the token in the browser's local storage and reloads the page to authenticate.
        If the token is invalid, it falls back to the classic login method. (email and password)
        """

        self.logger.debug("Logging in using the token...")
        await self.browser.main_tab.evaluate(
            f"localStorage.setItem('userToken', JSON.stringify({{value: '{self._token}', __version: '0'}}))",
            await_promise = True,
            return_by_value = True
        )
        await self.browser.main_tab.reload()
        
        # Reloading with an invalid token still gives access to the website somehow, but only for a split second
        # So I added a delay to make sure the token is actually invalid
        await sleep(2)
        
        # Check if the token login was successful
        try:
            await self.browser.main_tab.wait_for(DSS.textbox_css, timeout = 5)
        except:
            self.logger.debug("Token failed, logging in using email and password...")
            return await self._login_classic(token_failed = True)
    
        self.logger.debug("Token login successful!")
        
    async def _login_classic(self, token_failed: bool = False) -> None:
        """Logs in to DeepSeek using email and password.

        Args
        ---------
            token_failed (bool): Indicates whether the token login attempt failed.
        
        Raises:
        ---------
            InvalidCredentials: If the email or password is incorrect.
        """

        self.logger.debug("Entering the email and password...")
        email_input = await self.browser.main_tab.select(DSS.email_input_css)
        await email_input.send_keys(self._email)

        password_input = await self.browser.main_tab.select(DSS.password_input_css)
        await password_input.send_keys(self._password)

        self.logger.debug("Checking the confirm checkbox and logging in...")
        confirm_checkbox = await self.browser.main_tab.select(DSS.confirm_checkbox_css)
        await confirm_checkbox.click()

        login_button = await self.browser.main_tab.select(DSS.login_button_css)
        await login_button.click()

        try:
            await self.browser.main_tab.wait_for(DSS.textbox_css, timeout = 5)
        except:
            raise InvalidCredentials("The email or password is incorrect" \
                if not token_failed else "Both token and email/password are incorrect")

        self.logger.debug(f"Logged in successfully using email and password! {'(Token method failed)' if token_failed else ''}")
    
    def retrieve_token(self) -> Optional[str]:
        """Retrieves the token from the browser's local storage.
        
        Returns
        ---------
            Optional[str]: The token if found, otherwise None.
        """
        
        return self.browser.main_tab.evaluate(
            "JSON.parse(localStorage.getItem('userToken')).value",
            await_promise = True,
            return_by_value = True
        )

    async def send_message(
        self,
        message: str,
        slow_mode: bool = False,
        deepthink: bool = False,
        search: bool = False,
        timeout: int = 60,
        slow_mode_delay: float = 0.25
    ) -> Optional[Response]:
        """Sends a message to the DeepSeek chat.

        Args
        ---------
            message (str): The message to send.
            slow_mode (bool): Whether to send the message character by character with a delay.
            deepthink (bool): Whether to enable deepthink mode.
                - Setting this to True will add 20 seconds to the timeout.
            search (bool): Whether to enable search mode.
                - Setting this to True will add 60 seconds to the timeout.
            timeout (int): The maximum time to wait for a response.
                - Sometimes a response may take longer than expected, so it's recommended to increase the timeout if necessary.
                - Do note that the timeout increases by 20 seconds if deepthink is enabled, and by 60 seconds if search is enabled.
            slow_mode_delay (float): The delay between sending each character in slow mode.

        Returns
        ---------
            Optional[Response]: The generated response from DeepSeek, or None if no response is received within the timeout.
        """

        timeout += 20 if deepthink else 0
        timeout += 60 if search else 0

        self.logger.debug(f"Finding the textbox and sending the message: {message}")
        textbox = await self.browser.main_tab.select(DSS.textbox_css)
        if slow_mode:
            for char in message:
                await textbox.send_keys(char)
                await sleep(slow_mode_delay)
        else:
            await textbox.send_keys(message)

        # Find the parent div of both deepthink and search options
        send_options_parent = await self.browser.main_tab.select(DSS.send_options_parent_css)
        
        if deepthink != self._deepthink_enabled:
            await send_options_parent.children[0].click() # DeepThink (R1)
            self._deepthink_enabled = deepthink
        
        if search != self._search_enabled:
            await send_options_parent.children[1].click() # Search
            self._search_enabled = search

        send_button = await self.browser.main_tab.select(DSS.send_button_css)
        await send_button.click()

        return await self._get_response(timeout = timeout)

    async def regenerate_response(self, timeout: int = 60) -> Optional[Response]:
        """Regenerates the response from DeepSeek.

        Args
        ---------
            timeout (int): The maximum time to wait for the response.

        Returns
        ---------
            Optional[Response]: The regenerated response from DeepSeek, or None if no response is received within the timeout.
        """

        # Find the last response so I can access it's buttons
        toolbar = await self.browser.main_tab.select_all(DSS.response_toolbar_css)
        await toolbar[-1].children[1].click()

        return await self._get_response(timeout = timeout, regen = True)
    
    def _filter_search_results(
        self,
        search_results_children: list,
    ):
        """Filters the search results and returns a list of SearchResult objects.

        Args
        ---------
            search_results_children (list): The search results children.

        Returns
        ---------
            list: A list of SearchResult objects.
        """

        search_results = []
        for search_result in search_results_children:
            search_results.append(
                SearchResult(
                    image_url = BeautifulSoup(
                        str(search_result.children[0].children[0].children),
                        'html.parser'
                    ).find('img')['src'],
                    website = search_result.children[0].children[1].text_all,
                    date = search_result.children[0].children[2].text_all,
                    index = int(search_result.children[0].children[3].text_all),
                    title = search_result.children[1].text_all,
                    description = search_result.children[2].text_all
                )
            )
        
        return search_results

    async def _get_response(self, timeout: int = 60, regen: bool = False) -> Optional[Response]:
        """Waits for and retrieves the response from DeepSeek.

        Args
        ---------
            timeout (int): The maximum time to wait for the response.
            regen (bool): Whether the response is a regenerated response.

        Returns
        ---------
            Optional[Response]: The generated response from DeepSeek, or None if no response is received within the timeout.
        """

        end_time = time() + timeout

        # Wait till the response starts generating
        # If we don't wait for the response to start re/generating, we might get the previous response
        self.logger.debug("Waiting for the response to start generating..." if not regen \
            else "Waiting for the response to start regenerating...")
        while time() < end_time:
            try:
                _ = await self.browser.main_tab.select(DSS.response_generating_css if not regen \
                    else DSS.regen_loading_icon_css)
            except:
                continue
            else:
                break
        
        if time() >= end_time:
            return None

        # Once the response starts generating, wait till it's generated
        response_generated = None
        self.logger.debug("Waiting for the response to finish generating..." if not regen \
            else "Finding the last response...")
        while time() < end_time:
            try:
                response_generated: zendriver.Element = await self.browser.main_tab.select_all(DSS.response_generated_css)
            except:
                continue

            if response_generated:
                break
        
        if not response_generated:
            return None
        
        if regen:
            # Wait till toolbar appears
            self.logger.debug("Waiting for the response toolbar to appear...")
            while time() < end_time:
                # I need to keep refreshing the response_generated list because the elements change
                try:
                    response_generated: zendriver.Element = await self.browser.main_tab.select_all(DSS.response_generated_css)
                except Exception as e:
                    continue

                # Check if the toolbar is present
                soup = BeautifulSoup(repr(response_generated[-1]), 'html.parser')
                toolbar = soup.find("div", class_ = DSS.response_toolbar_b64_css)
                if not toolbar:
                    continue

                response_generated = await self.browser.main_tab.select_all(DSS.response_generated_css)
                break
            
            if time() >= end_time:
                return None

        self.logger.debug("Extracting the response text...")
        soup = BeautifulSoup(repr(response_generated[-1]), 'html.parser')
        markdown_blocks = soup.find_all("div", class_ = "ds-markdown ds-markdown--block")
        response_text = "\n\n".join(get_text(str(block)).strip() for block in markdown_blocks)

        if response_text.lower() == "the server is busy. please try again later.":
            raise ServerDown("The server is busy. Please try again later.")

        # 1 and 2 are the deepthink and search options
        search_results = None
        deepthink_duration = None
        deepthink_content = None
        for child in response_generated[-1].children[1:3]:
            if match(r"found \d+ results", child.text.lower()) and self.include_search:
                self.logger.debug("Extracting the search results...")
                # So this is a search result option, we need to click it and find the search results div
                await child.click()

                search_results_div = await self.browser.main_tab.select_all(DSS.search_results_div)
                # First child is "Search Results". Second child is the actual search results
                search_results_div_children = search_results_div[-1].children[1].children

                search_results = self._filter_search_results(search_results_div_children)
            
            if match(r"thought for \d+(\.\d+)? seconds", child.text.lower()) and self.include_deepthink:
                self.logger.debug("Extracting the deepthink duration and content...")
                # This is the deepthink option, we can find the duration through splitting the text
                deepthink_duration = int(child.text.split()[2])
                
                # DeepThink content is shown by default, no need to click anything
                deepthink_content_div = await self.browser.main_tab.select_all(DSS.deepthink_content_css)
                soup = BeautifulSoup(repr(deepthink_content_div[-1]), 'html.parser')
                deepthink_content = "\n".join(get_text(str(p)).strip() for p in soup.find_all('p'))

        response = Response(
            text = response_text,
            chat_id = self._chat_id,
            deepthink_duration = deepthink_duration,
            deepthink_content = deepthink_content,
            search_results = search_results
        )
        
        self.logger.debug("Response generated!")
        return response
    
    async def reset_chat(self) -> None:
        """Resets the chat by clicking the reset button."""
        reset_chat_button = await self.browser.main_tab.select(DSS.reset_chat_button_css)
        await reset_chat_button.click()
        self.chat_id = ""
        self.logger.debug("Chat reset!")
    
    async def logout(self) -> None:
        """Logs out of the DeepSeek account."""
        self.logger.debug("Logging out...")
        await self.browser.main_tab.evaluate("localStorage.removeItem('userToken')", await_promise = True)
        await self.browser.main_tab.reload()
        self.logger.debug("Logged out successfully!")
