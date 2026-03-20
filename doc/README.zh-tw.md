<div align="center">

<hr>

<p>
  <strong>🌏 語言切換 / Language:</strong>
  <a href="../README.md">🇺🇸 English</a> | 
  <a href="README.zh-tw.md">🇨🇳 中文版（繁體）</a>
</p>

<hr>

<img src="https://media.giphy.com/media/v1.Y2lkY2E0ZmJmZGJkYi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFiY2RlZi9jY2RlZmFi......" alt="Yuyuko Sleeping" width="150">
<!-- 建議替換為實際的幽幽子睡覺或吃糰子 GIF -->

# 🌸 幽幽子 Bot (Yuyuko Bot)

> *"哈～你來啦？別吵...我正在 dreaming about dango..."*

你好，使用者！我是 **Shiroko** —— 負責照顧這位大小姐飲食起居的開發者。  
感謝你把我們接回家，記得準時餵食...啊不是，是維護。

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Pycord](https://img.shields.io/badge/Pycord-v2.0+-5865F2.svg)](https://pypi.org/project/pycord/)
[![License](https://img.shields.io/badge/License-GPL%20v3-green.svg)](../LICENSE)

</div>

---

## 💤 現有狀態

目前的 **Yuyuko Bot** 採用 **全模組化 (Cog)** 架構。  
簡單來說，我把她的大腦分成了好幾塊，這樣她就不用一次動太多腦筋，比較不會當機。

### 與前一版本的差異

| 舊版本 😫 | 現版本 😌 | 補充說明 |
| :--- | :--- | :--- |
| 所有指令擠在單一檔案 | **全模組化 (Cog)** | 每個功能獨立，方便開發、維護，Shiroko 比較不會崩潰。 |
| 維護與擴充困難 | **易於維護且具延展性** | 新增功能只需編輯對應模組，不會吵醒其他部分。 |
| 指令與核心程式碼耦合度高 | **指令獨立分離** | 降低耦合、提升可讀性，除錯比較直觀。 |
| 彈性有限 | **高度彈性，便於未來拓展** | 支援動態載入，未來要增添功能更輕鬆（讓她多睡會兒）。 |

> - **全模組化 (Cog)：** 每個主要功能獨立檔案，方便增減功能。
> - **易於維護與擴展：** 增減功能不會影響其他部分，開發流程更乾淨安全。
> - **指令獨立分離：** 降低出錯風險，維護、除錯更直觀。
> - **高度彈性未來拓展：** 支援動態載入、快速擴充新功能。

---

## 📜 指令列表

### 🍵 一般指令 (礼貌问候)

| 指令 | 說明 | 用法範例 |
| :--- | :--- | :--- |
| `/about-bot` | 關於 Yuyuko 的資訊 (她餓了) | `/about-bot` |
| `/invite` | 生成 Yuyuko 的邀請連結 | `/invite` |
| `/time` | 查看 Yuyuko 已閒置多久 (偷懶時間) | `/time` |
| `/ping` | 查看 Yuyuko 與現世的延遲 (有沒有睡醒) | `/ping` |
| `/server_info` | 查看伺服器資訊 | `/server_info` |
| `/user_info` | 查看用戶個人資料資訊 | `/user_info @對象` |
| `/feedback` | 回報問題給 Shiroko 修復 | `/feedback 你的建議或回報內容` |
| `/quiz` | 快問快答小遊戲 (如果她有興趣) | `/quiz` |

### 💰 經濟系統 (零食基金)

> **注意：** 貨幣單位為 **👻 幽靈幣**，不與其他機器人共享，但可以買虛擬零食。

| 指令 | 說明 | 用法範例 |
| :--- | :--- | :--- |
| `/balance` | 查看當前餘額 (看看你窮成什麼樣) | `/balance` |
| `/leaderboard` | 查看最富有玩家與稅收排行榜 | `/leaderboard` |
| `/choose_job` | 選擇一份工作賺錢 (點擊 UI 選擇) | `/choose_job` |
| `/reset_job` | 重置職業選擇 (不想幹了) | `/reset_job` |
| `/work` | 執行工作 (冷卻時間：60 秒，好累...) | `/work` |
| `/shop` | 造訪商店購買解壓用品 | `/shop` |
| `/backpack` | 查看物品欄 | `/backpack` |
| `/server_bank` | 查看 Yuyuko 的虛擬銀行 (私人金庫) | `/server_bank` |
| `/pay` | 轉帳給其他玩家 | `/pay @對象 100` |

### 🔨 管理員指令 (別濫用)

> **⚠️ 警告：** Yuyuko 的角色必須位於角色列表最上方，否則她不會聽話。

| 指令 | 說明 | 用法範例 |
| :--- | :--- | :--- |
| `/ban` | 封禁使用者 (驅逐出境) | `/ban @對象 [理由]` |
| `/kick` | 踢出使用者 | `/kick @對象` |
| `/start_giveaway` | 開始抽獎 (散發零食) | `/start_giveaway Switch` |
| `/timeout` | 禁言使用者 (安靜一點) | `/timeout @對象 10` |
| `/untimeout` | 解除禁言 (可以說話了) | `/untimeout @對象` |
| `/tax` | **[「我宣布徵收說話稅！」](https://youtu.be/QmYVLAUwj9E?si=SBOMdRbBzqOqR6Hr&t=27)**  | `/tax` |

### 🎣 釣魚系統 (有吃的嗎？)

| 指令 | 說明 | 用法範例 |
| :--- | :--- | :--- |
| `/fish` | 開始釣魚 (可能釣到垃圾…) | `/fish` |
| `/fish_back` | 查看或展示漁獲物品欄 | `/fish_back` |
| `/fish_shop` | 出售漁獲 (把垃圾換成錢) | `/fish_shop` |

### 🎲 賭博 (為了零食冒險)

| 指令 | 說明 | 用法範例 |
| :--- | :--- | :--- |
| `/blackjack` | 玩 21 點 (特殊職業獲得 **2 倍獎勵**！) | `/blackjack 100` |

### 🔒 開發者專用指令 (秘密)

> 🚫 **一般使用者與管理員不可使用，這是 Shiroko 的後門。**

| 指令 | 說明 | 用法範例 |
| :--- | :--- | :--- |
| `/shutdown` | 讓 Yuyuko 關機休息 (去睡覺) | `/shutdown` |
| `/restart` | 重啟機器人 (叫醒她) | `/restart` |
| `/addmoney` | 增加使用者金錢 (作弊...) | `/addmoney @對象 500` |
| `/removemoney` | 移除使用者金錢 (沒收) | `/removemoney @對象 50` |
| `/join` | 讓 Yuyuko 加入語音頻道 | `/join` |
| `/leave` | 讓 Yuyuko 離開語音頻道 | `/leave` |

---

## 📄 授權條款

本專案採用 [**GNU 通用公共授權條款 第三版 (GPL v3.0)**](../LICENSE) 授權。  
*請不要偷走她的零食。*

<div align="center">

<hr>

<p>
  <em>製作：Shiroko | 監修：幽幽子 (正在睡覺) 💤</em>
</p>

</div>
