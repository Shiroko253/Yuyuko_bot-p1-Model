<div align="center">

<hr>

<p>
  <strong>🌏 Language / 語言切換：</strong>
  <a href="doc/README.zh-tw.md">🇨🇳 中文版（繁體）</a> | 
  <a href="README.md">🇺🇸 English</a>
</p>

<hr>

<img src="https://media.giphy.com/media/v1.Y2lkY2E0ZmJmZGJkYi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2......" alt="Yuyuko Sleeping" width="150">
<!-- 建議替换為實際的幽幽子睡覺或吃糰子 GIF -->

# 🌸 Yuyuko Bot

> *"Zzz... Hm? You need something? Make it quick, I was dreaming about dango..."*

Hello, user! I'm **Shiroko** — the developer who keeps Yuyuko fed.  
Thank you for inviting her to your server. Please try not to wake her up unnecessarily.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Pycord](https://img.shields.io/badge/Pycord-v2.7.1-5865F2.svg)](https://pypi.org/project/pycord/)
[![License](https://img.shields.io/badge/License-GPL%20v3-green.svg)](./LICENSE)

</div>

---

## 💤 Current Status

Yuyuko Bot is currently **fully modularized (Cogs)**.  
Basically, I organized her brain so she doesn't crash when she tries to think too hard.

### Why did we change this?

| Old Version 😫 | New Version 😌 | Why? |
| :--- | :--- | :--- |
| All commands in one messy file | **Separated Cogs** | Easier to find things when she loses them. |
| Hard to fix bugs | **Easy Maintenance** | Less headache for Shiroko. |
| Tightly coupled code | **Independent Modules** | If fishing breaks, gambling still works. |
| Rigid | **Flexible** | She can nap while we update features. |

> **Note:** This means less downtime for Yuyuko to sleep... I mean, to maintain.

---

## 📜 Command List

### 🍵 General (Polite Greetings)

| Command | Description | Usage |
| :--- | :--- | :--- |
| `/about-bot` | Who is Yuyuko? (She's hungry) | `/about-bot` |
| `/invite` | Get an invite link | `/invite` |
| `/time` | How long has she been idle? | `/time` |
| `/ping` | Check if she's awake or lagging | `/ping` |
| `/server_info` | Server details | `/server_info` |
| `/user_info` | Check your profile | `/user_info @user` |
| `/feedback` | Tell Shiroko something broke | `/feedback Help...` |
| `/quiz` | A mini-game (if she cares) | `/quiz` |

### 💰 Economy (Snack Fund)

> **Currency:** 👻 **Ghost Coins** (Not real money, but buys virtual snacks)

| Command | Description | Usage |
| :--- | :--- | :--- |
| `/balance` | Check your poverty level | `/balance` |
| `/leaderboard` | Who has the most snacks? | `/leaderboard` |
| `/choose_job` | Pick a job (UI Selection) | `/choose_job` |
| `/reset_job` | Quit your job (Lazy mode) | `/reset_job` |
| `/work` | Work for 60s cooldown (So tired...) | `/work` |
| `/shop` | Buy stress-relief items | `/shop` |
| `/backpack` | What do you own? | `/backpack` |
| `/server_bank` | Yuyuko's personal vault | `/server_bank` |
| `/pay` | Give money to someone | `/pay @user 100` |

### 🔨 Admin (Don't Abuse)

> **⚠️ Warning:** Yuyuko's role must be **highest**, or she won't listen.

| Command | Description | Usage |
| :--- | :--- | :--- |
| `/ban` | Banish a user | `/ban @user [reason]` |
| `/kick` | Kick a user out | `/kick @user` |
| `/start_giveaway` | Give away free stuff | `/start_giveaway Prize` |
| `/timeout` | Shut someone up (Mute) | `/timeout @user 10` |
| `/untimeout` | Let them speak again | `/untimeout @user` |
| `/tax` | **["Speaking Tax!"](https://youtu.be/QmYVLAUwj9E?si=SBOMdRbBzqOqR6Hr&t=27)**  | `/tax` |

### 🎣 Fishing (Is there food?)

| Command | Description | Usage |
| :--- | :--- | :--- |
| `/fish` | Try to catch something (maybe trash) | `/fish` |
| `/fish_back` | Show your catch | `/fish_back` |
| `/fish_shop` | Sell the trash... I mean, treasure | `/fish_shop` |

### 🎲 Gambling (Risk it for snacks)

| Command | Description | Usage |
| :--- | :--- | :--- |
| `/blackjack` | Play cards (**2x rewards** for special jobs!) | `/blackjack 100` |

### 🔒 Developer Only (Secrets)

> 🚫 **Normal humans cannot access these.**

| Command | Description | Usage |
| :--- | :--- | :--- |
| `/shutdown` | Put Yuyuko to sleep | `/shutdown` |
| `/restart` | Wake her up again | `/restart` |
| `/addmoney` | Cheat money (Shh...) | `/addmoney @user 500` |
| `/removemoney` | Take money away | `/removemoney @user 50` |
| `/join` | Join voice channel | `/join` |
| `/leave` | Leave voice channel | `/leave` |

---

## 📄 License

This project is licensed under the [**GNU General Public License v3.0**](./LICENSE).  
*Please don't steal her snacks.*

<div align="center">

<hr>

<p>
  <em>Made with 💤 and 🍡 by Shiroko</em>
</p>

</div>
