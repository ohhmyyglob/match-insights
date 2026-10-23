"""Smoke test: can this Mac talk to the Foundry model?"""
import asyncio
import os

from dotenv import load_dotenv
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential

load_dotenv()                                   # copies .env values into os.environ


async def main() -> None:
    agent = Agent(
        client=FoundryChatClient(
            project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
            model=os.environ["FOUNDRY_MODEL"],
            credential=AzureCliCredential(),    # borrows your az login, no keys
        ),
        name="Pundit",
            instructions=(
            "You are an over-excited home-team superfan. Use emotion, "
            "exclamation marks and fan language, but stay under three sentences."
            ),
    )
    reply = await agent.run("Why does a late equaliser change a match more than an early goal?")
    print(reply)


if __name__ == "__main__":
    asyncio.run(main())