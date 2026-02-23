from dotenv import load_dotenv
load_dotenv()

from guardrails import guardrail_llm

import asyncio
import logging
import uuid

import requests

from livekit.agents import (
    JobContext,
    JobRequest,
    WorkerOptions,
    cli,
    AgentSession,
    Agent,
    AutoSubscribe,
)
from livekit.agents.llm import LLM, LLMStream, ChatChunk, ChoiceDelta
from livekit.agents.llm.chat_context import ChatContext
from livekit.agents.types import DEFAULT_API_CONNECT_OPTIONS, APIConnectOptions
from livekit.plugins import deepgram, silero



logger = logging.getLogger("firstaid-agent")

BACKEND_URL = "http://127.0.0.1:8000/agent/query"


def _ask_backend_sync(question: str) -> str:
    
    try:
        res = requests.post(
            BACKEND_URL,
            json={"question": question},
            timeout=60,
        )
        return res.json().get("response", "No response from backend.")
    except Exception as e:
        logger.exception("Backend query failed: %s", e)
        return f"Sorry, I couldn't reach the first aid knowledge base: {str(e)}"


class BackendLLM(LLM):
    
    @property
    def model(self) -> str:
        return "firstaid-rag"

    @property
    def provider(self) -> str:
        return "firstaid-backend"

    def chat(
        self,
        *,
        chat_ctx: ChatContext,
        tools=None,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
        **kwargs,
    ) -> LLMStream:
        return _BackendLLMStream(llm=self, chat_ctx=chat_ctx, tools=tools or [], conn_options=conn_options)


class _BackendLLMStream(LLMStream):
    async def _run(self) -> None:
        from livekit.agents.llm.chat_context import ChatRole

        items = list(self._chat_ctx.items)
        question = "Hello"
        for item in reversed(items):
            if getattr(item, "type", None) == "message" and getattr(item, "role", None) == "user":
                text = (
                    getattr(item, "text_content", None)
                    or getattr(item, "text", None)
                    or getattr(item, "content", None)
                    or ""
                )
                if isinstance(text, str) and text.strip():
                    question = text.strip()
                break

        response = await guardrail_llm(
            type("ChatCtx", (), {"messages": [type("Msg", (), {"content": question})()]})(),
            _ask_backend_sync,
        )
        chunk_id = f"bk-{uuid.uuid4().hex[:8]}"
        self._event_ch.send_nowait(
            ChatChunk(id=chunk_id, delta=ChoiceDelta(role="assistant", content=response))
        )


async def on_request(req: JobRequest) -> None:
    logger.info(
        "received job request room=%s agent_name=%s job_id=%s",
        req.room.name,
        req.agent_name,
        req.id,
    )
    print("Received job request:", req.room.name, "| job_id:", req.id)
    await req.accept(name="First Aid Assistant", identity="firstaid-agent")


async def entrypoint(ctx: JobContext) -> None:
    logger.info("entrypoint started room=%s", ctx.room.name)
    print("LiveKit Voice Agent Started — room:", ctx.room.name)

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    agent = Agent(
        instructions="""
        You are an emergency first aid voice assistant.
        Provide calm, clear, step-by-step help.
        Keep answers short and practical.
        """,
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-2", language="en"),
        llm=BackendLLM(),
        tts=deepgram.TTS(model="aura-asteria-en"),
    )

    session = AgentSession()

    await session.start(
        agent=agent,
        room=ctx.room
    )

    logger.info("agent joined room and ready room=%s", ctx.room.name)
    print("Agent joined room and ready")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="firstaid-agent",
            request_fnc=on_request,
        )
    )