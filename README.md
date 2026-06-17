<div align="center">

<hr>

<p>
  <strong>🌏 Language / 語言切換：</strong>
  <a href="doc/README.zh-tw.md">🇨🇳 中文版（繁體）</a> | 
  <a href="README.md">🇺🇸 English</a>
</p>

<hr>

<!-- 
  [開發者注意] 原本的 Giphy 連結是壞掉的，我暫時用 Emoji 和文字排版代替。
  如果您有喜歡的幽幽子 GIF，請將下方替換為：
  <img src="您的_GIF_連結.gif" alt="Yuyuko Sleeping" width="200">
-->
<h1>🌸 Yuyuko Bot 🌸</h1>
<p><em>"Zzz... Hm? You need something? Make it quick, I was dreaming about dango..."</em></p>

Hello, user! I'm **Shiroko** — the developer who keeps Yuyuko fed.  
Thank you for inviting her to your server. Please try not to wake her up unnecessarily.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Pycord](https://img.shields.io/badge/pycord-v2.x-5865F2.svg)](https://pypi.org/project/py-cord/)
[![License](https://img.shields.io/badge/License-GPL%20v3-green.svg)](./LICENSE)

</div>

---

## 💤 Current Status & Architecture

Yuyuko Bot is currently **fully modularized (Cogs)** and powered by an **enterprise-grade data architecture**.  
Basically, I reorganized her brain so she doesn't crash when she tries to think too hard about snacks.

### Why did we change this?

| Old Version 😫 | New Version 😌 | Why? |
| :--- | :--- | :--- |
| All commands in one messy file | **Separated Cogs** | Easier to find things when she loses them. |
| Direct JSON reads/writes everywhere | **`SakuraDataManager` (In-Memory)** | Lightning-fast reads, zero disk I/O blocking. |
| Data corruption during backups | **Dual-Lock & SQLite Auto-Backup** | Midnight backups won't delete your snacks. |
| Rigid jobs | **Main/Sub Jobs & Passives** | She can nap while we update features. |

### 🧠 Under the Hood (The Boring but Cool Stuff)
If you are a developer, here is what keeps her soul intact:
*   **`SakuraDataManager`**: All economy data is cached in memory. We use `balance_lock` for atomic memory operations and `save_lock` with `deepcopy` to ensure JSON files never get corrupted during writes.
*   **Midnight SQLite Backup**: An `auto_backup` event runs at 4:00 AM, snapshotting all data into SQLite. During this time, write-commands are elegantly intercepted to prevent data mismatch.
*   **Pycord Best Practices**: All Views have `NotFound` exception handling (so if a user deletes the message, the bot doesn't crash), and `display_avatar` is used everywhere to prevent `NoneType` errors.
*   **Golden Restart Rule**: `/restart` uses `subprocess.Popen` + `os._exit(0)` to ensure a 100% clean process replacement without leaving dead Gateway connections.

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
| `/user_info` | Check profile (🚨 **Auto-detects new accounts < 4 weeks!**) | `/user_info @user` |
| `/feedback` | Tell Shiroko something broke | `/feedback Help...` |
| `/quiz` | A mini-game (Prepare to be roasted elegantly) | `/quiz` |

### 💰 Economy (Snack Fund & Stamina)

> **Currency:** 👻 **Ghost Coins** (Not real money, but buys virtual snacks)  
> **System:** Working costs **Stamina**. Eat food from `/shop` or `/backpack` to recover!

| Command | Description | Usage |
| :--- | :--- | :--- |
| `/balance` | Check your poverty level | `/balance` |
| `/leaderboard` | Who has the most snacks? | `/leaderboard` |
| `/choose_job` | Pick a Main Job & Sub Job (Unlocks Passives!) | `/choose_job` |
| `/reset_job` | Quit your job (Lazy mode) | `/reset_job` |
| `/work` | Work for snacks (Costs Stamina! 1h cooldown) | `/work` |
| `/shop` | Buy food to recover Stamina | `/shop` |
| `/backpack` | What do you own? (Eat items here) | `/backpack` |
| `/server_bank` | Deposit, withdraw, or take a high-interest loan | `/server_bank` |
| `/credit` | Check your loan credit score (Don't let it hit 0!) | `/credit` |
| `/pay` | Give money to someone | `/pay @user 100` |

### 🔨 Admin (Don't Abuse)

> **⚠️ Warning:** Yuyuko's role must be **highest**, or she won't listen.

| Command | Description | Usage |
| :--- | :--- | :--- |
| `/ban` | Banish a user (Supports Hackban via User ID) | `/ban @user [reason]` |
| `/kick` | Kick a user out | `/kick @user` |
| `/clear` | Clean up chat spam (Yomu's job!) | `/clear 50` |
| `/start_giveaway` | Give away free stuff (Auto-draws on timeout) | `/start_giveaway Prize` |
| `/timeout` | Shut someone up (Mute) | `/timeout @user 10` |
| `/untimeout` | Let them speak again | `/untimeout @user` |
| `/tax` | **["Speaking Tax!"](https://youtu.be/QmYVLAUwj9E?si=SBOMdRbBzqOqR6Hr&t=27)** (Progressive tax rates) | `/tax` |

### 🎣 Fishing (Is there food?)

> **Passives:** Fisher (Main) boosts rare catches. Angler (Sub) has a 30% "Empty-handed" rate but finds big treasures.

| Command | Description | Usage |
| :--- | :--- | :--- |
| `/fish` | Try to catch something (Immersive job scenarios!) | `/fish` |
| `/fish_back` | Show your catch (Sorted by rarity) | `/fish_back` |
| `/fish_shop` | Sell the trash... I mean, treasure | `/fish_shop` |
| `/fish_rates` | Check the exact fishing odds | `/fish_rates` |

### 🎲 Gambling (Risk it for snacks)

> **Passive:** Gambler (Main) bets 3x the amount. Win = 6x payout. Lose = Lose 3x.

| Command | Description | Usage |
| :--- | :--- | :--- |
| `/blackjack` | Play 21-point against Yuyuko | `/blackjack 100` |
| `/blackjack_pvp` | PVP 21-point against other souls | `/blackjack_pvp @user 100` |

### 🔒 Developer Only (Secrets)

> 🚫 **Normal humans cannot access these.**

| Command | Description | Usage |
| :--- | :--- | :--- |
| `/shutdown` | Put Yuyuko to sleep (Graceful Gateway close) | `/shutdown` |
| `/restart` | Wake her up again (100% clean process restart) | `/restart` |
| `/addmoney` | Cheat money (Shh...) | `/addmoney @user 500` |
| `/removemoney` | Take money away | `/removemoney @user 50` |

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
