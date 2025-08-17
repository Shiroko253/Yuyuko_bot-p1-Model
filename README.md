# Welcome to Yuyuko Bot

[🇨🇳 中文版本](Doc/README.zh-tw.md)

Hello, user! I’m **Shiroko** — the developer of Yuyuko Bot.

Thank you for using my Discord bot, I truly appreciate your support!

---

## Important Notice

**Unauthorized copying or code theft is strictly prohibited.**
All translations and documentation belong to the original developer and translators.
If you wish to redistribute, please keep the full source and license information intact without modification or concealment.

---

---

## Current Features

The current version of **Yuyuko Bot** is fully **modularized with Cogs**,
which allows for easier maintenance and future expansion.

### Differences from the Previous Version

| Previous Version                          | Current Version                             |
| ----------------------------------------- | ------------------------------------------- |
| All `@bot.slash_command` in a single file | Fully modularized with **Cogs**             |
| Hard to maintain and expand               | Easy maintenance and scalable design        |
| Commands tightly coupled with core code   | Commands separated into independent modules |
| Limited flexibility                       | Highly flexible and future-proof            |

---

## Command List

### General Commands

| Command        | Description                                  |
| -------------- | -------------------------------------------- |
| `/about-bot`   | Information about Yuyuko                     |
| `/invite`      | Generate Yuyuko’s invitation link            |
| `/time`        | Check how long Yuyuko has been idle          |
| `/ping`        | Check Yuyuko’s latency with the real world   |
| `/server_info` | View server information                      |
| `/user_info`   | View user profile information                |
| `/feedback`    | Report issues to Yuyuko for developer fixing |
| `/quiz`        | Quick quiz mini-game                         |

### Economy System

> **Note:** Currency unit = **Ghost Coins**, not shared with other bots.

| Command        | Description                                           |
| -------------- | ----------------------------------------------------- |
| `/balance`     | View current balance                                  |
| `/leaderboard` | View richest players & tax leaderboard                |
| `/choose_job`  | Choose a job to earn money (special jobs cannot work) |
| `/reset_job`   | Reset your chosen job                                 |
| `/work`        | Perform your job (cooldown: 60s)                      |
| `/shop`        | Visit the shop to buy stress-relief items             |
| `/backpack`    | View your inventory                                   |
| `/server_bank` | View Yuyuko’s virtual bank                            |
| `/pay`         | Transfer money to another player                      |

### Admin Commands

> **Note:** Yuyuko’s role must be at the top of the role list to use these.

| Command           | Description           |
| ----------------- | --------------------- |
| `/ban`            | Ban a user            |
| `/kick`           | Kick a user           |
| `/start_giveaway` | Start a giveaway      |
| `/timeout`        | Timeout a user (mute) |
| `/untimeout`      | Remove timeout        |

### Fishing

| Command      | Description                            |
| ------------ | -------------------------------------- |
| `/fish`      | Start fishing (you might catch trash…) |
| `/fish_back` | View or display your fishing inventory |
| `/fish_shop` | Sell your catches                      |

### Gambling

| Command      | Description                                       |
| ------------ | ------------------------------------------------- |
| `/blackjack` | Play Blackjack (special jobs get **2x rewards**!) |

### Developer-Only Commands

> These are not available for normal users or admins.

| Command        | Description                        |
| -------------- | ---------------------------------- |
| `/shutdown`    | Shut down Yuyuko                   |
| `/restart`     | Restart the bot                    |
| `/addmoney`    | Add money to a user                |
| `/removemoney` | Remove money from a user           |
| `/tax`         | “I hereby declare a speaking tax!” |
| `/join`        | Let Yuyuko join a voice channel    |
| `/leave`       | Let Yuyuko leave a voice channel   |

---

## License

**GNU General Public License v3.0 (GPL v3.0)**
