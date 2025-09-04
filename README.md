# HOLMES - Health Operations & Live Monitoring Expert System

A Slack bot designed to help teams efficiently resolve incidents through intelligent monitoring and automated response capabilities.

## Overview

HOLMES is an incident management Slack bot that provides real-time monitoring, alerting, and incident resolution assistance. It helps teams quickly identify, diagnose, and resolve operational issues.

## Features

- **Incident Detection**: Real-time monitoring and alerting for system health issues
- **Automated Response**: Intelligent incident response and resolution suggestions
- **Slack Integration**: Seamless integration with Slack for team collaboration
- **Live Monitoring**: Continuous system health checks and performance monitoring
- **Expert System**: Knowledge-based recommendations for incident resolution

## Setup

### Prerequisites
- Python 3.9+
- Poetry (for dependency management)
- Docker & Docker Compose (optional)
- Slack workspace with admin access

### Local Development with venv and Poetry

1. **Create and activate virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Poetry in the virtual environment:**
```bash
pip install poetry
```

3. **Install dependencies:**
```bash
poetry install
```

4. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your Slack credentials
```

5. **Run the bot:**
```bash
poetry run python -m app.main
# Or use the Makefile:
make run
```

### Docker Setup

1. **Build the Docker image:**
```bash
docker-compose build
# Or for production:
docker build -t holmes-bot .
```

2. **Run with Docker Compose:**
```bash
docker-compose up -d
# View logs:
docker-compose logs -f holmes-bot
```

### Slack App Configuration

1. Create a new Slack app at https://api.slack.com/apps
2. Add the following Bot Token Scopes:
   - `app_mentions:read`
   - `channels:history`
   - `chat:write`
   - `commands`
3. Install the app to your workspace
4. Copy the tokens to your `.env` file:
   - Bot User OAuth Token → `SLACK_BOT_TOKEN`
   - Signing Secret → `SLACK_SIGNING_SECRET`
   - App-Level Token → `SLACK_APP_TOKEN` (for Socket Mode)

## Development

### Running Tests
```bash
make test
```

### Linting & Formatting
```bash
make lint    # Run flake8 and mypy
make format  # Format with black
```

### Project Structure
```
holmes/
├── app/
│   ├── __init__.py
│   └── main.py          # Main bot application
├── tests/
│   └── test_main.py     # Unit tests
├── .env.example         # Environment variables template
├── docker-compose.yml   # Docker Compose configuration
├── Dockerfile          # Production Docker image
├── Dockerfile.dev      # Development Docker image
├── Makefile           # Common commands
├── poetry.lock        # Locked dependencies
└── pyproject.toml     # Project configuration
```

## Commands

The bot responds to:
- Direct messages containing "hello"
- App mentions
- Slash commands: `/holmes [status|scan|report|help]`

## License

*To be determined*
