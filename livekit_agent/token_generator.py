import os
from dotenv import load_dotenv

from livekit.api import (
    AccessToken,
    VideoGrants,
    RoomConfiguration,
    RoomAgentDispatch,
)

load_dotenv()

api_key = os.getenv("LIVEKIT_API_KEY")
api_secret = os.getenv("LIVEKIT_API_SECRET")

ROOM_NAME = "emergency-room"
IDENTITY = "dhanu-user"
AGENT_NAME = "firstaid-agent"


def create_token(
    room_name: str = ROOM_NAME,
    identity: str = IDENTITY,
    agent_name: str = AGENT_NAME,
) -> str:
    token = (
        AccessToken(api_key, api_secret)
        .with_identity(identity)
        .with_grants(VideoGrants(room_join=True, room=room_name))
        .with_room_config(
            RoomConfiguration(
                agents=[
                    RoomAgentDispatch(agent_name=agent_name, metadata=""),
                ]
            )
        )
    )
    return token.to_jwt()


def create_simple_token(
    room_name: str = ROOM_NAME,
    identity: str = IDENTITY,
) -> str:
    token = (
        AccessToken(api_key, api_secret)
        .with_identity(identity)
        .with_grants(VideoGrants(room_join=True, room=room_name))
    )
    return token.to_jwt()


if __name__ == "__main__":
    import sys
    if "--simple" in sys.argv:
        print(create_simple_token())
    else:
        print(create_token())