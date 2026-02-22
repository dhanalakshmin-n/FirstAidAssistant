import asyncio
import os
from dotenv import load_dotenv

from livekit import api

load_dotenv()

ROOM_NAME = "emergency-room"
AGENT_NAME = "firstaid-agent"


async def main() -> None:
    url = os.getenv("LIVEKIT_URL")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")

    if not all([url, api_key, api_secret]):
        print("Error: LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET must be set in .env")
        return

    async with api.LiveKitAPI(url, api_key, api_secret) as lkapi:
        dispatch = await lkapi.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name=AGENT_NAME,
                room=ROOM_NAME,
                metadata="",
            )
        )
        print(f"Agent dispatched: {dispatch.agent_name} -> room '{ROOM_NAME}'")
        print(f"Dispatch ID: {dispatch.id}")
        


if __name__ == "__main__":
    asyncio.run(main())
