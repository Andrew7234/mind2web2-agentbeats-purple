from dotenv import load_dotenv
import litellm

from a2a.server.tasks import TaskUpdater
from a2a.types import Message, TaskState, Part, TextPart
from a2a.utils import get_message_text, new_agent_text_message

load_dotenv()


class Agent:
    def __init__(self):
        self.messages = []

    async def run(self, message: Message, updater: TaskUpdater) -> None:
        input_text = get_message_text(message)
        print(f"> {input_text}")

        await updater.update_status(
            TaskState.working, new_agent_text_message("Thinking...")
        )

        self.messages.append({"content": input_text, "role": "user"})
        completion = litellm.completion(
            model="gpt-4o",
            messages=self.messages
        )
        response = completion.choices[0].message.content
        self.messages.append({"content": response, "role": "assistant"})
        print(response)

        await updater.add_artifact(
            parts=[Part(root=TextPart(text=response))],
            name="Response",
        )
