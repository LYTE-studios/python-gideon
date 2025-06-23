# 📝 Project Gideon – Implementation & Planning

## Overview
Project Gideon is a LYTE Studios initiative to integrate AI-powered developer bots into Discord teams, functioning as true development teammates. These bots can write code, review pull requests, test changes, and interact naturally within Discord.

---

## Tech Stack

- **Language**: Python
- **Framework**: Django
- **Bot Platform**: Discord (via `discord.py`)
- **AI**: OpenAI GPT-4 API (and ChatGPT for assistant bot)
- **Code Execution**: Docker-based sandbox
- **Task Queue**: Celery + Redis
- **Database**: PostgreSQL
- **Git Integration**: GitHub REST API + GitHub Apps

---

## Feature Deliverables & Breakdown

### 1. Core AI Developer Bot Functionality

#### a. Discord Bot Integration
- Embed Discord.py bot in Django project.
- Register Discord bot, configure permissions.
- Set up basic commands (`/ping`, `/code`, `/review_pr`, `/help`, etc.).
- Role-based permissions in Discord using Django/Discord roles.

#### b. AI Code Generation and PR Review
- Integrate GPT-4 for code/text generation.
- Code generation via `/code` Discord command, with context awareness.
- Pull request review via `/review_pr <url>` (GPT-4 powered inline analysis).
- Bots can provide explanations, suggested improvements, and auto-label PRs.
- Capability for bots to author commits & auto-create PRs from code suggestions.

#### c. Secure Code Execution
- Docker sandbox service to run and test generated code.
- `/test <code>` command for executing user-submitted snippets.
- Return and sanitize logs/output before posting to Discord.

#### d. Task Management
- Integrate Celery + Redis for asynchronous/background tasks (e.g. code execution, PR review).
- Post background task results to Discord as follow-ups.

#### e. Bot Customization & Learning
- Each bot has a `BotProfile` (distinct name, tone, specialties, response examples).
- `/switch_personality` command for dynamically changing personalities/roles.
- Conversation memory (short-term, per user) and preferences.
- Feedback collection (thumbs up/down on responses) for system improvement.

#### f. Admin, Monitoring & Metrics
- Django dashboard with usage stats, logs, and error rates.
- Bot status monitoring and kill switch for admins.
- Discord UI improvements: use of embeds, message threads, actionable buttons (where possible).
- Metrics tracked: usage per developer, test pass rate, feedback, and top-requested actions.

---

### 2. Assistant Chatbot Functionality

#### a. Assistant Bot as Guide & Scheduler
- Dedicated Assistant bot, powered by ChatGPT (OpenAI API).
- Responds to queries explaining ALL features and workflows of the developer bots, with up-to-date documentation style responses.
- Can process questions about how to use commands, features, or get assistance with common tasks in Project Gideon.
- Provides friendly, accessible, and comprehensive answers.

#### b. Event & Meeting Scheduling
- Assistant bot can create and edit Discord events (using Discord API endpoints).
- Commands to schedule meetings, edit or delete events, and notify users.
- Ability to handle scheduling conflicts and suggest available slots.
- (Optionally) integrate with calendar services for reminders or further automation.

---

## Phased Execution Plan

### Phase 1: Foundation & Setup
- Bootstrap Django project; integrate Discord.py.
- Set up bot registration and minimal commands.
- Set up Postgres and connect to Django.
- Implement role-based permissions/checks.

### Phase 2: Code Intelligence & Execution
- Integrate GPT-4 API.
- Build `/code` command with contextual code generation.
- Implement Docker sandbox service.
- Add `/test` for secure code execution.
- Hook in Celery & Redis for async operations.

### Phase 3: GitHub Automation
- Register GitHub App and configure permissions.
- Integrate GitHub REST API for PR review/automation.
- Develop `/review_pr` and PR creation features.

### Phase 4: Personalization & Learning
- Implement `BotProfile` model and personality switching.
- Add user conversation memory and feedback tools.
- Enable thumbs up/down and feedback metrics tracking.

### Phase 5: Admin & Monitoring Tools
- Build Django admin dashboard for monitoring and logs.
- Add bot status controls and Discord UI enhancements.

### Phase 6: Assistant Chatbot & Scheduling
- Add Assistant bot using ChatGPT API.
- Answer full range of bot and feature-related queries.
- Build event management commands (create, edit, delete Discord events).
- Implement scheduling workflows, notifications, and (optionally) calendar integration.

---

## Security & Best Practices

- ALL code execution is sandboxed via Docker.
- No file modifications outside the sandbox unless verified by tests.
- Logs/output sanitized before Discord posting.
- Secrets/tokens are environment-managed; never committed.
- Monitoring and logging always enabled.

---

## Future Ideas (Extended Goals)

- Integrate project/task trackers like Jira/Linear.
- Support multiple LLMs (Claude, Mistral) as fallback.
- Auto-generating documentation from PR/code outputs.
- Dev “Goals” and progress tracking for upskilling.
- Community contribution guidelines & repo automation.

---

## Contribution & Team

- **Lead Dev:** Tanguy @ LYTE Studios
- **AI Dev:** [Redacted]
- **Infra Dev:** [Redacted]

Stay tuned for GitHub repo and further contributor on-ramps!