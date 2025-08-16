# 導入所需的模組：sqlite3 用於資料庫操作，os 用於處理檔案路徑
import sqlite3
import os

# 定義資料庫檔案的路徑（硬編碼為 example.db）
DB_PATH = "example.db"

# 顯示資料庫檔案的絕對路徑，方便調試
print(f"資料庫路徑: {os.path.abspath(DB_PATH)}")

# 初始化資料庫，建立 BackgroundInfo 表（如果不存在）
def init_db():
    """
    初始化資料庫，建立包含 id、user_id 和 info 的 BackgroundInfo 表。
    使用 try-except 處理可能的資料庫錯誤。
    """
    try:
        # 建立資料庫連線
        conn = sqlite3.connect(DB_PATH)
        # 建立游標物件以執行 SQL 指令
        c = conn.cursor()

        # 建立 BackgroundInfo 表，包含自動遞增的主鍵 id、user_id 和 info 欄位
        c.execute("""
            CREATE TABLE IF NOT EXISTS BackgroundInfo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                info TEXT NOT NULL
            )
        """)
        # 提交變更以確保表結構儲存
        conn.commit()
        # 關閉資料庫連線
        conn.close()
        # 輸出成功訊息
        print("資料庫初始化完成。")

    except sqlite3.Error as e:
        # 捕獲並顯示資料庫相關錯誤
        print(f"資料庫錯誤: {e}")

# 新增單筆背景資訊到資料庫
def add_background_info(user_id, new_info):
    """
    將單筆背景資訊插入 BackgroundInfo 表。
    參數：
        user_id: 使用者識別碼 (TEXT)
        new_info: 背景資訊內容 (TEXT)
    """
    try:
        # 建立資料庫連線
        conn = sqlite3.connect(DB_PATH)
        # 建立游標物件
        c = conn.cursor()

        # 輸出插入的資料內容，供調試使用
        print(f"插入資料: user_id = {user_id}, info = {new_info}")
        # 使用參數化查詢插入資料，防止 SQL 注入
        c.execute("""
            INSERT INTO BackgroundInfo (user_id, info) VALUES (?, ?)
        """, (user_id, new_info))

        # 提交變更
        conn.commit()
        # 輸出成功訊息
        print("資料已成功寫入資料庫。")
        # 關閉連線
        conn.close()

    except sqlite3.Error as e:
        # 捕獲並顯示資料庫錯誤
        print(f"資料庫錯誤: {e}")
    except Exception as e:
        # 捕獲並顯示其他未知錯誤
        print(f"未知錯誤: {e}")

# 批量新增多筆背景資訊到資料庫
def add_bulk_background_info(user_id, info_list):
    """
    批量插入多筆背景資訊到 BackgroundInfo 表。
    參數：
        user_id: 使用者識別碼 (TEXT)
        info_list: 背景資訊列表 (List of TEXT)
    """
    try:
        # 建立資料庫連線
        conn = sqlite3.connect(DB_PATH)
        # 建立游標物件
        c = conn.cursor()

        # 輸出批量插入的資訊，供調試使用
        print(f"批量插入資料: user_id = {user_id}")
        # 使用 executemany 批量插入資料，提高效率
        c.executemany("""
            INSERT INTO BackgroundInfo (user_id, info) VALUES (?, ?)
        """, [(user_id, info) for info in info_list])

        # 提交變更
        conn.commit()
        # 輸出成功訊息
        print("批量資料已成功寫入資料庫。")
        # 關閉連線
        conn.close()

    except sqlite3.Error as e:
        # 捕獲並顯示資料庫錯誤
        print(f"資料庫錯誤: {e}")
    except Exception as e:
        # 捕獲並顯示其他未知錯誤
        print(f"未知錯誤: {e}")

# 查詢並顯示所有背景資訊
def get_all_background_info():
    """
    從 BackgroundInfo 表查詢所有記錄並顯示。
    如果表中無資料，則顯示提示訊息。
    """
    try:
        # 建立資料庫連線
        conn = sqlite3.connect(DB_PATH)
        # 建立游標物件
        c = conn.cursor()

        # 輸出查詢提示
        print("查詢資料...")
        # 執行查詢，選擇所有欄位
        c.execute("""SELECT id, user_id, info FROM BackgroundInfo""")
        # 獲取所有查詢結果
        rows = c.fetchall()

        # 檢查是否有資料
        if not rows:
            # 若無資料，顯示提示
            print("目前資料庫中沒有任何背景資訊。")
        else:
            # 遍歷並顯示每筆記錄
            for row in rows:
                print(f"ID: {row[0]}, 使用者ID: {row[1]}, 背景資訊: {row[2]}")

        # 關閉連線
        conn.close()

    except sqlite3.Error as e:
        # 捕獲並顯示資料庫錯誤
        print(f"資料庫錯誤: {e}")
    except Exception as e:
        # 捕獲並顯示其他未知錯誤
        print(f"未知錯誤: {e}")

