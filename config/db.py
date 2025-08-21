import sqlite3
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

DB_PATH = "example.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS BackgroundInfo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                info TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("資料庫錯誤", str(e))

def add_background_info(user_id, new_info):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""INSERT INTO BackgroundInfo (user_id, info) VALUES (?, ?)""", (user_id, new_info))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("資料庫錯誤", str(e))

def add_bulk_background_info(user_id, info_list):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.executemany("""INSERT INTO BackgroundInfo (user_id, info) VALUES (?, ?)""", [(user_id, info) for info in info_list])
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("資料庫錯誤", str(e))

def get_all_background_info():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""SELECT id, user_id, info FROM BackgroundInfo""")
        rows = c.fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        messagebox.showerror("資料庫錯誤", str(e))
        return []

def delete_background_info_by_id(record_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM BackgroundInfo WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("資料庫錯誤", str(e))

def delete_bulk_background_info(record_ids):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        placeholders = ",".join(["?"] * len(record_ids))
        query = f"DELETE FROM BackgroundInfo WHERE id IN ({placeholders})"
        c.execute(query, record_ids)
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("資料庫錯誤", str(e))

def update_background_info(record_id, new_user_id=None, new_info=None, new_id=None):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # 依選項選擇要更新哪個欄位
        if new_id is not None:
            # 先檢查 new_id 是否已存在
            c.execute("SELECT id FROM BackgroundInfo WHERE id = ?", (new_id,))
            if c.fetchone():
                conn.close()
                messagebox.showerror("錯誤", f"ID {new_id} 已存在，請選擇其他ID")
                return False
            # 更新 id（先更新其他欄位再改 id）
            c.execute("UPDATE BackgroundInfo SET id = ? WHERE id = ?", (new_id, record_id))
            conn.commit()
        if new_user_id is not None:
            c.execute("UPDATE BackgroundInfo SET user_id = ? WHERE id = ?", (new_user_id, record_id if new_id is None else new_id))
            conn.commit()
        if new_info is not None:
            c.execute("UPDATE BackgroundInfo SET info = ? WHERE id = ?", (new_info, record_id if new_id is None else new_id))
            conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        messagebox.showerror("資料庫錯誤", str(e))
        return False

class BackgroundInfoApp:
    def __init__(self, master):
        self.master = master
        master.title("BackgroundInfo 資料庫管理")
        master.geometry("700x500")
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        frm_input = tk.Frame(self.master)
        frm_input.pack(pady=5)
        tk.Label(frm_input, text="使用者ID：").grid(row=0, column=0)
        self.user_id_entry = tk.Entry(frm_input, width=20)
        self.user_id_entry.grid(row=0, column=1, padx=5)
        tk.Label(frm_input, text="背景資訊：").grid(row=0, column=2)
        self.info_entry = tk.Entry(frm_input, width=40)
        self.info_entry.grid(row=0, column=3, padx=5)
        tk.Button(frm_input, text="新增", command=self.add_single).grid(row=0, column=4, padx=5)
        tk.Button(frm_input, text="批量新增", command=self.add_bulk).grid(row=0, column=5, padx=5)

        frm_list = tk.Frame(self.master)
        frm_list.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(frm_list, columns=("ID", "UserID", "Info"), show="headings", selectmode="extended")
        self.tree.heading("ID", text="ID")
        self.tree.heading("UserID", text="使用者ID")
        self.tree.heading("Info", text="背景資訊")
        self.tree.column("ID", width=50)
        self.tree.column("UserID", width=100)
        self.tree.column("Info", width=400)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(frm_list, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<Double-1>", self.on_edit)

        frm_btn = tk.Frame(self.master)
        frm_btn.pack(pady=8)
        tk.Button(frm_btn, text="刪除選取", command=self.delete_selected).grid(row=0, column=0, padx=5)
        tk.Button(frm_btn, text="重新整理", command=self.refresh_list).grid(row=0, column=1, padx=5)
        tk.Button(frm_btn, text="批量刪除", command=self.bulk_delete_ids).grid(row=0, column=2, padx=5)
        tk.Button(frm_btn, text="修改", command=self.modify_selected).grid(row=0, column=3, padx=5)

    def refresh_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in get_all_background_info():
            self.tree.insert("", tk.END, values=row)

    def add_single(self):
        user_id = self.user_id_entry.get().strip()
        info = self.info_entry.get().strip()
        if not user_id or not info:
            messagebox.showwarning("輸入錯誤", "請填寫使用者ID和背景資訊")
            return
        add_background_info(user_id, info)
        self.info_entry.delete(0, tk.END)
        self.refresh_list()

    def add_bulk(self):
        user_id = self.user_id_entry.get().strip()
        if not user_id:
            messagebox.showwarning("輸入錯誤", "請填寫使用者ID")
            return
        bulk_info = simpledialog.askstring("批量新增", "請輸入多筆背景資訊（每行一筆）：")
        if not bulk_info:
            return
        info_list = [s for s in bulk_info.splitlines() if s.strip()]
        if info_list:
            add_bulk_background_info(user_id, info_list)
            self.refresh_list()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("提示", "請先選取要刪除的資料")
            return
        for item in selected:
            record_id = self.tree.item(item)["values"][0]
            delete_background_info_by_id(record_id)
        self.refresh_list()

    def bulk_delete_ids(self):
        id_str = simpledialog.askstring("批量刪除", "請輸入要刪除的ID, 以逗號分隔：")
        if not id_str:
            return
        try:
            id_list = [int(s) for s in id_str.split(",") if s.strip().isdigit()]
            if id_list:
                delete_bulk_background_info(id_list)
                self.refresh_list()
        except Exception as e:
            messagebox.showerror("錯誤", str(e))

    def on_edit(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        self.modify_item(item)

    def modify_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("提示", "請先選取要修改的資料")
            return
        # 只允許多選時第一筆
        self.modify_item(selected[0])

    def modify_item(self, item):
        record = self.tree.item(item)["values"]
        record_id, user_id, info = record

        # 讓用戶選擇要修改哪一欄
        modify_field = simpledialog.askstring(
            "選擇欄位", 
            "要修改哪一欄？請輸入: id、user_id、info"
        )
        if not modify_field:
            return
        modify_field = modify_field.strip().lower()
        if modify_field == "id":
            new_id = simpledialog.askinteger("修改ID", f"原ID: {record_id}\n輸入新ID：", initialvalue=record_id)
            if new_id is not None and new_id != record_id:
                ok = update_background_info(record_id, new_id=new_id)
                if ok:
                    messagebox.showinfo("成功", "ID 修改成功！")
                    self.refresh_list()
        elif modify_field == "user_id":
            new_user_id = simpledialog.askstring("修改使用者ID", f"原使用者ID: {user_id}\n輸入新使用者ID：", initialvalue=user_id)
            if new_user_id is not None and new_user_id != user_id:
                ok = update_background_info(record_id, new_user_id=new_user_id)
                if ok:
                    messagebox.showinfo("成功", "使用者ID 修改成功！")
                    self.refresh_list()
        elif modify_field == "info":
            new_info = simpledialog.askstring("修改背景資訊", f"原背景資訊: {info}\n輸入新背景資訊：", initialvalue=info)
            if new_info is not None and new_info != info:
                ok = update_background_info(record_id, new_info=new_info)
                if ok:
                    messagebox.showinfo("成功", "背景資訊 修改成功！")
                    self.refresh_list()
        else:
            messagebox.showwarning("欄位錯誤", "請輸入 id、user_id 或 info")

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = BackgroundInfoApp(root)
    root.mainloop()
