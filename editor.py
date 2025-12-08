# editor.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

FILE_PATH = "scripts.json"

class ScriptEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Loop Game - 劇本編輯器 (Dev Tool)")
        self.root.geometry("800x600")

        self.data = {"Main": [], "Sub": []}
        self.load_data()

        self.left_panel = tk.Frame(root, width=250, bg="#ddd")
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y)
        self.type_var = tk.StringVar(value="Main")
        tk.Radiobutton(self.left_panel, text="主劇本 (Main)", variable=self.type_var, value="Main", command=self.refresh_list).pack(anchor="w", padx=5, pady=5)
        tk.Radiobutton(self.left_panel, text="支線 (Sub)", variable=self.type_var, value="Sub", command=self.refresh_list).pack(anchor="w", padx=5)

        self.script_listbox = tk.Listbox(self.left_panel)
        self.script_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.script_listbox.bind("<<ListboxSelect>>", self.on_select_script)

        btn_frame = tk.Frame(self.left_panel)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(btn_frame, text="新劇本", command=self.add_script).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(btn_frame, text="刪除", command=self.delete_script, fg="red").pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(self.left_panel, text="💾 儲存所有變更", command=self.save_to_file, bg="lightblue", height=2).pack(fill=tk.X, padx=5, pady=10)

        self.right_panel = tk.Frame(root, padx=20, pady=20)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        tk.Label(self.right_panel, text="劇本名稱:").pack(anchor="w")
        self.name_entry = tk.Entry(self.right_panel, width=40)
        self.name_entry.pack(anchor="w", pady=5)
        self.name_entry.bind("<KeyRelease>", self.on_name_change)

        tk.Label(self.right_panel, text="包含角色配置:").pack(anchor="w", pady=(20, 0))
        self.roles_frame = tk.Frame(self.right_panel)
        self.roles_frame.pack(fill=tk.BOTH, expand=True)
        
        self.role_canvas = tk.Canvas(self.roles_frame)
        scrollbar = tk.Scrollbar(self.roles_frame, orient="vertical", command=self.role_canvas.yview)
        self.role_inner_frame = tk.Frame(self.role_canvas)
        self.role_inner_frame.bind("<Configure>", lambda e: self.role_canvas.configure(scrollregion=self.role_canvas.bbox("all")))
        self.role_canvas.create_window((0, 0), window=self.role_inner_frame, anchor="nw")
        self.role_canvas.configure(yscrollcommand=scrollbar.set)
        self.role_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        tk.Button(self.right_panel, text="+ 新增需求角色", command=self.add_role_slot).pack(fill=tk.X, pady=10)
        self.current_idx = None
        self.refresh_list()

    def load_data(self):
        if os.path.exists(FILE_PATH):
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else: self.data = {"Main": [], "Sub": []}

    def save_to_file(self):
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
        messagebox.showinfo("成功", "已儲存至 scripts.json")

    def get_current_list(self): return self.data[self.type_var.get()]

    def refresh_list(self):
        self.script_listbox.delete(0, tk.END)
        for s in self.get_current_list(): self.script_listbox.insert(tk.END, s['name'])
        self.current_idx = None
        self.name_entry.delete(0, tk.END)
        for widget in self.role_inner_frame.winfo_children(): widget.destroy()

    def on_select_script(self, event):
        if not self.script_listbox.curselection(): return
        idx = self.script_listbox.curselection()[0]
        self.current_idx = idx
        script = self.get_current_list()[idx]
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, script['name'])
        for widget in self.role_inner_frame.winfo_children(): widget.destroy()
        for role in script['roles']: self.create_role_widget(role)

    def on_name_change(self, event):
        if self.current_idx is None: return
        new_name = self.name_entry.get()
        self.get_current_list()[self.current_idx]['name'] = new_name
        self.script_listbox.delete(self.current_idx)
        self.script_listbox.insert(self.current_idx, new_name)
        self.script_listbox.selection_set(self.current_idx)

    def add_script(self):
        self.get_current_list().append({"name": "新劇本", "roles": []})
        self.refresh_list()
        self.script_listbox.selection_set(len(self.get_current_list())-1)
        self.on_select_script(None)

    def delete_script(self):
        if self.current_idx is None: return
        if messagebox.askyesno("確認", "確定要刪除？"):
            del self.get_current_list()[self.current_idx]
            self.refresh_list()

    def add_role_slot(self):
        if self.current_idx is None: return
        new_role = {"name": "新身分", "count": 1, "gender": None}
        self.get_current_list()[self.current_idx]['roles'].append(new_role)
        self.create_role_widget(new_role)

    def create_role_widget(self, role_data):
        row = tk.Frame(self.role_inner_frame, pady=2, bd=1, relief=tk.SOLID)
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text="身分:").pack(side=tk.LEFT)
        entry_name = tk.Entry(row, width=10)
        entry_name.insert(0, role_data['name'])
        entry_name.pack(side=tk.LEFT, padx=5)
        tk.Label(row, text="數量:").pack(side=tk.LEFT)
        spin_count = tk.Spinbox(row, from_=1, to=5, width=3)
        spin_count.delete(0, tk.END); spin_count.insert(0, role_data['count'])
        spin_count.pack(side=tk.LEFT, padx=5)
        tk.Label(row, text="性別限:").pack(side=tk.LEFT)
        gender_var = tk.StringVar(value=role_data.get('gender') or "無")
        cb_gender = ttk.Combobox(row, textvariable=gender_var, values=["無", "F", "M"], width=3, state="readonly")
        cb_gender.pack(side=tk.LEFT, padx=5)
        def delete_this_role():
            if role_data in self.get_current_list()[self.current_idx]['roles']:
                self.get_current_list()[self.current_idx]['roles'].remove(role_data)
                row.destroy()
        tk.Button(row, text="X", fg="red", command=delete_this_role, relief=tk.FLAT).pack(side=tk.RIGHT, padx=5)
        def update_data(*args):
            role_data['name'] = entry_name.get()
            try: role_data['count'] = int(spin_count.get())
            except: role_data['count'] = 1
            role_data['gender'] = None if gender_var.get() == "無" else gender_var.get()
        entry_name.bind("<KeyRelease>", update_data)
        spin_count.bind("<KeyRelease>", update_data); spin_count.bind("<<Increment>>", update_data); spin_count.bind("<<Decrement>>", update_data)
        cb_gender.bind("<<ComboboxSelected>>", update_data)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScriptEditor(root)
    root.mainloop()