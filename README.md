<div align="center">

<img src="https://i.ibb.co/rKM4mfnx/x.jpg" width="60%" />

#  Ether Userbot System
**The Next-Gen Modular Telegram Framework**

![Stars](https://img.shields.io/github/stars/LearningBotsOfficial/Ether)
![Forks](https://img.shields.io/github/forks/LearningBotsOfficial/Ether)

[![License](https://img.shields.io/github/license/LearningBotsOfficial/Ether?style=for-the-badge&color=94a3b8)](LICENSE)

<p align="center">
  <b>Ether</b> is a high-performance, modular Telegram userbot architecture built with <b>Telethon</b> + <b>MongoDB</b>. Designed for developers who prioritize security, speed, and clean code.
</p>


---

</div>

##  Why Ether is Safe?

**Zero String Session Reliance**

Unlike traditional userbots that require risky "String Sessions" generated via third-party  bots, Ether utilizes a **native authentication flow**.

* **Self-Hosted Sovereignty:** Deploy on your own VPS. Your credentials never leave your environment.
* **Direct-to-Telegram Login:** Use the `/login` command to trigger an official Telegram OTP/2FA flow directly to your device.
* **Encrypted Local Storage:** Session data is stored securely on *your* server, not in a cloud database or a developer's logs.
* **No Middleware Risks:** No Replit, no Heroku logs, and no external session string generators.

---

##  Features

* ** Secure Auth:** Native login system (No String Session required)
* ** Hybrid Engine:** Leverages Telethon (Userbot) and Bot API simultaneously
* ** Privacy First:** Full 2FA support and local session management
* ** Plugin Architecture:** Easily drop new `.py` scripts into the `plugins/` folder
* ** There are many more features — visit the plugins folder or deploy to explore all.**

---

#  DEPLOYMENT GUIDES

<details>
<summary><b> DEPLOY TO HEROKU (RECOMMENDED)</b></summary>

---

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://dashboard.heroku.com/new?template=https://github.com/LearningBotsOfficial/Ether)

### - STEP 1: PRE-REQUISITES
- A Heroku Account.
- A MongoDB Connection String (from MongoDB Atlas).
- Telegram API_ID, API_HASH, and BOT_TOKEN.

### - STEP 2: DEPLOY
1. Click the **"Deploy to Heroku"** button above.
2. Fill in the required environment variables.
3. Click **"Deploy App"**.

### - STEP 3: ACTIVATE
1. Go to the **Resources** tab in Heroku.
2. Enable the **worker** dyno (turn the switch on).
3. Open your bot on Telegram and send `/login`.

---

</details>

<details>
<summary><b> DEPLOY TO JUSTRUNMY.APP</b></summary>

---

## - ABOUT
We’ve found a **free + fast hosting platform** for you to easily deploy your userbot.  
Follow all steps carefully.

---

## - STEP 1: DOWNLOAD THE PROJECT

1. First, **fork the repository**  
   Link :- https://github.com/LearningBotsOfficial/Ether  

2. Click on the **green "Code" button**  
3. Select **"Download ZIP"** and save it to your device  

---

## - STEP 2: UPLOAD ON HOSTING SITE

1. Go to: https://justrunmy.app/  
2. **Sign up / Login**  
3. Upload the **ZIP file** you downloaded  
4. Wait until the upload & setup process completes  

---

## - STEP 3: FILL REQUIRED DETAILS

You will be asked to enter the following:

```
API_ID=
API_HASH=
OWNER_ID=
BOT_TOKEN=
BOT_USERNAME=etheruserbot
SESSION_NAME=etheruserbot
SESSION_DIR=sessions
MONGO_URI=
DB_NAME=Ether

DEBUG=False
```

- Fill in your **own details** for API_ID, API_HASH, BOT_TOKEN, etc.  
- Keep default values as provided where already mentioned  

---

## - STEP 4: START YOUR BOT

1. Click on **Continue**  
2. Wait for deployment to complete  
3. Once done, your bot is live  

---

## - STEP 5: LOGIN & ACTIVATE

1. Open your bot  
2. Send: `/start`  
3. Then send: `/login`  
4. Complete login safely  

---

## - DONE

Your userbot is now running with **100% safety**  

Some steps are shown in the video — watch it for better understanding  

---

## - SUPPORT

If you face any issues, feel free to ask for help  

---

</details>

---

##  Configuration (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| API_ID | Your Telegram API ID |  Yes |
| API_HASH | Your Telegram API Hash |  Yes |
| BOT_TOKEN | Token from @BotFather |  Yes |
| OWNER_ID | Your numeric Telegram ID |  Yes |
| BOT_USERNAME | Your bot username (without @) |  Yes |
| MONGO_URI | MongoDB Connection String |  Yes |
| DB_NAME | Database name (default: Ether) |  No |
| SESSION_NAME | Session file name (default: etheruserbot) |  No |
| SESSION_DIR | Session directory (default: sessions) |  No |
| DEBUG | Enable debug mode (True/False) |  No |

---
---

##  Commands

<details>
<summary>  Click Here  </summary>

### Bot Commands (Prefix: /)

| Command | Description | Access |
|---------|-------------|--------|
| `/start` | Initialize the bot and view welcome message | All Users |
| `/login` | Securely authenticate your account via OTP/2FA | Admin Only |
| `/cancel` | Cancel ongoing login process | Admin Only |
| `/remove` | Delete current session file | Admin Only |

### Userbot Commands (Prefix: .)

| Command | Description | Example |
|---------|-------------|---------|
| `.ping` | Measure response latency | `.ping` |
| `.alive` | View system status and uptime | `.alive` |
| `.help` | Display help menu and available commands | `.help` |
| `.tagall` | Mention all members in a group | `.tagall` |
| `.fonts <text>` | Convert text to multiple font styles | `.fonts Hello` |

### Shortcut Commands

| Command | Description | Example |
|---------|-------------|---------|
| `.shortcut <name>` | Save a message as shortcut (reply to message) | `.shortcut my` |
| `.get <name>` | Retrieve and send a shortcut | `.get my` |
| `.delshortcut <name>` | Delete a saved shortcut | `.delshortcut my` |
| `.shortcuts` | List all saved shortcuts | `.shortcuts` |

### DM Protection Commands

| Command | Description | Example |
|---------|-------------|---------|
| `.allow` | Allow a user to DM you (reply to their message) | `.allow` |
| `.disallow` | Remove a user from allowed list | `.disallow` |
| `.setwelcome` | Set custom welcome message for DMs | `.setwelcome` |
| `.clearwelcome` | Clear custom welcome message | `.clearwelcome` |
| `.setwarn <n>` | Set max warnings before auto-block | `.setwarn 3` |

### DM Shield Commands

| Command | Description | Example |
|---------|-------------|---------|
| `.shield` | Display shield help menu | `.shield` |
| `.shield on` | Enable DM protection | `.shield on` |
| `.shield off` | Disable DM protection | `.shield off` |
| `.shield status` | Show current shield status | `.shield status` |
| `.shield link` | Toggle link filter | `.shield link` |
| `.shield user` | Toggle username filter | `.shield user` |
| `.shield allow` | Whitelist a user | `.shield allow` |
| `.shield disallow` | Remove user from whitelist | `.shield disallow` |
</details>
---

##  Project Structure

```
Ether/
├── assets/          # Static assets (logos, images)
├── auth/            # Authentication utilities
├── config/          # Configuration management
├── core/            # Core client and bot logic
│   ├── bot.py       # Bot API handlers and inline queries
│   ├── loader.py    # Plugin loader
│   └── user_client.py # Telethon client wrapper
├── database/        # Database schemas
├── logs/            # Log files
├── media/           # User-uploaded media (shortcuts, welcome)
├── plugins/         # Userbot command plugins
│   ├── alive.py
│   ├── dm.py
│   ├── dm_shield.py
│   ├── fonts.py
│   ├── help.py
│   ├── ping.py
│   ├── shortcut.py
│   └── tagall.py
├── services/        # Business logic services
├── sessions/        # Telegram session files
├── storage/         # Database connection (MongoDB)
├── utils/           # Helper utilities
├── .env             # Environment variables
├── main.py          # Entry point
└── requirements.txt # Python dependencies
```

---

##  Deployment

### Local Deployment
Follow the Quickstart guide above for local deployment.

### VPS Deployment (Ubuntu/Debian)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+ or higher (Tested on Python 3.12)
sudo apt install python3.9 python3-pip python3-venv -y

# Clone repository
git clone https://github.com/LearningBotsOfficial/Ether.git
cd Ether

# Create and activate virtual environment 
python3.9 -m venv venv  # or higher (Tested on Python 3.12)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure .env file
nano .env

# Run with screen/tmux for persistent sessions
screen -S ether
python main.py
# Press Ctrl+A then D to detach
```

---

##  Community & Support

<p align="center">
  <a href="https://t.me/Ether_Update">
    <img src="https://img.shields.io/badge/%20Ether%20Userbot-Official%20Channel-5865F2?style=for-the-badge&logo=telegram">
  </a>
  <a href="https://t.me/EtherSupport">
    <img src="https://img.shields.io/badge/%20Ether%20Support-Get%20Help-2ECC71?style=for-the-badge&logo=telegram">
  </a>
</p>

<p align="center">
  <a href="https://t.me/LearningBotsNetwork">
    <img src="https://img.shields.io/badge/%20Learning%20Bots-Updates%20%26%20Ecosystem-F39C12?style=for-the-badge&logo=telegram">
  </a>
</p>

---

##  License & Terms

Ether is open-source. By using this software, you agree to:

- **Retain Credits:** Keep original credits to LearningBotsOfficial
- **No Reselling:** Do not resell this software as a standalone product
- **Responsible Use:** Use in accordance with Telegram's Terms of Service
- **Attribution:** Proper attribution to Ether project when forking or reusing

---

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with  by [LearningBotsOfficial](https://github.com/LearningBotsOfficial)**

[ Back to Top](#-ether-userbot-system)

</div>
