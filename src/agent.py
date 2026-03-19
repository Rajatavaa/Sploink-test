import json
import re
import os
from dotenv import load_dotenv
from groq import AsyncGroq

load_dotenv()

client = AsyncGroq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

AGENT_REGISTRY = None


def load_agents():
    """Load agents from registry."""
    global AGENT_REGISTRY
    if AGENT_REGISTRY is None:
        try:
            with open("register.json", "r") as f:
                data = json.load(f)
                AGENT_REGISTRY = data.get("agents", [])
        except FileNotFoundError:
            AGENT_REGISTRY = []
    return AGENT_REGISTRY


async def summarize(user_input: str) -> str:
    """Summarizer Agent using Groq."""
    try:
        text = user_input.replace("summarize", "").replace("summary", "").strip()
        if not text:
            text = user_input

        chat_completion = await client.chat.completions.create(
            messages=[
                {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
            ],
            model="llama-3.1-8b-instant",
        )
        return (
            chat_completion.choices[0].message.content
            or "[Summary Error] Empty response"
        )
    except Exception as e:
        return f"[Summary Error] {str(e)}"


async def research(query: str) -> str:
    """Research Agent using Groq."""
    try:
        question = (
            query.replace("research", "")
            .replace("find", "")
            .replace("what is", "")
            .replace("who is", "")
            .replace("how to", "")
            .strip()
        )
        if not question:
            question = query

        chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Research and provide information about: {question}",
                }
            ],
            model="llama-3.1-8b-instant",
        )
        return (
            chat_completion.choices[0].message.content
            or "[Research Error] Empty response"
        )
    except Exception as e:
        return f"[Research Error] {str(e)}"


async def calculate(user_input: str) -> str:
    """Calculator Agent - Evaluates math expressions."""
    try:
        import re

        expr = re.sub(r"[a-zA-Z]", "", user_input)
        expr = expr.strip()

        if not expr:
            return "[Calculator] Error: No expression found"

        safe_chars = set("0123456789+-*/.() ")
        if all(c in safe_chars or c.isspace() for c in expr):
            result = eval(expr.strip())
            return f"[Calculation] Result: {result}"
        else:
            return "[Calculator] Error: Invalid characters in expression"
    except Exception as e:
        return f"[Calculator] Error: {str(e)}"


async def generate_content(prompt: str) -> str:
    """Content Generator Agent using Groq."""
    try:
        content_prompt = (
            prompt.replace("write", "")
            .replace("generate", "")
            .replace("create", "")
            .replace("draft", "")
            .strip()
        )
        if not content_prompt:
            content_prompt = prompt

        chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Generate creative content based on: {content_prompt}",
                }
            ],
            model="llama-3.1-8b-instant",
        )
        return (
            chat_completion.choices[0].message.content
            or "[Content Error] Empty response"
        )
    except Exception as e:
        return f"[Content Generation Error] {str(e)}"


AGENT_FUNCTIONS = {
    "Basic Summarizer": summarize,
    "Advanced Summarization Agent": summarize,
    "Research Agent": research,
    "Calculator Agent": calculate,
    "Content Generator": generate_content,
}


async def execute_agent(agent: dict, user_input: str) -> str:
    """Executes the selected agent with user input."""
    agent_name = agent.get("name")

    if agent_name in AGENT_FUNCTIONS:
        func = AGENT_FUNCTIONS[agent_name]
        result = await func(user_input)
        return result if result is not None else f"[Error] Agent returned None"

    return f"[Error] No implementation found for agent: {agent_name}"
