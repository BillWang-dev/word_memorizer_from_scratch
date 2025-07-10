import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.font_manager as fm
import numpy as np

from typing import Dict
from asyncio import set_event_loop
from os.path import commonpath
import tkinter as tk
from tkinter import DISABLED, LEFT, RIGHT, Pack, ttk, messagebox, scrolledtext
import logging
import sv_ttk
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__))) # 工作目录定义为根目录

from logic.core import MemorizerCore, WordItem
from audio.listen import get_listen_engine

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

class MainApplication:
    def __init__(self):
        self.root = tk.Tk()

        sv_ttk.use_light_theme() #选择UI的主题
        
        self.root.title("我的单词记忆程序") #窗口标题
        self.root.geometry("1000x700") # 窗口大小
        # 初始化核心组件
        self.core = MemorizerCore()
        self.core.initialize()
        
        self._create_main_interface() #调用方法, 创建主界面

    def _create_main_interface(self):
        """创建主界面"""
        # 创建标签页
        self.notebook = ttk.Notebook(self.root) #ttk.Notebook 是容器型控件，专门用来创建带有多个标签页的界面
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # fill=tk.BOTH, expand=True 的意思是让这个笔记本填满整个窗口，并随窗口大小变化而变化

        # 单词听写页
        self.word_frame = ttk.Frame(self.notebook) # ttk.Frame 是普通容器控件，用来放置其它控件 (Label、Entry、Button)
        self.notebook.add(self.word_frame, text="📝 单词听写") #向 Notebook（标签页容器）中添加一个新的标签页
        
        #把复杂的听写界面封装在了另一个类 DictationInterface 中
        self.word_dictation = DictationInterface(self.word_frame, self.core)
        

        # 统计页面
        self.stats_frame = ttk.Frame(self.notebook) #第二个标签页
        self.notebook.add(self.stats_frame, text="📊 学习统计")
        self.statistics_panel = StatisticsPanel(self.stats_frame, self.core)

    def run(self):
        self.root.mainloop() #是一个循环, 让窗口一直显示

