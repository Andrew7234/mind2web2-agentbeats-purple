# Mind2Web-2 Research Agent (Purple Agent)

A web research agent that answers complex information-gathering tasks with cited sources. This is the **purple agent** (competitor) in the AgentBeats Mind2Web-2 scenario.

## How It Works

Receives a research task description via A2A, calls an LLM to produce a markdown answer with URL citations, and returns the answer as an artifact. The agent instructs the LLM to:

- Address every part of the task
- Include specific markdown-formatted URL links to sources
- Organize information with headings, lists, or tables
- Provide concrete data points rather than vague summaries

## Project Structure

```
src/
├─ server.py      # A2A server and agent card
├─ executor.py    # A2A request handling
├─ agent.py       # LLM-based research agent
└─ messenger.py   # A2A messaging utilities
Dockerfile            # Docker build
pyproject.toml        # Dependencies
amber-manifest.json5  # Amber manifest
```

## Running Locally

```bash
uv sync
AGENT_LLM=gemini/gemini-2.0-flash GEMINI_API_KEY=... uv run src/server.py --port 9019
```

## Running with Docker

```bash
docker build -t mind2web2-purple .
docker run -p 9019:9009 -e AGENT_LLM=gemini/gemini-2.0-flash -e GEMINI_API_KEY=... mind2web2-purple
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AGENT_LLM` | no (default: `openai/gpt-4o-mini`) | LLM model in [litellm format](https://docs.litellm.ai/docs/providers) |
| `GEMINI_API_KEY` | if using Gemini | Gemini API key |
| `OPENAI_API_KEY` | if using OpenAI | OpenAI API key |
| `ANTHROPIC_API_KEY` | if using Anthropic | Anthropic API key |
| `DEEPSEEK_API_KEY` | if using DeepSeek | DeepSeek API key |
| `AGENT_LLM_MAX_RETRIES` | no (default: `5`) | Max retry attempts for transient LLM errors |
| `AGENT_LLM_BACKOFF_BASE` | no (default: `2`) | Exponential backoff base in seconds |

## Running Both Agents Together

```bash
# Terminal 1: Purple agent
cd ~/oasis/agent-template
AGENT_LLM=gemini/gemini-2.0-flash GEMINI_API_KEY=... uv run src/server.py --port 9019

# Terminal 2: Green agent (evaluator)
cd ~/oasis/green-agent-template
AGENT_LLM=gemini/gemini-2.0-flash GEMINI_API_KEY=... uv run src/server.py --port 9009

# Terminal 3: Run evaluation
cd ~/oasis/green-agent-template
uv run test_run.py
```
