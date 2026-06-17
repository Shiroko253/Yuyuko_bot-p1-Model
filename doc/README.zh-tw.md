<div align="center">

<hr>

<p>
  <strong>🌏 語言切換 / Language:</strong>
  <a href="../README.md">🇺🇸 English</a> | 
  <a href="README.zh-tw.md">🇨🇳 中文版（繁體）</a>
</p>

<hr>

<!-- 
  [開發者注意] 原本的 Giphy 連結是壞掉的，我暫時用 Emoji 和文字排版代替。
  如果您有喜歡的幽幽子 GIF，請將下方替換為：
  <img src="您的_GIF_連結.gif" alt="Yuyuko Sleeping" width="200">
-->
<h1>🌸 幽幽子 Bot (Yuyuko Bot) 🌸</h1>
<p><em>「哈～你來啦？別吵...我正在 dreaming about dango...」</em></p>

你好，使用者！我是 **Shiroko** —— 負責照顧這位大小姐飲食起居的開發者。  
感謝你把我們接回家，記得準時餵食...啊不是，是維護。

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Pycord](https://img.shields.io/badge/Pycord-v2.x-5865F2.svg)](https://pypi.org/project/py-cord/)
[![License](https://img.shields.io/badge/License-GPL%20v3-green.svg)](../LICENSE)

</div>

---

# 📚 官方設定圖鑑

想要深入了解幽幽子 Bot 的各種系統嗎？請查閱以下官方文檔，讓你從萌新變成冥界老手！

<div align="center">

| 📖 文檔名稱 | 📝 內容說明 | 🔗 快速跳轉 |
| :--- | :--- | :---: |
| 💼 **冥界職業指南** | 正副職系統、薪資範圍、體力消耗、三大被動技能詳解、互斥機制 | [👉 前往查閱](jobs.md) |
| 🎣 **櫻花湖釣魚圖鑑** | 釣魚情境、機率分布、100+ 種漁獲完整圖鑑、漁夫/釣魚佬被動加成 | [👉 前往查閱](fish.md) |
| 🍡 **冥界商店指南** | 體力系統、39 種商品完整列表、含稅價格與性價比分析、東方聯名餐點 | [👉 前往查閱](shop_item.md) |

</div>

> 💡 **Shiroko 的閱讀建議**：
> 如果你是第一次接觸幽幽子 Bot，建議先閱讀 **《冥界職業指南》** 選擇一個適合你的職業，
> 然後透過 **《冥界商店指南》** 了解如何恢復體力，最後在 **《櫻花湖釣魚圖鑑》** 中挑戰傳說級巨物！

---

## 💤 現有狀態與底層架構

目前的 **Yuyuko Bot** 採用 **全模組化 (Cog)** 架構，並搭載了**企業級的數據管理系統**。  
簡單來說，我把她的大腦分成了好幾塊，並加裝了各種安全鎖，這樣她就不用一次動太多腦筋，也比較不會在吃零食時當機。

### 與前一版本的差異

| 舊版本 😫 | 現版本 😌 | 補充說明 |
| :--- | :--- | :--- |
| 所有指令擠在單一檔案 | **全模組化 (Cog)** | 每個功能獨立，方便開發、維護，Shiroko 比較不會崩潰。 |
| 到處直接讀寫 JSON 硬碟 | **`SakuraDataManager` (記憶體快取)** | 閃電般的讀取速度，零硬碟 I/O 阻塞。 |
| 備份時容易導致數據損壞 | **雙重鎖保護 & SQLite 自動備份** | 凌晨的備份絕對不會偷偷吃掉你的零食。 |
| 死板的職業設定 | **正副職系統 & 專屬被動** | 她可以在睡覺時順便升級功能。 |

### 🧠 底層技術 (給開發者看的無聊但很酷的東西)
如果你也是開發者，以下是維持她靈魂不散的關鍵技術：
*   **`SakuraDataManager`**：所有經濟數據皆快取於記憶體中。我們使用 `balance_lock` 確保記憶體操作的原子性，並搭配 `save_lock` 與 `deepcopy` 確保寫入 JSON 時檔案絕對不會損壞。
*   **凌晨 SQLite 備份**：`auto_backup` 事件會在凌晨 4:00 自動將所有數據快照備份至 SQLite。備份期間，寫入型指令會被優雅地攔截，防止數據不一致。
*   **Pycord 最佳實踐**：所有 View 都加入了 `NotFound` 異常處理（所以如果使用者刪除了訊息，Bot 不會噴紅字崩潰），並全面使用 `display_avatar` 防止 `NoneType` 錯誤。
*   **黃金重啟法則**：`/restart` 指令使用 `subprocess.Popen` 啟動乾淨新進程，並搭配 `os._exit(0)` 瞬間終止舊進程，確保 100% 成功重啟且釋放所有 Gateway 連線與檔案鎖。

---

## 📜 指令列表

### 🍵 一般指令 (禮貌問候)

| 指令 | 說明 | 用法範例 |
| :--- | :--- | :--- |
| `/about-bot` | 關於 Yuyuko 的資訊 (她餓了) | `/about-bot` |
| `/invite` | 生成 Yuyuko 的邀請連結 | `/invite` |
| `/time` | 查看 Yuyuko 已閒置多久 (偷懶時間) | `/time` |
| `/ping` | 查看 Yuyuko 與現世的延遲 (有沒有睡醒) | `/ping` |
| `/server_info` | 查看伺服器詳細資訊 | `/server_info` |
| `/user_info` | 查看用戶資料 (🚨 **自動偵測 < 4 週的新帳號！**) | `/user_info @對象` |
| `/feedback` | 回報問題給 Shiroko 修復 | `/feedback 你的建議或回報內容` |
| `/quiz` | 快問快答小遊戲 (準備好被優雅地嘲諷吧) | `/quiz` |

### 💰 經濟系統 (零食基金與體力)

> **貨幣：** 👻 **幽靈幣** (不與其他機器人共享，但可以買虛擬零食)  
> **系統：** 工作會消耗 **體力 (Stamina)**。體力不足時，請去 `/shop` 買食物或從 `/backpack` 吃東西恢復！

| 指令 | 說明 | 用法範例 |
| :--- | :--- | :--- |
| `/balance` | 查看當前餘額 (看看你窮成什麼樣) | `/balance` |
| `/leaderboard` | 查看最富有玩家與稅收排行榜 | `/leaderboard` |
| `/choose_job` | 選擇正職與副職 (解鎖專屬被動！) | `/choose_job` |
| `/reset_job` | 重置職業選擇 (不想幹了) | `/reset_job` |
| `/work` | 執行工作賺取零食 (消耗體力！1小時冷卻) | `/work` |
| `/shop` | 造訪商店購買食物以恢復體力 | `/shop` |
| `/backpack` | 查看物品欄 (可以在這裡吃東西) | `/backpack` |
| `/server_bank` | 存錢、提款，或借高利貸 (注意信譽！) | `/server_bank` |
| `/credit` | 查看你的借貸信譽分數 (別讓它歸零！) | `/credit` |
| `/pay` | 轉帳給其他玩家 | `/pay @對象 100` |

### 🔨 管理員指令 (別濫用)

> **⚠️ 警告：** Yuyuko 的角色必須位於角色列表最上方，否則她不會聽話。

| 指令 | 說明 | 用法範例 |
| :--- | :--- | :--- |
| `/ban` | 封禁使用者 (支援透過 User ID 進行 Hackban) | `/ban @對象 [理由]` |
| `/kick` | 踢出使用者 | `/kick @對象` |
| `/clear` | 清掃聊天室垃圾訊息 (妖夢的工作！) | `/clear 50` |
| `/start_giveaway` | 開始抽獎 (超時自動開獎) | `/start_giveaway Switch` |
| `/timeout` | 禁言使用者 (安靜一點) | `/timeout @對象 10` |
| `/untimeout` | 解除禁言 (可以說話了) | `/untimeout @對象` |
| `/tax` | **[「我宣布徵收說話稅！」](https://youtu.be/QmYVLAUwj9E?si=SBOMdRbBzqOqR6Hr&t=27)** (累進稅率) | `/tax` |

### 🎣 釣魚系統 (有吃的嗎？)

> **被動機制：** 漁夫 (正職) 會大幅提高稀有漁獲機率。釣魚佬 (副職) 有 30% 機率空軍，但能釣到大寶藏。

| 指令 | 說明 | 用法範例 |
| :--- | :--- | :--- |
| `/fish` | 開始釣魚 (充滿沉浸感的職業情境！) | `/fish` |
| `/fish_back` | 查看漁獲背包 (按稀有度排序) | `/fish_back` |
| `/fish_shop` | 出售漁獲 (把垃圾換成錢) | `/fish_shop` |
| `/fish_rates` | 查看精確的釣魚機率分布 | `/fish_rates` |

### 🎲 賭博 (為了零食冒險)

> **被動機制：** 賭徒 (正職) 實際下注金額 x3。勝利可獲得 x6 返還，失敗則失去 x3 本金。

| 指令 | 說明 | 用法範例 |
| :--- | :--- | :--- |
| `/blackjack` | 與 Yuyuko 玩 21 點 | `/blackjack 100` |
| `/blackjack_pvp` | 與其他靈魂進行 PVP 21 點對決 | `/blackjack_pvp @對象 100` |

### 🔒 開發者專用指令 (秘密)

> 🚫 **一般使用者與管理員不可使用，這是 Shiroko 的後門。**

| 指令 | 說明 | 用法範例 |
| :--- | :--- | :--- |
| `/shutdown` | 讓 Yuyuko 關機休息 (優雅斷開 Gateway) | `/shutdown` |
| `/restart` | 重啟機器人 (100% 乾淨進程重啟) | `/restart` |
| `/addmoney` | 增加使用者金錢 (作弊...) | `/addmoney @對象 500` |
| `/removemoney` | 移除使用者金錢 (沒收) | `/removemoney @對象 50` |

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
