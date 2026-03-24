# A2A Agent Template

A minimal template for building [A2A (Agent-to-Agent)](https://a2a-protocol.org/latest/) agents compatible with the [AgentBeats](https://agentbeats.dev) platform.

## Project Structure

```
src/
├─ server.py       # Server setup and agent card configuration
├─ executor.py     # A2A request handling
├─ agent.py        # Purple agent template
├─ agent_green.py  # Green agent template (receives EvalRequest JSON)
└─ messenger.py    # A2A messaging utilities
Dockerfile         # Docker configuration
pyproject.toml     # Python dependencies
uv.lock            # Locked dependencies
```

## Getting Started

1. **Create your repository** - Click "Use this template" to create your own repository from this template

2. **Choose your template** - Pick the appropriate starting point:
   - **Purple agent** (participant): Use [`src/agent.py`](src/agent.py) as-is.
   - **Green agent** (assessor): Replace `src/agent.py` with [`src/agent_green.py`](src/agent_green.py). Receives structured `EvalRequest` with participants and config.

3. **Implement your agent**:
   - Purple: Add your logic to the `run` method
   - Green: Fill in `required_roles`, `required_config_keys`, and implement the `evaluate` method

4. **Configure your agent card** - Fill in your agent's metadata (name, skills, description) in [`src/server.py`](src/server.py)

## Running Locally

```bash
# Install dependencies
uv sync

# Run the server
uv run src/server.py
```

## Running with Docker

```bash
# Build the image
docker build -t my-agent .

# Run the container
docker run -p 9009:9009 my-agent
```

## Publishing

The repository includes a GitHub Actions workflow that automatically builds and publishes a Docker image of your agent to GitHub Container Registry:

- **Push to `main`** → publishes `latest` tag:
```
ghcr.io/<your-username>/<your-repo-name>:latest
```

- **Create a git tag** (e.g. `git tag v1.0.0 && git push origin v1.0.0`) → publishes version tags:
```
ghcr.io/<your-username>/<your-repo-name>:1.0.0
ghcr.io/<your-username>/<your-repo-name>:1
```