# 🛠️ Project Gideon — Core TODOs for Discord Assistant

This document lists the actionable tasks required to implement Gideon's core Discord Assistant functionality. Each TODO is described in depth and broken into manageable development units for clear ticketing. Complete these items step-by-step for a robust, focused v1.

---

## 1. Discord Bot Setup & Channel Targeting

**Description:**  
- Set up the bot using `discord.py` (or your chosen Discord library).
- Read the target text channel ID from a `.env` environment file.
- The bot should only process messages from this configured channel.
- Add logging for startup and channel binding success/failure.

---

## 2. Bot Authentication and Permissions

**Description:**  
- Generate the bot’s Discord credentials and invite the bot to the desired server.
- Ensure permissions are granted: message reading, message sending, and event management.
- Add error messages for missing or insufficient permissions when starting.

---

## 3. Listen for @Mention and Extract User Queries [DONE]

**Description:**
- In the configured channel, listen to all messages.
- If a message contains “@<BOT_USERNAME>”, extract the relevant user query text.
- Strip extra whitespace, mentions, or formatting for clean input.
- Add basic logging for each received query.

---

## 4. Call OpenAI/ChatGPT and Format Replies

**Description:**  
- Send the extracted message content to the OpenAI/ChatGPT API for response generation.
- Sanitize the output (trim, prevent code injection, etc.).
- Send a reply in the Discord channel, directly under the triggering message.
- Handle cases where the completion fails or takes too long (display a helpful error or retry).

---

## 5. Event Scheduling from User Requests

**Description:**  
- Analyze incoming queries to detect event scheduling intent.
  - Example trigger phrases: “schedule a meeting…”, “plan a call…”, etc.
- Parse out the event participants, topic, date, and time from natural language.
- Use the Discord API to create a server event with all details.
- Tag mentioned users in the event or notification.
- Confirm event creation to the user, or reply with error details if parsing fails.
- Handle timezone ambiguity and clarify if necessary.

---

## 6. Environment Configuration & Validation

**Description:**  
- Ensure all settings (API keys, channel IDs, permissions) are validated at bot start.
- Add startup checks and descriptive error logs for missing config.

---

## 7. Basic Error Handling and Logging

**Description:**  
- Implement error logging for API failures, Discord API exceptions, and parsing errors.
- Log whenever the bot handles a query, schedules an event, or encounters an error.
- Consider preparing logs for future extensibility.

---

## 8. Helper Functions & Stubs for Extensibility

**Description:**  
- Modularize code: bot startup, message processing, OpenAI interaction, and event scheduling in separate functions/modules.
- Clearly comment stubs for possible future enhancements (e.g., broader event types, fallback LLMs).
- Document each function’s responsibilities for easier ramp-up.

---

Once these core TODOs are complete, you'll have a production-ready Discord assistant focused on answering queries and scheduling events in your chosen channel. 🚀