# 根據 ID 刪除單筆背景資訊
def delete_background_info_by_id(record_id):
    """
    根據指定 ID 刪除 BackgroundInfo 表中的記錄。
    參數：
        record_id: 要刪除的記錄 ID (INTEGER)
    """
    try:
        # 建立資料庫連線
        conn = sqlite3.connect(DB_PATH)
        # 建立游標物件
        c = conn.cursor()

        # 輸出刪除的記錄 ID，供調試使用
        print(f"刪除資料 ID: {record_id}")
        # 執行刪除操作，使用參數化查詢
        c.execute("DELETE FROM BackgroundInfo WHERE id = ?", (record_id,))
        # 提交變更
        conn.commit()

        # 檢查是否成功刪除記錄
        if c.rowcount > 0:
            print("資料已成功刪除。")
        else:
            print("未找到指定 ID 的資料。")

        # 關閉連線
        conn.close()

    except sqlite3.Error as e:
        # 捕獲並顯示資料庫錯誤
        print(f"資料庫錯誤: {e}")
    except Exception as e:
        # 捕獲並顯示其他未知錯誤
        print(f"未知錯誤: {e}")

# 批量刪除多筆背景資訊
def delete_bulk_background_info(record_ids):
    """
    根據指定的 ID 列表批量刪除 BackgroundInfo 表中的記錄。
    參數：
        record_ids: 要刪除的記錄 ID 列表 (List of INTEGER)
    """
    try:
        # 建立資料庫連線
        conn = sqlite3.connect(DB_PATH)
        # 建立游標物件
        c = conn.cursor()

        # 輸出批量刪除的 ID 列表，供調試使用
        print(f"批量刪除資料 ID: {record_ids}")
        # 動態生成佔位符，用於 IN 子句
        placeholders = ",".join(["?"] * len(record_ids))
        # 構建批量刪除的 SQL 查詢
        query = f"DELETE FROM BackgroundInfo WHERE id IN ({placeholders})"
        # 執行刪除操作
        c.execute(query, record_ids)
        # 提交變更
        conn.commit()

        # 檢查是否成功刪除記錄
        if c.rowcount > 0:
            print(f"已成功刪除 {c.rowcount} 筆資料。")
        else:
            print("未找到指定 ID 的資料。")

        # 關閉連線
        conn.close()

    except sqlite3.Error as e:
        # 捕獲並顯示資料庫錯誤
        print(f"資料庫錯誤: {e}")
    except Exception as e:
        # 捕獲並顯示其他未知錯誤
        print(f"未知錯誤: {e}")

# 主程式入口
if __name__ == "__main__":
    # 初始化資料庫
    init_db()

    # 顯示操作選單
    print("1. 新增背景資訊")
    print("2. 查看所有背景資訊")
    print("3. 批量新增背景資訊")
    print("4. 刪除指定 ID 的資料")
    print("5. 批量刪除指定 ID 的資料")

    # 獲取使用者輸入的操作選擇
    choice = input("請選擇操作 (1/2/3/4/5): ").strip()

    # 根據選擇執行相應操作
    if choice == "1":
        # 新增單筆背景資訊
        user_id = input("請輸入使用者ID: ").strip()
        new_info = input("請輸入新的背景資訊: ").strip()
        add_background_info(user_id, new_info)
    elif choice == "2":
        # 查看所有背景資訊
        get_all_background_info()
    elif choice == "3":
        # 批量新增背景資訊
        user_id = input("請輸入使用者ID: ").strip()
        print("請輸入多條背景資訊（每條資訊一行）：")
        info_list = []
        while True:
            # 循環獲取背景資訊，直到使用者輸入空行
            new_info = input("背景資訊 (按 Enter 結束輸入): ").strip()
            if not new_info:
                break
            info_list.append(new_info)
        add_bulk_background_info(user_id, info_list)
    elif choice == "4":
        # 刪除單筆記錄
        record_id = input("請輸入要刪除的資料 ID: ").strip()
        if record_id.isdigit():
            # 確保輸入為數字
            delete_background_info_by_id(int(record_id))
        else:
            print("無效的 ID，請輸入數字。")
    elif choice == "5":
        # 批量刪除記錄
        print("請輸入要批量刪除的資料 ID，用逗號分隔（例如: 1,2,3）")
        record_ids = input("請輸入 ID 列表: ").strip()
        try:
            # 將輸入的 ID 列表轉換為整數列表
            id_list = [int(id.strip()) for id in record_ids.split(",") if id.strip().isdigit()]
            if id_list:
                delete_bulk_background_info(id_list)
            else:
                print("無效的輸入，請輸入有效的數字 ID。")
        except ValueError:
            # 處理無效輸入
            print("無效的輸入，請確認格式正確。")
    else:
        # 處理無效的選單選擇
        print("無效選擇")
        
