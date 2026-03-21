# Development Plan: LMS Telegram Bot

## Overview

This document outlines the development plan for the LMS Telegram Bot that integrates with the Learning Management Service API and uses an LLM for intent routing and natural language queries.

## Architecture Principles

The bot follows a **layered architecture** with clear separation of concerns:

1. **Transport Layer** (`bot.py`): Handles Telegram API communication via aiogram
2. **Handler Layer** (`handlers/`): Command and message processing logic
3. **Service Layer** (`services/`): External API clients (LMS API, LLM API)
4. **Configuration Layer** (`config.py`): Environment variable loading and validation

The key design principle is **testable handlers**: all command logic is implemented as pure functions that take input and return text responses. They have no dependency on Telegram. This enables the `--test` mode for offline verification without connecting to Telegram.

## Task Breakdown

### Task 1: Project Scaffolding (Current)

- Create directory structure: `bot/`, `handlers/`, `services/`
- Implement `bot.py` entry point with `--test` mode support
- Create placeholder handlers for `/start`, `/help`, `/health`, `/labs`, `/scores`
- Set up `pyproject.toml` with dependencies (aiogram, httpx, pydantic-settings)
- Create `.env.bot.example` and `.env.bot.secret` for configuration
- Write this development plan

### Task 2: Backend Integration

- Implement `services/lms_client.py`: HTTP client for LMS API calls
- Implement `services/llm_client.py`: HTTP client for LLM API calls
- Connect handlers to real API endpoints
- Implement `/health` to check backend availability
- Implement `/labs` to fetch available labs from LMS API
- Implement `/scores <lab_id>` to fetch student scores

### Task 3: Intent Routing with LLM

- Implement natural language understanding using LLM
- Parse user queries like "what labs are available" into commands
- Route intents to appropriate handlers
- Add fallback handling for unrecognized intents
- Implement conversational context if needed

### Task 4: Deployment and Hardening

- Configure production deployment on VM
- Set up process management (nohup/systemd)
- Add logging and error handling
- Implement graceful shutdown
- Add rate limiting and error recovery
- Document deployment procedures

## Testing Strategy

- **Unit tests**: Test handlers in isolation with mocked services
- **Integration tests**: Test API client interactions
- **Manual testing**: Use `--test` mode for quick verification
- **E2E testing**: Deploy and test in Telegram

## Dependencies

- `aiogram>=3.20`: Async Telegram Bot API framework
- `httpx==0.28.1`: Async HTTP client for API calls
- `pydantic-settings==2.12.0`: Configuration management

## Environment Variables

| Variable | Description | Source |
|----------|-------------|--------|
| `BOT_TOKEN` | Telegram bot token | BotFather |
| `LMS_API_BASE_URL` | LMS API base URL | Backend deployment |
| `LMS_API_KEY` | LMS API authentication key | Backend config |
| `LLM_API_KEY` | LLM API authentication key | LLM provider |
| `LLM_API_BASE_URL` | LLM API base URL | LLM provider |
| `LLM_API_MODEL` | LLM model name | LLM provider |

## File Structure

```
bot/
├── bot.py              # Entry point with --test mode
├── config.py           # Configuration loading
├── handlers/
│   ├── __init__.py
│   ├── start.py        # /start command
│   ├── help.py         # /help command
│   ├── health.py       # /health command
│   ├── labs.py         # /labs command
│   └── scores.py       # /scores command
├── services/
│   ├── __init__.py
│   ├── lms_client.py   # LMS API client
│   └── llm_client.py   # LLM API client
├── pyproject.toml      # Dependencies
├── PLAN.md             # This file
└── .env.bot.example    # Environment template
```
