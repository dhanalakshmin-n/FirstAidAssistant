DISCLAIMER = (
    "This guidance does not replace professional medical help. "
    "Call emergency services if the condition is severe."
)

def guardrail_router(text: str):
    if not text:
        return {"type": "reject", "response": "I didn’t catch that."}

    text = text.lower().strip()

    # Goodbye detection
    goodbyes = ["bye", "goodbye", "exit", "quit", "thank you", "thanks"]
    if any(g in text for g in goodbyes):
        return {
            "type": "local",
            "response": "Bye. Have a nice day. Stay safe!",
        }

    # Greeting detection
    greetings = ["hi", "hello", "hey", "good morning", "good evening"]
    if any(g in text for g in greetings):
        return {
            "type": "local",
            "response": (
                "Hello. I am your emergency first aid assistant. "
                "How can I help you today?"
            ),
        }

    # Emergency detection
    emergency_keywords = [
        "bleeding",
        "burn",
        "fracture",
        "unconscious",
        "not breathing",
        "choking",
        "heart attack",
        "cut",
        "injury",
        "shock",
        "emergency",
        "cpr",
    ]
    if any(word in text for word in emergency_keywords):
        return {"type": "backend"}

    # Fallback
    return {
        "type": "reject",
        "response": (
            "I am trained only for bleeding, burns, casualty assessment, CPR, "
            "and fracture related first aid guidance. "
            + DISCLAIMER
        ),
    }


async def guardrail_llm(chat_ctx, backend_fn):
    user_text = chat_ctx.messages[-1].content

    print(f"[Guardrail] User said: {user_text}")
    decision = guardrail_router(user_text)
    print(f"[Guardrail] Decision: {decision['type']}")

    if decision["type"] == "local":
        return decision["response"]

    if decision["type"] == "reject":
        return decision["response"]

    backend_response = backend_fn(user_text)

    if DISCLAIMER not in backend_response:
        backend_response = backend_response + "\n\n" + DISCLAIMER

    return backend_response