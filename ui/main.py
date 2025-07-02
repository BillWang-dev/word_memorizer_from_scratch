import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

class MainApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("我的单词记忆程序") #窗口标题
        self.root.geometry("800x600") # 窗口大小
        self._create_main_interface() #调用方法, 创建主界面

    def _create_main_interface(self):
        """创建主界面"""
        # 创建标签页
        self.notebook = ttk.Notebook(self.root) #创建一个笔记本控件 , 用来管理标签页
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # fill=tk.BOTH, expand=True 的意思是让这个笔记本填满整个窗口，并随窗口大小变化而变化

        # 单词听写页
        self.word_frame = ttk.Frame(self.notebook) # 第一个标签页
        self.notebook.add(self.word_frame, text="📝 单词听写") #加入笔记本中
        
        #把复杂的听写界面封装在了另一个类 DictationInterface 中
        self.word_dictation = DictationInterface(self.word_frame)
        

        # 统计页面
        self.stats_frame = ttk.Frame(self.notebook) #第二个标签页
        self.notebook.add(self.stats_frame, text="📊 学习统计")

    def run(self):
        self.root.mainloop() #是一个循环, 让窗口一直显示

class DictationInterface:
    def __init__(self, parent_frame):
        """
        构造函数。现在它只需要一个 parent_frame，因为不需要核心逻辑了。
        """
        self.parent_frame = parent_frame  # 界面要画在这个父容器上
        
        # 直接调用创建界面的方法
        self._create_widgets()
        
        # 设置一些初始的提示文字，让界面看起来不那么空
        self._setup_initial_display()

    def _button_clicked(self, button_name: str):
        print(f"'{button_name}' 按钮被点击了。(这是静态版本，没有实际功能)")

    def _volume_changed(self, value: str):
        """
        专门为音量滑动条准备的占位函数。
        """
        # 从滑动条获取的值是字符串，我们转成浮点数再格式化输出
        print(f"音量被调整为: {float(value):.2f}")

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
        这个函数和原版几乎一样，只是修改了所有按钮的 `command` 参数。
        """
        main_frame = ttk.Frame(self.parent_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部控制区域
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(control_frame, text="🎧 单词听写 (静态演示)", 
                 font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
        
        # 【修改点】command 指向了我们的占位函数 _button_clicked
        ttk.Button(control_frame, text="下一个", 
                   command=lambda: self._button_clicked("下一个")).pack(side=tk.RIGHT)
        ttk.Button(control_frame, text="跳过", 
                   command=lambda: self._button_clicked("跳过")).pack(side=tk.RIGHT, padx=(0, 10))
        
        # 内容显示区域
        self.content_frame = ttk.LabelFrame(main_frame, text="听写内容", padding="20")
        self.content_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 音频控制区域
        audio_frame = ttk.LabelFrame(main_frame, text="音频控制", padding="15")
        audio_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 【修改点】所有按钮的 command 都改了
        self.play_button = ttk.Button(audio_frame, text="🔊 播放", 
                                      command=lambda: self._button_clicked("播放"))
        self.play_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(audio_frame, text="🔁 重播", 
                   command=lambda: self._button_clicked("重播")).pack(side=tk.LEFT, padx=(0, 10))
        
        # 音量控制
        volume_frame = ttk.Frame(audio_frame)
        volume_frame.pack(side=tk.RIGHT)
        
        ttk.Label(volume_frame, text="音量:").pack(side=tk.LEFT)
        self.volume_var = tk.DoubleVar(value=0.7)
        # 【修改点】滑动条的 command 也改了
        volume_scale = ttk.Scale(volume_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL,
                               variable=self.volume_var, command=self._volume_changed)
        volume_scale.pack(side=tk.LEFT, padx=(5, 0))
        
        # 答案输入区域
        answer_frame = ttk.LabelFrame(main_frame, text="答案输入", padding="15")
        answer_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        ttk.Label(answer_frame, text="请输入您听到的内容:").pack(anchor=tk.W)
        self.answer_input = scrolledtext.ScrolledText(answer_frame, height=4, wrap=tk.WORD,
                                                    font=('Arial', 12))
        self.answer_input.pack(fill=tk.X, pady=(5, 10))
        
        submit_frame = ttk.Frame(answer_frame)
        submit_frame.pack(fill=tk.X)
        
        # 【修改点】提交按钮的 command
        self.submit_button = ttk.Button(submit_frame, text="✅ 提交答案", 
                                        command=lambda: self._button_clicked("提交答案"))
        self.submit_button.pack(side=tk.LEFT)
        
        # 结果显示区域
        self.result_frame = ttk.LabelFrame(main_frame, text="结果", padding="15")
        self.result_frame.pack(fill=tk.X)
        
        self.result_text = scrolledtext.ScrolledText(self.result_frame, height=4, wrap=tk.WORD,
                                                   font=('Arial', 10), state=tk.DISABLED)
        self.result_text.pack(fill=tk.X)


#程序入口
if __name__ == "__main__":
    try:
        app = MainApplication()
        app.run()
    except Exception as e:
        logger.error(f"程序启动失败:{e}") # 记录错误日志
        messagebox.showerror("错误", f"程序启动失败:{e}") # 弹出错误提示框
        
        




