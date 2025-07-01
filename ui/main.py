import tkinter as tk
from tkinter import ttk

class MainApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("我的单词记忆程序")
        self.root.geometry("800x600")
        self._create_main_interface()

    def _create_main_interface(self):
        """创建主界面"""
        # 创建标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 单词听写页
        self.word_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.word_frame, text="📝 单词听写")
        
        # 统计页面
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="📊 学习统计")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MainApplication()
    app.run()
