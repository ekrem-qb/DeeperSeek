import asyncio
import os
import shlex
import sys

from DeeperSeek import DeepSeek  # type: ignore


async def main():
    # Read the message from environment variables
    message = os.getenv("DEEPSEEK_MESSAGE")
    if not message:
        print("Error: DEEPSEEK_MESSAGE environment variable is required.", file=sys.stderr)
        sys.exit(1)

    # Read other optional parameters
    token = os.getenv("DEEPSEEK_TOKEN")
    email = os.getenv("DEEPSEEK_EMAIL")
    password = os.getenv("DEEPSEEK_PASSWORD")
    chat_id = os.getenv("DEEPSEEK_CHAT_ID")

    # Parse boolean flags with appropriate defaults
    headless = os.getenv("DEEPSEEK_HEADLESS", "true").lower() == "true"
    verbose = os.getenv("DEEPSEEK_VERBOSE", "false").lower() == "true"
    attempt_cf_bypass = os.getenv("DEEPSEEK_ATTEMPT_CF_BYPASS", "true").lower() == "true"

    # Parse Chrome arguments from a string into a list
    chrome_args_str = os.getenv("DEEPSEEK_CHROME_ARGS", "")
    chrome_args = shlex.split(chrome_args_str) if chrome_args_str else []

    # Initialize the DeepSeek API with environment variables
    api = DeepSeek(
        email=email,
        password=password,
        token=token,
        chat_id=chat_id,
        chrome_args=chrome_args,
        verbose=verbose,
        headless=headless,
        attempt_cf_bypass=attempt_cf_bypass,
    )

    await api.initialize()

    # Send the message and handle the response
    response = await api.send_message(message, deepthink=True)

    if not response:
        print("Error: Empty response from the API.", file=sys.stderr)
        sys.exit(1)

    print(response.text)


if __name__ == "__main__":
    asyncio.run(main())