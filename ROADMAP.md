# 🗺️ Project Gideon – New Roadmap (Developer & PR Automation)

A focused roadmap for upcoming core improvements:
- Delegation between assistant and developer personalities
- Deep GitHub Pull Request automation

---

## Core Goals

1. **Add Developer GPT Personality**  
   - Create a distinct "developer" persona (system prompt) specializing in code, programming Q&A, and software engineering advice.
   - Main assistant delegates any technical/coding question to this developer persona.
   - Developer persona answers those questions directly in the channel.

2. **PR Automation: Initiate, Review, Push**  
   - Enable Gideon to recognize PR-related requests and automate the steps from code proposal to review and merging.

---

## Milestone 1: Developer Assistant Integration

### 1. Create Developer Persona Logic
- Implement a second ChatGPT persona in code ("developer"), with a tailored system prompt for code/software Q&A.
- The assistant detects technical/dev/software/PR/code questions/conversations.
- If detected, assistant routes the request to this persona and posts the developer’s answer instead of its own.
- Add tests for persona switching and routing.

### 2. Define Persona Prompts
- Draft and codify system prompts for both:
  - General assistant (current: friendly, life/productivity/events)
  - Developer (direct, technical, expert on programming and software engineering)

### 3. Developer Conversation Context
- Pass last N messages to developer persona as context, as for assistant.
- Ensure code-formatting, language, and explanations are concise and reliable.
- Confirm developer genuinely adds value beyond the generic assistant.

---

## Milestone 2: GitHub Pull Request Automation

### 4. GitHub Integration Setup
- Add or update `.env` for GitHub API token.
- Securely configure GitHub App or OAuth for repo access.

### 5. Listen for PR Requests in Chat
- Detect requests like "Gideon, create a PR for the following code..." or "Can you review PR #34?".
- Route code/PR requests either to developer persona or to actual PR automation logic.

### 6. Create Pull Request via Bot
- Implement logic to take received code (from chat or generated response) and push a branch to GitHub.
- Automatically open a PR with title/description from the user’s message.
- Log outcomes (success, errors, links).

### 7. Review Pull Requests
- Allow users to ask for a bot review on specified PRs.
- Developer persona reviews, or uses GitHub API to post review comments directly in the PR.

### 8. PR Workflow Notification
- Assistant returns status updates and URLs to Discord when a PR is started, completed, or merged.
- Handle errors gracefully (auth, branch existence, bad code).

---

## Future/Stretch Goals

- Multi-developer personas (frontend/backend/devops experts)
- Code auto-format/lint
- Merge conflicts: human-in-the-loop for hard cases
- Slack and other chat integrations

---

_This roadmap is intentionally scoped, actionable, and precise. Each item can be developed and reviewed as its own ticket. Feel free to expand or break down as tasks evolve!_