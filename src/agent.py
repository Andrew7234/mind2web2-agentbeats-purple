import asyncio
import os
import logging
import time

from a2a.server.tasks import TaskUpdater
from a2a.types import Message, Part, TextPart
from a2a.utils import get_message_text

from litellm import acompletion
from litellm.exceptions import (
    ServiceUnavailableError,
    RateLimitError,
    Timeout,
    APIConnectionError,
)

from messenger import Messenger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a web research agent. You will receive a research task that requires \
gathering information from multiple online sources.

Your job is to produce a thorough, well-structured markdown answer that:
1. Fully addresses every part of the task
2. Includes direct URLs to the sources you reference
3. Formats URLs as markdown links, e.g. [Page Title](https://example.com/page)
4. Organizes information clearly with headings, lists, or tables as appropriate
5. Provides specific data points (names, dates, numbers, prices) rather than vague summaries

Always cite your sources with real, specific URLs — not generic homepages. \
For example, link to the specific product page, patent page, or article rather \
than just the website's main page."""

RETRYABLE_EXCEPTIONS = (
    ServiceUnavailableError,
    RateLimitError,
    Timeout,
    APIConnectionError,
)


async def call_llm_with_retry(messages, model, max_retries=5, backoff_base=2):
    for attempt in range(1, max_retries + 1):
        try:
            response = await acompletion(
                messages=messages,
                model=model,
                temperature=1,
            )
            if attempt > 1:
                logger.info(f"LLM call succeeded on attempt {attempt}")
            return response
        except RETRYABLE_EXCEPTIONS as e:
            if attempt >= max_retries:
                logger.error(f"LLM call failed after {max_retries} attempts")
                raise
            backoff_seconds = backoff_base ** attempt
            logger.warning(
                f"LLM call failed (attempt {attempt}/{max_retries}): "
                f"{type(e).__name__}: {str(e)[:100]}"
            )
            await asyncio.sleep(backoff_seconds)


class Agent:
    def __init__(self):
        self.messenger = Messenger()
        self.model = os.getenv("AGENT_LLM", "openai/gpt-4o-mini")
        self.max_retries = int(os.getenv("AGENT_LLM_MAX_RETRIES", "5"))
        self.backoff_base = int(os.getenv("AGENT_LLM_BACKOFF_BASE", "2"))
        logger.info(f"Purple agent initialized with model: {self.model}")

    async def run(self, message: Message, updater: TaskUpdater) -> None:
        task_description = get_message_text(message)
        logger.info(f"Received research task ({len(task_description)} chars): {task_description[:100]}...")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": task_description},
        ]

        t0 = time.time()
        logger.info(f"Calling LLM {self.model}")
        try:
            response = await call_llm_with_retry(
                messages=messages,
                model=self.model,
                max_retries=self.max_retries,
                backoff_base=self.backoff_base,
            )
            answer = response.choices[0].message.content
            t_llm = time.time() - t0
            logger.info(f"LLM responded in {t_llm:.1f}s ({len(answer)} chars)")
        except Exception as e:
            t_llm = time.time() - t0
            logger.error(f"LLM call failed after {t_llm:.1f}s: {type(e).__name__}: {e}")
            answer = f"I was unable to complete the research task due to an error: {e}"

        await updater.add_artifact(
            parts=[Part(root=TextPart(text=answer))],
            name="Answer",
        )
