# 🧠 Project Gideon – AI Developer Bots for Discord

Welcome to **Project Gideon**, a LYTE Studios initiative to bring AI developers into your team. These bots are designed to function as full-stack AI teammates—writing code, reviewing pull requests, testing changes, and interacting naturally within your Discord workspace.

---

## 🔧 Tech Stack
- **Language**: Python
- **Framework**: Django
- **Bot Platform**: Discord (via `discord.py`)
- **AI**: OpenAI GPT-4 API
- **Code Execution**: Docker-based sandbox
- **Task Queue**: Celery + Redis
- **Database**: PostgreSQL
- **Git Integration**: GitHub REST API + GitHub Apps

---

## 📦 Features Overview
- 🤖 **AI bots as devs**: Talk, request, or assign tasks to AI developers
- 🧑‍💻 **Code generation**: Describe a task, get fully generated code with file structure
- 🛠️ **Code execution**: Securely test code in containers and return test logs
- 🔍 **Pull request reviews**: AI reviews with inline feedback and auto-labeling
- 🎭 **Custom personalities**: Each bot has its own tone, specialty, and role

---

## 🛣️ Project Roadmap

### Phase 1: Foundation & Setup
- [ ] Set up Discord bot using `discord.py` within Django project
- [ ] Basic command set: `/ping`, `/code`, `/review_pr`, etc.
- [ ] Role-based permissions in Discord

### Phase 2: Code Intelligence & Execution
- [ ] Integrate GPT-4 API for code generation tasks
- [ ] Setup Docker-based sandbox for secure code execution
- [ ] Integrate Redis + Celery for long-running task handling

### Phase 3: GitHub Automation
- [ ] Register GitHub App
- [ ] Enable PR review via `/review_pr <url>`
- [ ] Enable bot-authored commits + auto PR creation from code tasks

### Phase 4: Personalization & Learning
- [ ] Bot personalities defined via Django model
- [ ] Conversation memory & user preferences
- [ ] Feedback thumbs up/down for fine-tuning

### Phase 5: Admin & Monitoring Tools
- [ ] Django dashboard for usage stats & logs
- [ ] Bot status monitoring and kill-switch
- [ ] Discord UI improvements (buttons, embeds, threads)

---

## ⚙️ Bot Personalities
Each AI developer can be assigned a distinct role and tone.

Examples:
- **Gideon the Junior**: Eager to learn, asks clarifying questions
- **Gideon the Architect**: Provides scalable solutions and design patterns
- **Gideon the Reviewer**: Strict reviewer, focuses on best practices

Defined in `BotProfile` model:
```python
class BotProfile(models.Model):
    name = models.CharField(...)
    tone = models.TextField()
    specialties = models.JSONField()
    response_examples = models.TextField()
```

---

## 💬 Discord Commands (Planned)
| Command | Description |
|---------|-------------|
| `/ping` | Check bot responsiveness |
| `/code <task>` | Get generated code for a task |
| `/test <code>` | Run and return results of code snippet |
| `/review_pr <url>` | AI reviews GitHub PR |
| `/switch_personality` | Switch a bot's personality |

---

## 🔐 Security & Safety
- Code execution is isolated in Docker containers
- No direct code writes without sandbox testing
- Logs and outputs sanitized before posting

---

## 📈 Metrics (Planned)
- Usage per developer
- Success rate of tests
- Feedback tracking
- Top-requested functions

---

## 📂 Future Ideas
- Integration with Jira / Linear (`/link_task <id>`)
- LLM fallback (Claude, Mistral)
- Auto-doc generation
- Dev goals (e.g. "learn Rust")

---

## 👥 Core Team
- **Lead Dev**: Tanguy @ LYTE Studios
- **AI Dev**: [Redacted]
- **Infra Dev**: [Redacted]

---

## 🧠 Vision
Project Gideon is not just an automation tool—it's the future of team augmentation. We believe in blending human creativity with AI precision to scale faster, smarter, and with a smile in chat.

> "The real magic isn’t replacing developers. It’s giving them a team that never sleeps."

---

## 🛠️ To Contribute
Coming soon: GitHub repo + contribution guidelines

Stay tuned!
