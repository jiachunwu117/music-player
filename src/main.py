"""
简单音乐播放器
课程设计 - 程序语言课程设计
功能：播放/暂停/上一曲/下一曲/重播/音量控制/进度条/循环模式
快捷键：空格=播放/暂停，←=上一曲，→=下一曲，↑=音量+，↓=音量-
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pygame
import os
import random
import time
import json
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE


class MusicPlayer:
    """音乐播放器主类"""

    # 播放列表保存文件
    PLAYLIST_FILE = "playlist.json"

    def __init__(self, root):
        """初始化播放器"""
        # 窗口设置
        self.root = root
        self.root.title("🎵 音乐播放器")
        self.root.geometry("500x650")

        # 初始化pygame音乐播放器
        pygame.mixer.init()

        # ===== 播放状态变量 =====
        self.song_list = []          # 歌曲路径列表
        self.current_index = -1      # 当前播放歌曲索引
        self.is_playing = False      # 是否在播放
        self.is_paused = False       # 是否暂停
        self.song_duration = 0       # 当前歌曲总时长（秒）
        self.current_position = 0    # 当前播放位置（秒）
        self.play_start_time = 0     # 开始播放的时间点
        self.play_mode = 0           # 0=列表循环 1=单曲循环 2=随机播放
        self.timer_id = None         # 进度更新定时器ID

        # 创建界面
        self.create_ui()

        # 默认音量70%
        self.volume_slider.set(70)
        pygame.mixer.music.set_volume(0.7)

        # 加载上次保存的播放列表
        self.load_playlist()

        # 绑定键盘快捷键
        self.bind_keyboard_shortcuts()

        # 窗口关闭时清理资源
        self.root.protocol("WM_DELETE_WINDOW", self.cleanup)

    # ==================== 键盘快捷键绑定 ====================

    def bind_keyboard_shortcuts(self):
        """绑定键盘快捷键"""
        self.root.focus_set()

        # 空格键 - 播放/暂停
        self.root.bind("<space>", lambda e: self.play_pause())

        # 左箭头 - 上一曲
        self.root.bind("<Left>", lambda e: self.prev_song())

        # 右箭头 - 下一曲
        self.root.bind("<Right>", lambda e: self.next_song())

        # 上箭头 - 增加音量
        self.root.bind("<Up>", lambda e: self.volume_up())

        # 下箭头 - 减小音量
        self.root.bind("<Down>", lambda e: self.volume_down())

    def volume_up(self):
        """增加音量"""
        current = int(self.volume_slider.get())
        new_vol = min(100, current + 10)
        self.volume_slider.set(new_vol)
        self.set_volume()

    def volume_down(self):
        """减小音量"""
        current = int(self.volume_slider.get())
        new_vol = max(0, current - 10)
        self.volume_slider.set(new_vol)
        self.set_volume()

    # ==================== 播放列表持久化 ====================

    def save_playlist(self):
        """保存播放列表到本地文件"""
        try:
            with open(self.PLAYLIST_FILE, "w", encoding="utf-8") as f:
                json.dump(self.song_list, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存播放列表失败: {e}")

    def load_playlist(self):
        """从本地文件加载播放列表"""
        if not os.path.exists(self.PLAYLIST_FILE):
            return

        try:
            with open(self.PLAYLIST_FILE, "r", encoding="utf-8") as f:
                loaded_list = json.load(f)

            # 只保留仍然存在的文件
            self.song_list = []
            for file_path in loaded_list:
                if os.path.exists(file_path):
                    self.song_list.append(file_path)
                    self.listbox.insert(tk.END, os.path.basename(file_path))
                # 不存在的文件自动忽略

            if self.song_list:
                self.status_label.config(text=f"📂 已加载 {len(self.song_list)} 首歌曲")
                # 自动播放第一首
                self.play_song(0)
            else:
                self.status_label.config(text="💡 双击列表播放歌曲")

        except Exception as e:
            print(f"加载播放列表失败: {e}")
            self.status_label.config(text="💡 双击列表播放歌曲")

    # ==================== 界面创建 ====================

    def create_ui(self):
        """创建所有界面组件"""
        # ---------- 标题 ----------
        title = tk.Label(self.root, text="🎵 音乐播放器",
                         font=("微软雅黑", 16, "bold"), fg="#2196F3")
        title.pack(pady=10)

        # ---------- 快捷键提示 ----------
        shortcut_label = tk.Label(self.root, text="⌨️ 空格:暂停/播放 | ←:上一曲 | →:下一曲 | ↑:音量+ | ↓:音量-",
                                  font=("微软雅黑", 8), fg="#888")
        shortcut_label.pack()

        # ---------- 播放列表 ----------
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        list_label = tk.Label(list_frame, text="📋 播放列表", font=("微软雅黑", 10))
        list_label.pack(anchor=tk.W)

        # 带滚动条的列表
        listbox_frame = tk.Frame(list_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(listbox_frame,
                                  bg="#1a1a2e", fg="white",
                                  font=("微软雅黑", 10),
                                  yscrollcommand=scrollbar.set,
                                  height=12,
                                  selectbackground="#2196F3")
        self.listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        # 双击列表播放
        self.listbox.bind("<Double-Button-1>", lambda e: self.play_selected())

        # ---------- 当前播放信息 ----------
        self.info_label = tk.Label(self.root, text="🎵 未播放",
                                   font=("微软雅黑", 10), fg="#666")
        self.info_label.pack(pady=5)

        # ---------- 进度条 ----------
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(fill=tk.X, padx=20, pady=5)

        self.time_label = tk.Label(progress_frame, text="00:00", font=("Arial", 9))
        self.time_label.pack(side=tk.LEFT)

        self.progress = ttk.Scale(progress_frame, from_=0, to=100,
                                  orient=tk.HORIZONTAL, length=300)
        self.progress.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        # 松开鼠标时跳转
        self.progress.bind("<ButtonRelease-1>", self.seek_position)

        self.duration_label = tk.Label(progress_frame, text="00:00", font=("Arial", 9))
        self.duration_label.pack(side=tk.RIGHT)

        # ---------- 控制按钮 ----------
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        btn_style = {"width": 8, "height": 1, "font": ("微软雅黑", 10)}

        tk.Button(control_frame, text="⏮上一曲",
                  command=self.prev_song, **btn_style).pack(side=tk.LEFT, padx=3)

        self.play_btn = tk.Button(control_frame, text="▶播放",
                                  command=self.play_pause,
                                  **btn_style, bg="#4CAF50", fg="white")
        self.play_btn.pack(side=tk.LEFT, padx=3)

        tk.Button(control_frame, text="下一曲⏭",
                  command=self.next_song, **btn_style).pack(side=tk.LEFT, padx=3)

        tk.Button(control_frame, text="🔄重播",
                  command=self.replay, **btn_style).pack(side=tk.LEFT, padx=3)

        # ---------- 功能按钮 ----------
        func_frame = tk.Frame(self.root)
        func_frame.pack(pady=8)

        tk.Button(func_frame, text="📂添加音乐",
                  command=self.add_songs, width=10,
                  font=("微软雅黑", 9)).pack(side=tk.LEFT, padx=3)

        tk.Button(func_frame, text="🗑清空列表",
                  command=self.clear_list, width=10,
                  font=("微软雅黑", 9)).pack(side=tk.LEFT, padx=3)

        self.mode_btn = tk.Button(func_frame, text="🔁列表循环",
                                  command=self.switch_mode, width=12,
                                  font=("微软雅黑", 9), bg="#FFC107")
        self.mode_btn.pack(side=tk.LEFT, padx=3)

        # ---------- 音量控制 ----------
        volume_frame = tk.Frame(self.root)
        volume_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(volume_frame, text="🔊音量:", font=("微软雅黑", 9)).pack(side=tk.LEFT)

        self.volume_slider = ttk.Scale(volume_frame, from_=0, to=100,
                                       orient=tk.HORIZONTAL, length=150)
        self.volume_slider.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.volume_slider.bind("<ButtonRelease-1>", self.set_volume)

        self.vol_label = tk.Label(volume_frame, text="70%", font=("Arial", 9))
        self.vol_label.pack(side=tk.LEFT, padx=5)

        # ---------- 底部状态栏 ----------
        self.status_label = tk.Label(self.root, text="💡 双击列表播放歌曲",
                                     font=("微软雅黑", 8), fg="#888")
        self.status_label.pack(side=tk.BOTTOM, pady=5)

    # ==================== 核心功能 ====================

    def get_song_duration(self, file_path):
        """获取歌曲总时长（秒）"""
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.mp3':
                return MP3(file_path).info.length
            elif ext == '.flac':
                return FLAC(file_path).info.length
            elif ext == '.ogg':
                return OggVorbis(file_path).info.length
            elif ext == '.wav':
                return WAVE(file_path).info.length
            else:
                return 0
        except:
            return 0

    def add_songs(self):
        """添加音乐文件到播放列表"""
        files = filedialog.askopenfilenames(
            title="选择音乐文件",
            filetypes=[("音频文件", "*.mp3 *.wav *.flac *.ogg"), ("所有文件", "*.*")]
        )

        if files:
            for file in files:
                if file not in self.song_list:
                    self.song_list.append(file)
                    self.listbox.insert(tk.END, os.path.basename(file))

            # 保存列表到文件
            self.save_playlist()

            self.status_label.config(text=f"✅ 已添加 {len(files)} 首歌曲")

            # 如果当前没有播放，自动播放第一首
            if not self.is_playing:
                self.play_song(0)

    def play_selected(self):
        """播放列表中选中的歌曲"""
        selected = self.listbox.curselection()
        if selected:
            self.play_song(selected[0])

    def play_song(self, index, start_pos=0):
        """播放指定索引的歌曲，可从指定位置开始"""
        if index < 0 or index >= len(self.song_list):
            return

        self.current_index = index
        file_path = self.song_list[index]

        try:
            # 读取歌曲时长
            self.song_duration = self.get_song_duration(file_path)
            if self.song_duration > 0:
                min_str = str(int(self.song_duration // 60)).zfill(2)
                sec_str = str(int(self.song_duration % 60)).zfill(2)
                self.duration_label.config(text=f"{min_str}:{sec_str}")
                self.progress.config(to=100)
            else:
                self.duration_label.config(text="--:--")
                self.progress.config(to=0)

            # 加载并播放
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play(start=start_pos)

            # 更新状态
            self.current_position = start_pos
            self.play_start_time = time.time()
            self.is_playing = True
            self.is_paused = False
            self.play_btn.config(text="⏸暂停", bg="#FF9800")

            # 更新界面
            self.info_label.config(text=f"🎵 {os.path.basename(file_path)}")
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(index)
            self.listbox.see(index)
            self.status_label.config(text="▶ 播放中")

            # 更新进度条
            self.update_display(start_pos)

            # 启动进度更新
            self.start_timer()

        except Exception as e:
            messagebox.showerror("错误", f"无法播放:\n{str(e)}")

    # ==================== 播放控制 ====================

    def play_pause(self):
        """播放/暂停切换"""
        if not self.song_list:
            messagebox.showinfo("提示", "请先添加音乐")
            return

        # 如果当前没有播放，播放选中的或第一首
        if not self.is_playing:
            selected = self.listbox.curselection()
            self.play_song(selected[0] if selected else 0)
            return

        # 暂停/恢复切换
        if self.is_paused:
            # 恢复播放
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.play_btn.config(text="⏸暂停", bg="#FF9800")
            self.status_label.config(text="▶ 继续播放")
            self.play_start_time = time.time()
            self.start_timer()
        else:
            # 暂停
            pygame.mixer.music.pause()
            self.is_paused = True
            self.play_btn.config(text="▶播放", bg="#4CAF50")
            self.status_label.config(text="⏸ 已暂停")

            # 保存当前位置
            elapsed = time.time() - self.play_start_time
            self.current_position = self.current_position + elapsed

    def replay(self):
        """重播：从头播放当前歌曲"""
        if not self.song_list:
            messagebox.showinfo("提示", "请先添加音乐")
            return

        if self.current_index < 0 or self.current_index >= len(self.song_list):
            self.play_song(0)
            return

        self.play_song(self.current_index, 0)
        self.status_label.config(text="🔄 重新播放")

    def prev_song(self):
        """上一曲"""
        if not self.song_list:
            return

        if self.play_mode == 2:  # 随机模式
            self.play_random()
            return

        if self.current_index > 0:
            self.play_song(self.current_index - 1)
        else:
            self.play_song(len(self.song_list) - 1)

    def next_song(self):
        """下一曲"""
        if not self.song_list:
            return

        if self.play_mode == 2:  # 随机模式
            self.play_random()
            return

        if self.current_index < len(self.song_list) - 1:
            self.play_song(self.current_index + 1)
        else:
            self.play_song(0)

    def play_random(self):
        """随机播放一首"""
        if len(self.song_list) <= 1:
            return

        rand_idx = random.randint(0, len(self.song_list) - 1)
        while rand_idx == self.current_index and len(self.song_list) > 1:
            rand_idx = random.randint(0, len(self.song_list) - 1)
        self.play_song(rand_idx)

    # ==================== 进度条相关 ====================

    def get_current_position(self):
        """计算当前播放位置（秒）"""
        if not self.is_playing:
            return 0

        if self.is_paused:
            return self.current_position

        elapsed = time.time() - self.play_start_time
        pos = self.current_position + elapsed

        if self.song_duration > 0 and pos > self.song_duration:
            pos = self.song_duration

        return pos

    def update_display(self, position):
        """更新进度条和时间标签"""
        if self.song_duration <= 0:
            return

        min_str = str(int(position // 60)).zfill(2)
        sec_str = str(int(position % 60)).zfill(2)
        self.time_label.config(text=f"{min_str}:{sec_str}")

        percent = (position / self.song_duration) * 100
        self.progress.set(min(percent, 100))

    def start_timer(self):
        """启动进度更新定时器"""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.update_progress()

    def update_progress(self):
        """定时更新进度（每500ms）"""
        if self.is_playing and not self.is_paused:
            if not pygame.mixer.music.get_busy():
                self.on_song_end()
                return

            pos = self.get_current_position()
            self.update_display(pos)

        self.timer_id = self.root.after(500, self.update_progress)

    def on_song_end(self):
        """歌曲播放结束处理"""
        self.is_playing = False
        self.play_btn.config(text="▶播放", bg="#4CAF50")
        self.progress.set(0)
        self.time_label.config(text="00:00")
        self.current_position = 0

        if self.play_mode == 0:
            self.next_song()
        elif self.play_mode == 1:
            self.play_song(self.current_index)
        elif self.play_mode == 2:
            self.play_random()

    def seek_position(self, event):
        """拖动进度条跳转"""
        if not self.is_playing or self.song_duration <= 0:
            return

        percent = self.progress.get() / 100
        target = min(percent * self.song_duration, self.song_duration)

        was_playing = not self.is_paused

        try:
            file_path = self.song_list[self.current_index]
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play(start=target)

            self.current_position = target
            self.play_start_time = time.time()

            if not was_playing:
                pygame.mixer.music.pause()
                self.is_paused = True
                self.play_btn.config(text="▶播放", bg="#4CAF50")
            else:
                self.is_paused = False
                self.play_btn.config(text="⏸暂停", bg="#FF9800")

            self.update_display(target)

            min_str = str(int(target // 60)).zfill(2)
            sec_str = str(int(target % 60)).zfill(2)
            self.status_label.config(text=f"⏩ 跳转到 {min_str}:{sec_str}")

        except Exception as e:
            print(f"跳转失败: {e}")

    # ==================== 其他功能 ====================

    def switch_mode(self):
        """切换循环模式"""
        modes = ["🔁列表循环", "🔂单曲循环", "🎲随机播放"]
        self.play_mode = (self.play_mode + 1) % 3
        self.mode_btn.config(text=modes[self.play_mode])
        self.status_label.config(text=f"🔄 {modes[self.play_mode]}")

    def set_volume(self, event=None):
        """调节音量"""
        vol = int(self.volume_slider.get()) / 100
        pygame.mixer.music.set_volume(vol)
        self.vol_label.config(text=f"{int(vol * 100)}%")

    def clear_list(self):
        """清空播放列表"""
        if not self.song_list:
            return

        if messagebox.askyesno("确认", "确定清空播放列表吗？"):
            self.song_list.clear()
            self.listbox.delete(0, tk.END)
            pygame.mixer.music.stop()
            self.is_playing = False
            self.is_paused = False
            self.play_btn.config(text="▶播放", bg="#4CAF50")
            self.info_label.config(text="📭 列表已清空")
            self.progress.set(0)
            self.time_label.config(text="00:00")
            self.duration_label.config(text="00:00")
            self.current_position = 0
            self.current_index = -1
            self.status_label.config(text="🗑 已清空")
            if self.timer_id:
                self.root.after_cancel(self.timer_id)

            # 删除保存文件
            if os.path.exists(self.PLAYLIST_FILE):
                os.remove(self.PLAYLIST_FILE)

    def cleanup(self):
        """关闭窗口时清理资源"""
        # 关闭前保存播放列表
        self.save_playlist()

        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        self.root.destroy()


# ==================== 程序入口 ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()