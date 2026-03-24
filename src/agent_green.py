from typing import Any

from pydantic import BaseModel, HttpUrl, ValidationError
from a2a.server.tasks import TaskUpdater
from a2a.utils import new_agent_text_message

from messenger import Messenger


class EvalRequest(BaseModel):
    """Request format sent by the AgentBeats platform to green agents."""
    participants: dict[str, HttpUrl]
    config: dict[str, Any]


class Agent:
    # Fill in: list of required participant roles, e.g. ["pro_debater", "con_debater"]
    required_roles: list[str] = []
    # Fill in: list of required config keys, e.g. ["topic", "num_rounds"]
    required_config_keys: list[str] = []

    def __init__(self):
        self.messenger = Messenger()
        # initialize other state here

    async def run(self, input_text: str, updater: TaskUpdater) -> None:
        """Parse EvalRequest and delegate to evaluate(). Override evaluate(), not this."""
        try:
            req = EvalRequest.model_validate_json(input_text)
        except ValidationError as e:
            await updater.reject(new_agent_text_message(f"Invalid request: {e}", updater.context_id))
            return

        missing_roles = set(self.required_roles) - set(req.participants.keys())
        if missing_roles:
            await updater.reject(new_agent_text_message(f"Missing roles: {missing_roles}", updater.context_id))
            return

        missing_keys = set(self.required_config_keys) - set(req.config.keys())
        if missing_keys:
            await updater.reject(new_agent_text_message(f"Missing config keys: {missing_keys}", updater.context_id))
            return

        await self.evaluate(req.participants, req.config, updater)

    async def evaluate(
        self,
        participants: dict[str, HttpUrl],
        config: dict[str, Any],
        updater: TaskUpdater,
    ) -> None:
        """Implement your evaluation logic here.

        Args:
            participants: Map of role name to agent URL
            config: Evaluation configuration from the request
            updater: Report progress (update_status) and results (add_artifact)

        Use self.messenger.talk_to_agent(message, url) to call participant agents.
        """
        raise NotImplementedError("Agent not implemented.")
