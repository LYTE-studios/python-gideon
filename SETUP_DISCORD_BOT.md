# 🛠️ Discord Developer Portal Bot Setup Guide

Follow these steps to configure your Discord bot and connect it to your server.

---

## 1. Create a New Application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **"New Application"**.  
   - Give it a descriptive name, e.g. `gideon-assistant`.
   - Click **"Create"**.

---

## 2. Add a Bot User

1. In your Application page, select the **"Bot"** tab on the sidebar.
2. Click **"Add Bot"** and confirm.
3. (Optional) Set your bot icon and display name.

---

## 3. Copy the Bot Token

1. On the Bot page, click **"Reset Token"** or **"Copy Token"**.
2. This is your secret `DISCORD_BOT_TOKEN` for the `.env` file.  
   **Keep it private!**

---

## 4. Set Bot Permissions

1. Still in the Bot settings:
    - Under **"Privileged Gateway Intents"**, enable **"Message Content Intent"**.
2. Under **"OAuth2" > "URL Generator"**:
    - Scopes: check **"bot"**.
    - Bot Permissions: check  
      - **"Send Messages"**
      - **"Read Messages/View Channels"**
      - **"Manage Events"** (for event scheduling)
3. Copy the generated OAuth2 **invite URL**.

---

## 5. Invite the Bot to Your Server

1. Open the OAuth2 invite URL in your browser.
2. Select your server and "Authorize".

---

## 6. Get the Channel ID

1. In Discord, go to your desired text channel.
2. Right-click the channel and hit **"Copy Channel ID"**  
   _(Enable Developer Mode in Discord User Settings > Advanced for this option)_

3. Paste this ID in your `.env` as `DISCORD_CHANNEL_ID`.

---

You’re ready to run your containerized bot!  
See the main README or PLANNING.md for next steps.