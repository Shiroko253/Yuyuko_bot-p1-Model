<div align="center">

<hr>

<p>
  <strong>🌏 Language / 語言切換：</strong>
  <a href="doc/README.zh-tw.md">🇨🇳 中文版（繁體）</a> | 
  <a href="README.md">🇺🇸 English</a>
</p>

<hr>

</div>

# Welcome to Yuyuko Bot

Hello, user! I’m **Shiroko** — the developer of Yuyuko Bot.

Thank you for using my Discord bot, I truly appreciate your support!

---

## Current Features

The current version of **Yuyuko Bot** is fully **modularized with Cogs**,  
which allows for easier maintenance and future expansion.

### Differences from the Previous Version

| Previous Version                                 | Current Version                                   | Explanation                                                                                  |
| ------------------------------------------------ | ------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| All `@bot.slash_command` in a single file        | Fully modularized with **Cogs**                   | Each command is separated into its own module, making development and management much easier. |
| Hard to maintain and expand                      | Easy maintenance and scalable design              | You can add, remove, or update features without affecting other parts of the bot.             |
| Commands tightly coupled with core code          | Commands separated into independent modules       | Reduces code coupling and improves code readability.                                         |
| Limited flexibility                             | Highly flexible and future-proof                  | Supports hot-reloading modules and seamless future upgrades.                                 |

> - **Modularization (Cogs):** Each main function/command is in its own file, making it easy to add or remove functionality.
> - **Easy maintenance and scalability:** Add or remove features anytime without breaking other parts.
> - **Independent command modules:** Commands are separated, making development and troubleshooting clearer.
> - **Future-proof:** Supports dynamic loading/unloading/reloading, so new features can be added easily.

---

## Command List

### General Commands

| Command        | Description                                  | Usage Example             |
| -------------- | -------------------------------------------- | ------------------------- |
| `/about-bot`   | Information about Yuyuko                     | `/about-bot`              |
| `/invite`      | Generate Yuyuko’s invitation link            | `/invite`                 |
| `/time`        | Check how long Yuyuko has been idle          | `/time`                   |
| `/ping`        | Check Yuyuko’s latency with the real world   | `/ping`                   |
| `/server_info` | View server information                      | `/server_info`            |
| `/user_info`   | View user profile information                | `/user_info @user`        |
| `/feedback`    | Report issues to Yuyuko for developer fixing | `/feedback Something...`  |
| `/quiz`        | Quick quiz mini-game                         | `/quiz`                   |

### Economy System

> **Note:** Currency unit = **Ghost Coins**, not shared with other bots.

| Command        | Description                                            | Usage Example                |
| -------------- | ------------------------------------------------------ | ---------------------------- |
| `/balance`     | View current balance                                   | `/balance`                   |
| `/leaderboard` | View richest players & tax leaderboard                 | `/leaderboard`               |
| `/choose_job`  | Choose a job to earn money (select from UI, not manual input)  | `/choose_job` (select via UI) |
| `/reset_job`   | Reset your chosen job                                  | `/reset_job`                 |
| `/work`        | Perform your job (cooldown: 60s)                       | `/work`                      |
| `/shop`        | Visit the shop to buy stress-relief items              | `/shop`                      |
| `/backpack`    | View your inventory                                    | `/backpack`                  |
| `/server_bank` | View Yuyuko’s virtual bank                             | `/server_bank`               |
| `/pay`         | Transfer money to another player                       | `/pay @user 100`             |

### Admin Commands

> **Note:** Yuyuko’s role must be at the top of the role list to use these.

| Command           | Description           | Usage Example          |
| ----------------- | --------------------- | ---------------------- |
| `/ban`            | Ban a user            | `/ban @user [reason]`  |
| `/kick`           | Kick a user           | `/kick @user`          |
| `/start_giveaway` | Start a giveaway      | `/start_giveaway Prize`|
| `/timeout`        | Timeout a user (mute) | `/timeout @user 10`    |
| `/untimeout`      | Remove timeout        | `/untimeout @user`     |

### Fishing

| Command      | Description                            | Usage Example      |
| ------------ | -------------------------------------- | ------------------ |
| `/fish`      | Start fishing (you might catch trash…) | `/fish`            |
| `/fish_back` | View or display your fishing inventory | `/fish_back`       |
| `/fish_shop` | Sell your catches                      | `/fish_shop`       |

### Gambling

| Command      | Description                                       | Usage Example        |
| ------------ | ------------------------------------------------- | -------------------- |
| `/blackjack` | Play Blackjack (special jobs get **2x rewards**!) | `/blackjack 100`     |

### Developer-Only Commands

> These are not available for normal users or admins.

| Command        | Description                        | Usage Example          |
| -------------- | ---------------------------------- | ---------------------- |
| `/shutdown`    | Shut down Yuyuko                   | `/shutdown`            |
| `/restart`     | Restart the bot                    | `/restart`             |
| `/addmoney`    | Add money to a user                | `/addmoney @user 500`  |
| `/removemoney` | Remove money from a user           | `/removemoney @user 50`|
| `/tax`         | “I hereby declare a speaking tax!” | `/tax`                 |
| `/join`        | Let Yuyuko join a voice channel    | `/join`                |
| `/leave`       | Let Yuyuko leave a voice channel   | `/leave`               |

---

## License

[**GNU General Public License v3.0 (GPL v3.0)**](./LICENSE)