class DictationInterface:
    def __init__(self, parent_frame, core: MemorizerCore):
        """
        构造函数。现在它只需要一个 parent_frame，因为不需要核心逻辑了。
        """
        self.parent_frame = parent_frame  # 在单词听写页面下
        self.current_item = None
        self.core = core
        self.answer_submitted = False
        self.listen_engine = get_listen_engine()

        self._create_widgets() #在当前界面创建一些控件 
        
        self._load_next_item()
    
    def _load_next_item(self):
        self.current_item = self.core.get_next_review_item("word")
        if self.current_item is None:
            messagebox.showinfo("所有单词已复习完成")
            return
        self._reset_interface()
        self._display_next_item()

    def _display_next_item(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        info_text = f"单词听写, 含义:{self.current_item.meaning}"
        if self.current_item.pronunciation:
            info_text += f"\n音标:{self.current_item.pronunciation}"
        ttk.Label(self.content_frame, text = info_text, font = ('Arial', 12), justify=tk.LEFT).pack(anchor=tk.W)
        

    def _button_clicked(self, button_name: str): # 没有任何实际功能
        print(f"'{button_name}' 按钮被点击了")

    def _setup_initial_display(self):
        """
        设置界面上各个区域的初始提示文本。
        """
        # 在“听写内容”区域显示提示
        info_text = "这里会显示单词的提示信息，例如：\n含义: 苹果\n音标: /ˈæp.əl/"
        ttk.Label(self.content_frame, text=info_text, font=('Arial', 12)).pack(anchor=tk.W)

        # 在“结果”区域显示提示
        self.result_text.config(state=tk.NORMAL) # 先设为可编辑
        self.result_text.delete(1.0, tk.END) # 清空内容
        self.result_text.insert(1.0, "提交答案后，这里会显示对错结果。") # 插入提示文字
        self.result_text.config(state=tk.DISABLED) # 再设为不可编辑

    def _create_widgets(self):
        """
        创建界面组件 (核心部分)。
        """
        main_frame = ttk.Frame(self.parent_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部控制区域
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(control_frame, text="🎧 单词听写", 
                 font=('Arial', 14, 'bold')).pack(side=tk.LEFT) #.pack(side = tk.LEFT) 从最左边开始布局 
        
        # command 指向了占位函数 _button_clicked
        ttk.Button(control_frame, text="下一个", # 按钮的名称为“下一个  ” 
                   command=self._load_next_item).pack(side=tk.RIGHT)
        # 听写内容显示区域
        self.content_frame = ttk.LabelFrame(main_frame, text="听写内容", padding="20")
        self.content_frame.pack(fill=tk.X, pady=(0, 20))

        # 音频控制区域
        self.audio_frame = ttk.LabelFrame(main_frame, text = "音频控制", padding="20")
        self.audio_frame.pack(fill=tk.X, pady=(0, 20))

        self.play_button = ttk.Button(self.audio_frame, text="🔊 播放", 
                                      command = self._play_audio) 
        self.play_button.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(self.audio_frame, text="🔁 重播", 
                   command=self._play_audio).pack(side=tk.LEFT, padx=(0, 10))
        
        # 答案输入区域
        self.answer_frame = ttk.LabelFrame(main_frame,text="答案输入", padding="20")
        self.answer_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.answer_input = tk.Entry(self.answer_frame, font=('Arial', 12))
        self.answer_input.pack(fill=tk.X, pady=(5, 10))


        submit_frame = ttk.Frame(self.answer_frame)
        submit_frame.pack(fill=tk.X)

        # 提交按钮
        self.submit_button = ttk.Button(submit_frame, text="✅ 提交答案", 
        command = self._submit_answer)
        self.submit_button.pack(side=tk.LEFT)
        
        #结果显示:
        self.result_frame = ttk.LabelFrame(main_frame, text="结果显示", padding="20")
        self.result_frame.pack(fill=tk.X)
        
        self.result_text = scrolledtext.ScrolledText(self.result_frame, height=4, wrap=tk.WORD,
                                                   font=('Arial', 10), state=tk.DISABLED)
        self.result_text.pack(fill=tk.X)

    def _submit_answer(self):
        user_answer = self.answer_input.get().strip()
        if not user_answer:
            messagebox.showwarning("提示", "请输入您听到的内容")
            return
        correct_answer = self.current_item.word
        is_correct = self.compare_texts(correct_answer, user_answer)
        
        if not self.answer_submitted:
            self.core.submit_answer(self.current_item, is_correct)
            self.answer_submitted = True
        self._display_result(is_correct, correct_answer, user_answer)

    def _display_result(self, is_correct, correct:str, user_answer: str):
        self.result_text.config(state = tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        result_text = f"{'🎉正确! ' if is_correct else '❌ 错误'}\n"
        result_text += f"正确答案:{correct}\n"
        result_text += f"你的答案:{user_answer}\n"
        
        self.result_text.insert(1.0, result_text)
        self.result_text.config(state = DISABLED)
        
    
    def compare_texts(self, original: str, recognized: str)-> bool:
        return original.strip().lower() == recognized.strip().lower()
    
    def _reset_interface(self):
        self.answer_submitted = False
        self.answer_input.delete(0, tk.END)
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        # 重置按钮文本和状态
        self.submit_button.config(text="✅ 提交答案", state=tk.NORMAL)
    def _play_audio(self):
        if self.current_item is None:
            return
        text_to_play = self.current_item.word
        def play_finished():
            self.play_button.config(text="🔊 播放", state=tk.NORMAL)
        self.play_button.config(text = "播放中...", state = tk.DISABLED)
        self.listen_engine.play_text(text_to_play, callback=play_finished)

class StatisticsPanel:

    def __init__(self, parent_frame, core: MemorizerCore):
        self.parent_frame = parent_frame
        self.core = core
        self.canvas = None
        self._create_widgets()

    def _create_widgets(self):
        control_frame = ttk.Frame(self.parent_frame)
        control_frame.pack(fill=tk.X, padx = 10, pady= 10)

        ttk.Label(control_frame, text="📊 学习统计", font=('Arial', 14, 'bold')).pack(side = tk.LEFT)

        ttk.Button(control_frame, text="刷新数据", command = self.refresh_data).pack(side = tk.RIGHT)
        
        # 数据显示区域
        self.stats_frame = ttk.LabelFrame(self.parent_frame, text="概览统计", padding="10")
        self.stats_frame.pack(fill=tk.X, padx = 10, pady = (0, 10))
        
        # 图表显示区域
        self.chart_frame = ttk.LabelFrame(self.parent_frame, text="数据图表", padding="10")
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.refresh_data()
        
    def _button_clicked(self, button_name: str): # 没有任何实际功能
        print(f"'{button_name}' 按钮被点击了")
    
    def refresh_data(self):
        try:
            stats = self.core.get_overall_stats()
            session_stats = self.core.get_session_stats()
            
            # 更新概览统计
            self._update_overview(stats, session_stats)
            
            # 更新图表
            self._update_charts(stats)
        except Exception as e:
            logger.error(f"刷新统计数据失败: {e}")
            messagebox.showerror("错误", f"刷新数据失败: {e}")
    
    def _update_overview(self, stats: Dict, session_stats: Dict):
        # 清除旧的统计显示
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        word_frame = ttk.LabelFrame(self.stats_frame, text = "单词统计", padding = "10")
        word_frame.pack(side = tk.LEFT, fill = tk.BOTH, expand = True, padx = (10, 5))
        
        word_stats = stats.get('words', {})
        
        self._create_stat_item(word_frame, "总数", word_stats.get('total', 0))
        self._create_stat_item(word_frame, "已复习", word_stats.get('reviewed', 0))
        self._create_stat_item(word_frame, "正确率", f"{word_stats.get('accuracy', 0):.1f}%")
    
    def _update_charts(self, stats: Dict):
       # 清除旧图表
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        # 创建matplotlib图表
        self.figure = Figure(figsize=(12, 6), dpi=100)
        # 创建子图
        ax1 = self.figure.add_subplot(121)  # 左上
        ax2 = self.figure.add_subplot(122)  # 右上
        # 图1: 单词统计柱状图
        self._create_word_stats_chart(ax1, stats)
        
        # 图2: 单词正确率饼图
        self._create_word_accuracy_chart(ax2, stats)
        
        
        self.figure.tight_layout()
        # 嵌入到Tkinter
        self.canvas = FigureCanvasTkAgg(self.figure, self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _create_word_stats_chart(self, ax, stats:Dict):
        words = stats.get('words', {})
        categories = ['Total', 'Reviewed']
        word_values = [words.get('total', 0), words.get('reviewed', 0)]

        x = np.arange(len(categories))

        ax.bar(x, word_values, color='skyblue', alpha=0.8)

        ax.set_title('Word Learning Statistics')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.grid(True, alpha=0.3)

        # 在柱状图上显示数值
        for i, v in enumerate(word_values):
            ax.text(i, v + max(word_values) * 0.01, str(v), ha='center', va='bottom')
    
    def _create_word_accuracy_chart(self, ax, stats: Dict):
        words = stats.get('words', {})

        word_accuracy = words.get('accuracy', 0)
        word_reviewed = words.get('reviewed', 0)
        word_total = words.get('total', 0)

        if word_reviewed > 0:
            correct_count = round(word_reviewed * word_accuracy / 100)
            incorrect_count = word_reviewed - correct_count
            
            labels = ['correct','incorrect']
            sizes = [correct_count, incorrect_count]
            colors = ['lightgreen', 'lightcoral']
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.set_title(f"word_accuracy ({word_accuracy:.1f}%)")

        else:
            ax.text(0.5, 0.5,'no_records', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12)
            ax.set_title('word_accuracy')
    

    def _create_stat_item(self, parent, label: str, value):
        item_frame = ttk.Frame(parent)
        item_frame.pack(fill = tk.X, pady = 2)

        ttk.Label(item_frame, text = f"{label}:", font = ('Arial', 9)).pack(side=tk.LEFT)
        ttk.Label(item_frame, text = str(value), font = ('Arial', 9, 'bold')).pack(side = tk.RIGHT)
    

#程序入口
if __name__ == "__main__":
    try:
        app = MainApplication()
        app.run()
    except Exception as e:
        logger.error(f"程序启动失败:{e}") # 记录错误日志
        messagebox.showerror("错误", f"程序启动失败:{e}") # 弹出错误提示框
        
        




