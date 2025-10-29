import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json, os


class NotebookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📝 Digital Notebook - Mini Project")
        self.root.geometry("850x600")

        # ==== Data Files ====
        self.notes_file = "notes.json"
        self.todos_file = "todos.json"

        # ==== Load Data ====
        self.notes = self.load_json(self.notes_file, {})
        self.todos = self.load_json(self.todos_file, [])

        # ==== Create Tabs ====
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.create_notes_tab()
        self.create_calculator_tab()
        self.create_todo_tab()
        self.create_search_tab()
        self.create_help_tab()

    # ---------------------- NOTES TAB ----------------------
    def create_notes_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🗒 Notes")

        # Center columns
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)

        ttk.Label(tab, text="Note Title:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.note_title = ttk.Entry(tab, width=60)
        self.note_title.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        self.notes_text = scrolledtext.ScrolledText(tab, wrap=tk.WORD, height=18, width=90)
        self.notes_text.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="n")

        button_frame = ttk.Frame(tab)
        button_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky="n")

        ttk.Button(button_frame, text="💾 Save", command=self.save_note).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="📂 Load", command=self.load_note).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="🆕 New", command=self.new_note).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="🗑 Delete", command=self.delete_note).grid(row=0, column=3, padx=5)

        ttk.Label(tab, text="Saved Notes:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.notes_listbox = tk.Listbox(tab, height=6)
        self.notes_listbox.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.notes_listbox.bind("<<ListboxSelect>>", self.select_note)
        self.update_notes_list()

    # ---------------------- CALCULATOR TAB ----------------------
    def create_calculator_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🧮 Calculator")

        tab.grid_columnconfigure((0, 1, 2, 3), weight=1)
        tab.grid_rowconfigure(tuple(range(6)), weight=1)

        self.calc_display = ttk.Entry(tab, font=("Arial", 20), justify="right")
        self.calc_display.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="ew")

        buttons = [
            ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("/", 1, 3),
            ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("*", 2, 3),
            ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("-", 3, 3),
            ("0", 4, 0), (".", 4, 1), ("=", 4, 2), ("+", 4, 3),
            ("C", 5, 0), ("CE", 5, 1)
        ]

        for text, row, col in buttons:
            ttk.Button(tab, text=text, command=lambda t=text: self.calc_button_click(t)).grid(
                row=row, column=col, padx=8, pady=8, sticky="nsew"
            )

    # ---------------------- TO-DO TAB ----------------------
    def create_todo_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="✅ To-Do List")

        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)

        ttk.Label(tab, text="Enter Task:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.todo_entry = ttk.Entry(tab, width=60)
        self.todo_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ttk.Button(tab, text="➕ Add Task", command=self.add_todo).grid(row=1, column=0, columnspan=2, pady=5)

        self.todos_listbox = tk.Listbox(tab, height=15, selectmode=tk.MULTIPLE)
        self.todos_listbox.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        btn_frame = ttk.Frame(tab)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky="n")
        ttk.Button(btn_frame, text="✔ Mark Done", command=self.mark_done).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="🗑 Delete", command=self.delete_todo).grid(row=0, column=1, padx=10)

        self.update_todos_list()

    # ---------------------- SEARCH TAB ----------------------
    def create_search_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🔍 Search")

        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)

        ttk.Label(tab, text="Enter Keyword:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.search_entry = ttk.Entry(tab, width=60)
        self.search_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ttk.Button(tab, text="Search Notes", command=self.search_notes).grid(row=1, column=0, columnspan=2, pady=5)

        self.search_results = scrolledtext.ScrolledText(tab, wrap=tk.WORD, height=20, width=90)
        self.search_results.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="n")

    # ---------------------- HELP TAB ----------------------
    def create_help_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="💡 Help")

        tab.grid_columnconfigure(0, weight=1)
        help_text = """
Welcome to Digital Notebook!

📘 Notes:
- Write and save notes easily.
- Load or delete from saved list.

🧮 Calculator:
- Perform simple math operations.

✅ To-Do List:
- Add tasks, mark them done, or delete.

🔍 Search:
- Search across all notes instantly.

Data auto-saves in JSON files.
Enjoy your Notebook! ✨
"""
        label = tk.Label(tab, text=help_text, justify="center", font=("Consolas", 11))
        label.grid(row=0, column=0, padx=15, pady=15, sticky="n")

    # ---------------------- NOTES FUNCTIONS ----------------------
    def save_note(self):
        title = self.note_title.get().strip()
        content = self.notes_text.get(1.0, tk.END).strip()
        if not title:
            messagebox.showerror("Error", "Enter a note title.")
            return
        self.notes[title] = content
        self.save_json(self.notes_file, self.notes)
        self.update_notes_list()
        messagebox.showinfo("Saved", f"Note '{title}' saved successfully!")

    def load_note(self):
        title = self.note_title.get().strip()
        if title in self.notes:
            self.notes_text.delete(1.0, tk.END)
            self.notes_text.insert(tk.END, self.notes[title])
        else:
            messagebox.showerror("Error", "Note not found.")

    def new_note(self):
        self.note_title.delete(0, tk.END)
        self.notes_text.delete(1.0, tk.END)

    def delete_note(self):
        title = self.note_title.get().strip()
        if title in self.notes:
            del self.notes[title]
            self.save_json(self.notes_file, self.notes)
            self.update_notes_list()
            self.new_note()
            messagebox.showinfo("Deleted", f"Note '{title}' deleted.")
        else:
            messagebox.showerror("Error", "Note not found.")

    def select_note(self, event):
        selection = self.notes_listbox.curselection()
        if selection:
            title = self.notes_listbox.get(selection[0])
            self.note_title.delete(0, tk.END)
            self.note_title.insert(0, title)
            self.load_note()

    def update_notes_list(self):
        self.notes_listbox.delete(0, tk.END)
        for title in self.notes:
            self.notes_listbox.insert(tk.END, title)

    # ---------------------- CALCULATOR FUNCTIONS ----------------------
    def calc_button_click(self, text):
        if text == "=":
            try:
                result = str(eval(self.calc_display.get()))
                self.calc_display.delete(0, tk.END)
                self.calc_display.insert(0, result)
            except:
                self.calc_display.delete(0, tk.END)
                self.calc_display.insert(0, "Error")
        elif text == "C":
            self.calc_display.delete(0, tk.END)
        elif text == "CE":
            current = self.calc_display.get()
            self.calc_display.delete(0, tk.END)
            self.calc_display.insert(0, current[:-1])
        else:
            self.calc_display.insert(tk.END, text)

    # ---------------------- TO-DO FUNCTIONS ----------------------
    def add_todo(self):
        task = self.todo_entry.get().strip()
        if task:
            self.todos.append({"task": task, "done": False})
            self.save_json(self.todos_file, self.todos)
            self.update_todos_list()
            self.todo_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Enter a task.")

    def mark_done(self):
        selections = self.todos_listbox.curselection()
        for i in selections:
            self.todos[i]["done"] = True
        self.save_json(self.todos_file, self.todos)
        self.update_todos_list()

    def delete_todo(self):
        selections = self.todos_listbox.curselection()
        for i in reversed(selections):
            del self.todos[i]
        self.save_json(self.todos_file, self.todos)
        self.update_todos_list()

    def update_todos_list(self):
        self.todos_listbox.delete(0, tk.END)
        for todo in self.todos:
            status = "✅" if todo["done"] else "⬜"
            self.todos_listbox.insert(tk.END, f"{status} {todo['task']}")

    # ---------------------- SEARCH FUNCTION ----------------------
    def search_notes(self):
        keyword = self.search_entry.get().strip().lower()
        self.search_results.delete(1.0, tk.END)
        if not keyword:
            messagebox.showerror("Error", "Enter a keyword.")
            return
        found = False
        for title, content in self.notes.items():
            if keyword in title.lower() or keyword in content.lower():
                snippet = content[:150].replace("\n", " ") + ("..." if len(content) > 150 else "")
                self.search_results.insert(tk.END, f"📘 {title}\n{snippet}\n\n")
                found = True
        if not found:
            self.search_results.insert(tk.END, "No matches found.")

    # ---------------------- JSON HELPERS ----------------------
    def save_json(self, file, data):
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_json(self, file, default):
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        return default


if __name__ == "__main__":
    root = tk.Tk()
    app = NotebookApp(root)
    root.mainloop()
