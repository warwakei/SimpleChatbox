import tkinter as tk
from tkinter import ttk
import threading

from media_engine_client import MediaEngineClient
from vrchat_chatbox import VRChatChatbox
from system_info import SystemInfo
from config import Config


class SimpleChatboxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SimpleChatbox")
        self.root.geometry("650x850")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f0f0f")
        
        # Аутлайн окна с градиентом
        self.root.attributes('-alpha', 0.99)
        self.root.overrideredirect(False)
        
        self.config = Config()
        self.media_client = MediaEngineClient()
        self.vrchat = VRChatChatbox(
            ip=self.config.get('vrchat_ip'),
            port=self.config.get('vrchat_port')
        )
        self.system_info = SystemInfo()
        self.current_track = None
        self.auto_send_enabled = False
        
        self.setup_styles()
        self.create_ui()
        self.setup_timers()
        self.check_connection()
    
    def create_gradient_line(self, parent, height: int = 2) -> tk.Frame:
        """Создать линию с градиентом от accent к accent_light"""
        frame = tk.Frame(parent, height=height, bg=self.bg_primary)
        frame.pack(fill=tk.X)
        frame.pack_propagate(False)
        
        canvas = tk.Canvas(frame, height=height, bg=self.bg_primary, highlightthickness=0, bd=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        width = 600
        steps = 50
        for i in range(steps):
            ratio = i / steps
            r1, g1, b1 = int(0xb8), int(0x95), int(0x6a)
            r2, g2, b2 = int(0xd4), int(0xc5), int(0xa9)
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            x = (width / steps) * i
            canvas.create_line(x, 0, x + (width / steps), height, fill=color, width=2)
        
        return frame
    
    def setup_styles(self):
        
        self.bg_primary = "#0f0f0f"
        self.bg_secondary = "#1a1a1a"
        self.bg_tertiary = "#252525"
        self.accent = "#b8956a"
        self.accent_light = "#d4c5a9"
        self.text_primary = "#e8e8e8"
        self.text_secondary = "#a8a8a8"
        self.border = "#b8956a"
        
        self.root.configure(bg=self.bg_primary)
        
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("TFrame", background=self.bg_primary, relief="flat", borderwidth=0)
        style.configure("TLabel", background=self.bg_primary, foreground=self.text_primary, font=("Consolas", 9))
        style.configure("TButton", background=self.bg_secondary, foreground=self.text_primary, font=("Consolas", 9), relief="flat", padding=8, borderwidth=0)
        style.map("TButton", background=[("active", self.bg_tertiary)], foreground=[("active", self.accent)], relief=[("pressed", "flat")])
        style.configure("TCheckbutton", background=self.bg_primary, foreground=self.text_primary, font=("Consolas", 9), focuscolor="none")
        style.map("TCheckbutton", background=[("active", self.bg_primary)], foreground=[("active", self.text_primary)])
        style.configure("TRadiobutton", background=self.bg_primary, foreground=self.text_primary, font=("Consolas", 9), focuscolor="none")
        style.map("TRadiobutton", background=[("active", self.bg_primary)], foreground=[("active", self.text_primary)])
        style.configure("TEntry", fieldbackground=self.bg_secondary, background=self.bg_secondary, foreground=self.text_primary, font=("Consolas", 9), relief="flat", borderwidth=2, fieldrelief="flat", insertcolor=self.accent)
        style.configure("TSpinbox", fieldbackground=self.bg_secondary, background=self.bg_secondary, foreground=self.text_primary, font=("Consolas", 9), relief="flat", borderwidth=2, fieldrelief="flat", insertcolor=self.accent)
        style.configure("TNotebook", background=self.bg_primary, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.bg_secondary, foreground=self.text_secondary, font=("Consolas", 8), padding=[8, 4], borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", self.bg_primary)], foreground=[("selected", self.accent)])
        style.configure("TLabelframe", background=self.bg_primary, foreground=self.text_primary, font=("Consolas", 9, "bold"), borderwidth=2, relief="flat")
        style.configure("TLabelframe.Label", background=self.bg_primary, foreground=self.accent, font=("Consolas", 9, "bold"))
    
    def create_ui(self):
        """Создать основной интерфейс"""
        main_frame = tk.Frame(self.root, bg=self.bg_primary)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Автоотправка
        auto_frame = tk.Frame(main_frame, bg=self.bg_primary, height=30)
        auto_frame.pack(fill=tk.X, padx=12, pady=(8, 0))
        auto_frame.pack_propagate(False)
        
        self.auto_send_var = tk.BooleanVar()
        auto_check = ttk.Checkbutton(auto_frame, text="Auto-send every (ms):", 
                                     variable=self.auto_send_var, 
                                     command=self.toggle_auto_send)
        auto_check.pack(side=tk.LEFT, anchor=tk.W)
        
        self.delay_spinbox = ttk.Spinbox(auto_frame, from_=100, to=60000, width=8, justify=tk.CENTER)
        self.delay_spinbox.set(self.config.get('auto_send_delay', 3000))
        self.delay_spinbox.pack(side=tk.LEFT, padx=(8, 0))
        
        # Preview панель с толстым золотым аутлайном
        preview_frame = tk.Frame(main_frame, bg=self.bg_primary, relief=tk.FLAT, bd=0)
        preview_frame.pack(fill=tk.BOTH, expand=False, padx=12, pady=(12, 0))
        
        preview_border = tk.Frame(preview_frame, bg=self.border, height=3)
        preview_border.pack(fill=tk.X)
        self.create_gradient_line(preview_frame, 3)
        
        preview_label = tk.Label(preview_frame, text="Preview", fg=self.accent, bg=self.bg_primary, 
                                font=("Consolas", 10, "bold"), padx=10, pady=8)
        preview_label.pack(anchor=tk.W)
        
        content_frame = tk.Frame(preview_frame, bg=self.bg_secondary, relief=tk.FLAT, bd=0)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        inner_content = tk.Frame(content_frame, bg=self.bg_secondary)
        inner_content.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        self.track_label = tk.Label(inner_content, text="No track playing", 
                                    fg=self.accent, bg=self.bg_secondary, 
                                    font=("Consolas", 10), wraplength=550, justify=tk.CENTER)
        self.track_label.pack(fill=tk.X, pady=(0, 8), expand=True)
        
        self.sys_label = tk.Label(inner_content, text="", fg=self.accent_light, bg=self.bg_secondary,
                                 font=("Consolas", 8), wraplength=550, justify=tk.CENTER)
        self.sys_label.pack(fill=tk.X, expand=True)
        
        preview_border_bottom = tk.Frame(preview_frame, bg=self.border, height=2)
        preview_border_bottom.pack(fill=tk.X)
        
        # Кнопки управления
        button_frame = tk.Frame(main_frame, bg=self.bg_primary, height=40)
        button_frame.pack(fill=tk.X, padx=12, pady=(8, 0))
        button_frame.pack_propagate(False)
        
        send_btn = ttk.Button(button_frame, text="Send to VRChat", command=self.send_to_vrchat)
        send_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        refresh_btn = ttk.Button(button_frame, text="Refresh", command=self.refresh_track)
        refresh_btn.pack(side=tk.LEFT)
        
        # Табы для настроек
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=(8, 0))
        
        music_tab = tk.Frame(notebook, bg=self.bg_primary)
        notebook.add(music_tab, text="MusicMSG")
        self.create_music_tab(music_tab)
        
        status_tab = tk.Frame(notebook, bg=self.bg_primary)
        notebook.add(status_tab, text="StatusMSG")
        self.create_status_tab(status_tab)
        
        time_tab = tk.Frame(notebook, bg=self.bg_primary)
        notebook.add(time_tab, text="TimeMSG")
        self.create_time_tab(time_tab)
        
        sys_tab = tk.Frame(notebook, bg=self.bg_primary)
        notebook.add(sys_tab, text="SysMSG")
        self.create_sys_tab(sys_tab)
        
        advanced_tab = tk.Frame(notebook, bg=self.bg_primary)
        notebook.add(advanced_tab, text="CFG")
        self.create_advanced_tab(advanced_tab)
        
        about_tab = tk.Frame(notebook, bg=self.bg_primary)
        notebook.add(about_tab, text="About")
        self.create_about_tab(about_tab)
    
    def create_scrollable_tab(self, parent):
        """Создать прокручиваемый таб"""
        canvas = tk.Canvas(parent, bg=self.bg_primary, highlightthickness=0, bd=0)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_primary)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=lambda *args: None, bg=self.bg_primary, bd=0, highlightthickness=0)
        
        canvas.pack(side="left", fill="both", expand=True)
        
        return scrollable_frame
    
    def create_music_tab(self, parent):
        """Таб для настроек музыки"""
        scrollable_frame = self.create_scrollable_tab(parent)
        
        frame_inner = tk.Frame(scrollable_frame, bg=self.bg_primary)
        frame_inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        # Статус подключения
        status_frame = tk.Frame(frame_inner, bg=self.bg_primary, height=30)
        status_frame.pack(fill=tk.X, pady=(0, 12))
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="Connecting to MediaEngine...", 
                                     fg=self.accent, bg=self.bg_primary, font=("Consolas", 9, "bold"), wraplength=300)
        self.status_label.pack(side=tk.LEFT, anchor=tk.W)
        
        format_frame = tk.Frame(frame_inner, bg=self.bg_secondary, relief=tk.FLAT, bd=0)
        format_frame.pack(fill=tk.X, pady=(0, 12))
        
        format_border = tk.Frame(format_frame, bg=self.border, height=2)

        
        format_border.pack(fill=tk.X)

        
        self.create_gradient_line(format_frame, 2)
        self.create_gradient_line(format_frame, 2)
        
        format_label = tk.Label(format_frame, text="Message Format", fg=self.accent, bg=self.bg_secondary, 
                               font=("Consolas", 9, "bold"), padx=10, pady=6)
        format_label.pack(anchor=tk.W)
        
        format_content = tk.Frame(format_frame, bg=self.bg_secondary)
        format_content.pack(fill=tk.X, padx=8, pady=(0, 8))
        
        ttk.Label(format_content, text="Select format:").pack(anchor=tk.W, pady=(0, 6))
        
        self.format_var = tk.StringVar(value=self.config.get('format', 'display'))
        formats = [
            ("Display (from API)", "display"),
            ("Artist - Track", "artist_track"),
            ("Track - Artist", "track_artist"),
            ("Track by Artist", "track_by_artist"),
            ("Track only", "track_only"),
        ]
        
        for text, value in formats:
            ttk.Radiobutton(format_content, text=text, variable=self.format_var, 
                           value=value, command=self.on_format_changed).pack(anchor=tk.W, pady=2)
        
        icons_frame = tk.Frame(frame_inner, bg=self.bg_secondary, relief=tk.FLAT, bd=0)
        icons_frame.pack(fill=tk.X)
        
        icons_border = tk.Frame(icons_frame, bg=self.border, height=2)

        
        icons_border.pack(fill=tk.X)

        
        self.create_gradient_line(icons_frame, 2)

        
        self.create_gradient_line(icons_frame, 2)
        self.create_gradient_line(icons_frame, 2)
        
        icons_label = tk.Label(icons_frame, text="Status Icons", fg=self.accent, bg=self.bg_secondary, 
                              font=("Consolas", 9, "bold"), padx=10, pady=6)
        icons_label.pack(anchor=tk.W)
        
        icons_content = tk.Frame(icons_frame, bg=self.bg_secondary)
        icons_content.pack(fill=tk.X, padx=8, pady=(0, 8))
        
        self.show_icon_var = tk.BooleanVar(value=self.config.get('show_status_icon', True))
        ttk.Checkbutton(icons_content, text="Show status icon", variable=self.show_icon_var,
                       command=self.on_show_icon_changed).pack(anchor=tk.W, pady=(0, 8))
        
        playing_frame = tk.Frame(icons_content, bg=self.bg_secondary)
        playing_frame.pack(fill=tk.X, pady=4)
        ttk.Label(playing_frame, text="Playing icon:").pack(side=tk.LEFT)
        self.playing_icon_var = tk.StringVar(value=self.config.get('playing_icon', '▶'))
        ttk.Entry(playing_frame, textvariable=self.playing_icon_var, width=5).pack(side=tk.LEFT, padx=(8, 0))
        self.playing_icon_var.trace('w', lambda *args: self.on_playing_icon_changed())
        
        paused_frame = tk.Frame(icons_content, bg=self.bg_secondary)
        paused_frame.pack(fill=tk.X, pady=4)
        ttk.Label(paused_frame, text="Paused icon:").pack(side=tk.LEFT)
        self.paused_icon_var = tk.StringVar(value=self.config.get('paused_icon', '⏸'))
        ttk.Entry(paused_frame, textvariable=self.paused_icon_var, width=5).pack(side=tk.LEFT, padx=(8, 0))
        self.paused_icon_var.trace('w', lambda *args: self.on_paused_icon_changed())
    
    def create_status_tab(self, parent):
        """Таб для пользовательского статус сообщения"""
        scrollable_frame = self.create_scrollable_tab(parent)
        
        frame_inner = tk.Frame(scrollable_frame, bg=self.bg_primary)
        frame_inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        self.show_status_var = tk.BooleanVar(value=self.config.get('show_status_msg', False))
        ttk.Checkbutton(frame_inner, text="Show custom status message", variable=self.show_status_var,
                       command=self.on_show_status_changed).pack(anchor=tk.W, pady=(0, 12))
        
        msg_frame = tk.Frame(frame_inner, bg=self.bg_primary)
        msg_frame.pack(fill=tk.X, pady=(0, 12))
        ttk.Label(msg_frame, text="Status message:").pack(side=tk.LEFT)
        self.status_msg_var = tk.StringVar(value=self.config.get('status_msg', ''))
        ttk.Entry(msg_frame, textvariable=self.status_msg_var, width=40).pack(side=tk.LEFT, padx=(8, 0), fill=tk.X, expand=True)
        self.status_msg_var.trace('w', lambda *args: self.on_status_msg_changed())
        
        position_frame = tk.Frame(frame_inner, bg=self.bg_secondary, relief=tk.FLAT, bd=0)
        position_frame.pack(fill=tk.X, pady=(0, 12))
        
        position_border = tk.Frame(position_frame, bg=self.border, height=2)

        
        position_border.pack(fill=tk.X)

        
        self.create_gradient_line(position_frame, 2)

        
        self.create_gradient_line(position_frame, 2)
        
        position_label = tk.Label(position_frame, text="Message Position", fg=self.accent, bg=self.bg_secondary, 
                                 font=("Consolas", 9, "bold"), padx=10, pady=6)
        position_label.pack(anchor=tk.W)
        
        position_content = tk.Frame(position_frame, bg=self.bg_secondary)
        position_content.pack(fill=tk.X, padx=8, pady=(0, 8))
        
        self.status_position_var = tk.StringVar(value=self.config.get('status_position', 'after_music'))
        positions = [
            ("Before everything", "before_all"),
            ("After MusicMSG", "after_music"),
            ("After SysMSG", "after_sys"),
            ("At the end", "at_end"),
        ]
        
        for text, value in positions:
            ttk.Radiobutton(position_content, text=text, variable=self.status_position_var, 
                           value=value, command=self.on_status_position_changed).pack(anchor=tk.W, pady=2)
        
        conditions_frame = tk.Frame(frame_inner, bg=self.bg_secondary, relief=tk.FLAT, bd=0)
        conditions_frame.pack(fill=tk.X, pady=(12, 0))
        
        conditions_border = tk.Frame(conditions_frame, bg=self.border, height=2)

        
        conditions_border.pack(fill=tk.X)

        
        self.create_gradient_line(conditions_frame, 2)

        
        self.create_gradient_line(conditions_frame, 2)
        
        conditions_label = tk.Label(conditions_frame, text="Show only if", fg=self.accent, bg=self.bg_secondary, 
                                   font=("Consolas", 9, "bold"), padx=10, pady=6)
        conditions_label.pack(anchor=tk.W)
        
        conditions_content = tk.Frame(conditions_frame, bg=self.bg_secondary)
        conditions_content.pack(fill=tk.X, padx=8, pady=(0, 8))
        
        self.status_if_music_var = tk.BooleanVar(value=self.config.get('status_if_music', True))
        ttk.Checkbutton(conditions_content, text="MusicMSG is enabled", variable=self.status_if_music_var,
                       command=self.on_status_condition_changed).pack(anchor=tk.W, pady=2)
        
        self.status_if_sys_var = tk.BooleanVar(value=self.config.get('status_if_sys', False))
        ttk.Checkbutton(conditions_content, text="SysMSG is enabled", variable=self.status_if_sys_var,
                       command=self.on_status_condition_changed).pack(anchor=tk.W, pady=2)
    
    def create_time_tab(self, parent):
        """Таб для времени"""
        import datetime
        import pytz
        
        scrollable_frame = self.create_scrollable_tab(parent)
        
        frame_inner = tk.Frame(scrollable_frame, bg=self.bg_primary)
        frame_inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        self.show_time_var = tk.BooleanVar(value=self.config.get('show_time_msg', False))
        ttk.Checkbutton(frame_inner, text="Show time in message", variable=self.show_time_var,
                       command=self.on_show_time_changed).pack(anchor=tk.W, pady=(0, 12))
        

        
        time_format_frame = tk.Frame(frame_inner, bg=self.bg_secondary, relief=tk.FLAT, bd=0)
        time_format_frame.pack(fill=tk.X, pady=(0, 12))
        
        self.create_gradient_line(time_format_frame, 2)
        
        time_format_label = tk.Label(time_format_frame, text="Time Format", fg=self.accent, bg=self.bg_secondary, 
                                     font=("Consolas", 9, "bold"), padx=10, pady=6)
        time_format_label.pack(anchor=tk.W)
        
        time_format_content = tk.Frame(time_format_frame, bg=self.bg_secondary)
        time_format_content.pack(fill=tk.X, padx=8, pady=(0, 8))
        
        self.time_format_var = tk.StringVar(value=self.config.get('time_format', 'auto'))
        
        ttk.Radiobutton(time_format_content, text="Auto (use PC time)", variable=self.time_format_var, 
                       value="auto", command=self.on_time_format_changed).pack(anchor=tk.W, pady=2)
        
        custom_frame = tk.Frame(time_format_content, bg=self.bg_secondary)
        custom_frame.pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(custom_frame, text="Custom time (HH:MM):", variable=self.time_format_var, 
                       value="custom", command=self.on_time_format_changed).pack(side=tk.LEFT)
        
        self.time_custom_var = tk.StringVar(value=self.config.get('time_custom', ''))
        self.time_start_offset: int = 0
        time_entry = ttk.Entry(custom_frame, textvariable=self.time_custom_var, width=10)
        time_entry.pack(side=tk.LEFT, padx=(8, 0))
        time_entry.bind('<Return>', self.on_time_custom_enter)
        
        hint_label = tk.Label(custom_frame, text="(press Enter to start)", fg=self.text_secondary, 
                             bg=self.bg_secondary, font=("Consolas", 7))
        hint_label.pack(side=tk.LEFT, padx=(4, 0))
        
        self.time_custom_var.trace('w', lambda *args: self.on_time_format_changed())
        
        position_frame = tk.Frame(frame_inner, bg=self.bg_secondary, relief=tk.FLAT, bd=0)
        position_frame.pack(fill=tk.X, pady=(0, 12))
        
        position_border = tk.Frame(position_frame, bg=self.border, height=2)

        
        position_border.pack(fill=tk.X)

        
        self.create_gradient_line(position_frame, 2)

        
        self.create_gradient_line(position_frame, 2)
        
        position_label = tk.Label(position_frame, text="Message Position", fg=self.accent, bg=self.bg_secondary, 
                                 font=("Consolas", 9, "bold"), padx=10, pady=6)
        position_label.pack(anchor=tk.W)
        
        position_content = tk.Frame(position_frame, bg=self.bg_secondary)
        position_content.pack(fill=tk.X, padx=8, pady=(0, 8))
        
        self.time_position_var = tk.StringVar(value=self.config.get('time_position', 'at_end'))
        positions = [
            ("Before everything", "before_all"),
            ("After MusicMSG", "after_music"),
            ("After StatusMSG", "after_status"),
            ("After SysMSG", "after_sys"),
            ("At the end", "at_end"),
        ]
        
        for text, value in positions:
            ttk.Radiobutton(position_content, text=text, variable=self.time_position_var, 
                           value=value, command=self.on_time_position_changed).pack(anchor=tk.W, pady=2)
    
    def create_sys_tab(self, parent):
        """Таб для системной информации"""
        scrollable_frame = self.create_scrollable_tab(parent)
        
        frame_inner = tk.Frame(scrollable_frame, bg=self.bg_primary)
        frame_inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        self.show_sys_var = tk.BooleanVar(value=self.config.get('show_sys_msg', False))
        ttk.Checkbutton(frame_inner, text="Show system info in message", variable=self.show_sys_var,
                       command=self.on_show_sys_changed).pack(anchor=tk.W, pady=(0, 12))
        
        sep_frame = tk.Frame(frame_inner, bg=self.bg_primary)
        sep_frame.pack(fill=tk.X, pady=(0, 12))
        ttk.Label(sep_frame, text="Message separator:").pack(side=tk.LEFT)
        self.separator_var = tk.StringVar(value=self.config.get('sys_msg_separator', ' | '))
        ttk.Entry(sep_frame, textvariable=self.separator_var, width=15).pack(side=tk.LEFT, padx=(8, 0))
        self.separator_var.trace('w', lambda *args: self.on_separator_changed())
        
        display_frame = tk.Frame(frame_inner, bg=self.bg_secondary, relief=tk.FLAT, bd=0)
        display_frame.pack(fill=tk.X)
        
        display_border = tk.Frame(display_frame, bg=self.border, height=2)

        
        display_border.pack(fill=tk.X)

        
        self.create_gradient_line(display_frame, 2)

        
        self.create_gradient_line(display_frame, 2)
        
        display_label = tk.Label(display_frame, text="What to Display", fg=self.accent, bg=self.bg_secondary, 
                                font=("Consolas", 9, "bold"), padx=10, pady=6)
        display_label.pack(anchor=tk.W)
        
        display_content = tk.Frame(display_frame, bg=self.bg_secondary)
        display_content.pack(fill=tk.X, padx=8, pady=(0, 8))
        
        self.show_cpu_var = tk.BooleanVar(value=self.config.get('show_cpu_usage', True))
        ttk.Checkbutton(display_content, text="CPU Usage", variable=self.show_cpu_var,
                       command=self.on_cpu_usage_changed).pack(anchor=tk.W, pady=2)
        
        self.show_ram_var = tk.BooleanVar(value=self.config.get('show_ram_usage', True))
        ttk.Checkbutton(display_content, text="RAM Usage", variable=self.show_ram_var,
                       command=self.on_ram_usage_changed).pack(anchor=tk.W, pady=2)
        
        self.show_cpu_temp_var = tk.BooleanVar(value=self.config.get('show_cpu_temp', True))
        ttk.Checkbutton(display_content, text="CPU Temperature", variable=self.show_cpu_temp_var,
                       command=self.on_cpu_temp_changed).pack(anchor=tk.W, pady=2)
        
        self.show_gpu_temp_var = tk.BooleanVar(value=self.config.get('show_gpu_temp', True))
        ttk.Checkbutton(display_content, text="GPU Temperature", variable=self.show_gpu_temp_var,
                       command=self.on_gpu_temp_changed).pack(anchor=tk.W, pady=2)
    
    def create_advanced_tab(self, parent):
        """Таб для конфигурации"""
        scrollable_frame = self.create_scrollable_tab(parent)
        
        frame_inner = tk.Frame(scrollable_frame, bg=self.bg_primary)
        frame_inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        media_frame = tk.Frame(frame_inner, bg=self.bg_primary)
        media_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(media_frame, text="MediaEngine URL:").pack(side=tk.LEFT)
        self.media_url_var = tk.StringVar(value=self.config.get('media_engine_url', 'http://localhost:5000'))
        ttk.Entry(media_frame, textvariable=self.media_url_var, width=35).pack(side=tk.LEFT, padx=(8, 0))
        self.media_url_var.trace('w', lambda *args: self.on_media_url_changed())
        
        ip_frame = tk.Frame(frame_inner, bg=self.bg_primary)
        ip_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(ip_frame, text="VRChat IP:").pack(side=tk.LEFT)
        self.vrchat_ip_var = tk.StringVar(value=self.config.get('vrchat_ip', '127.0.0.1'))
        ttk.Entry(ip_frame, textvariable=self.vrchat_ip_var, width=20).pack(side=tk.LEFT, padx=(8, 0))
        self.vrchat_ip_var.trace('w', lambda *args: self.on_vrchat_ip_changed())
        
        port_frame = tk.Frame(frame_inner, bg=self.bg_primary)
        port_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(port_frame, text="VRChat Port:").pack(side=tk.LEFT)
        self.vrchat_port_var = tk.StringVar(value=str(self.config.get('vrchat_port', 9000)))
        ttk.Spinbox(port_frame, from_=1, to=65535, textvariable=self.vrchat_port_var, width=10).pack(side=tk.LEFT, padx=(8, 0))
        self.vrchat_port_var.trace('w', lambda *args: self.on_vrchat_port_changed())
        
        sep = tk.Frame(frame_inner, height=2, bg=self.border)
        sep.pack(fill=tk.X, pady=12)
        self.create_gradient_line(frame_inner, 2)
        
        save_label = tk.Label(frame_inner, text="Configuration", fg=self.accent, bg=self.bg_primary, 
                             font=("Consolas", 9, "bold"), padx=10, pady=6)
        save_label.pack(anchor=tk.W)
        
        save_btn = tk.Button(frame_inner, text="Save All Settings to Config", 
                            command=self.save_all_settings,
                            bg=self.bg_secondary, fg=self.accent, 
                            font=("Consolas", 9), relief=tk.FLAT, 
                            padx=12, pady=8, cursor="hand2",
                            activebackground=self.bg_tertiary, activeforeground=self.accent_light)
        save_btn.pack(fill=tk.X, pady=(8, 0))
    
    def create_about_tab(self, parent):
        """Таб информации о приложении"""
        scrollable_frame = self.create_scrollable_tab(parent)
        
        frame_inner = tk.Frame(scrollable_frame, bg=self.bg_primary)
        frame_inner.pack(fill=tk.BOTH, expand=True)
        
        center_frame = tk.Frame(frame_inner, bg=self.bg_primary)
        center_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20, anchor=tk.CENTER)
        
        spacer1 = tk.Frame(center_frame, bg=self.bg_primary)
        spacer1.pack(fill=tk.BOTH, expand=True)
        
        content_frame = tk.Frame(center_frame, bg=self.bg_primary)
        content_frame.pack(anchor=tk.CENTER, expand=False)
        
        icon_label = tk.Label(content_frame, text="🎵", font=("Arial", 48), bg=self.bg_primary, fg=self.accent)
        icon_label.pack(pady=(0, 12))
        
        title_label = tk.Label(content_frame, text="SimpleChatbox", font=("Consolas", 18, "bold"), 
                              bg=self.bg_primary, fg=self.accent)
        title_label.pack()
        
        version_label = tk.Label(content_frame, text="v0.0.2", font=("Consolas", 9), 
                                bg=self.bg_primary, fg=self.accent_light)
        version_label.pack()
        
        desc_label = tk.Label(content_frame, text="VRChat Music Display Utility", 
                             font=("Consolas", 9), bg=self.bg_primary, fg=self.text_secondary)
        desc_label.pack(pady=(4, 16))
        
        sep = tk.Frame(content_frame, height=2, bg=self.border)
        sep.pack(fill=tk.X, pady=12, padx=20)
        self.create_gradient_line(content_frame, 2)
        
        info_frame = tk.Frame(content_frame, bg=self.bg_primary)
        info_frame.pack(fill=tk.X, pady=10, padx=20)
        
        info_text = """Displays currently playing media from your PC
in VRChat chatbox via OSC protocol.

Integrates with warwakei Media Engine
to fetch track information and system stats."""
        
        info_label = tk.Label(info_frame, text=info_text, font=("Consolas", 8),
                             bg=self.bg_primary, fg=self.text_secondary, justify=tk.CENTER, wraplength=300)
        info_label.pack()
        
        sep2 = tk.Frame(content_frame, height=2, bg=self.border)
        sep2.pack(fill=tk.X, pady=12, padx=20)
        self.create_gradient_line(content_frame, 2)
        
        dev_label = tk.Label(content_frame, text="Developer", font=("Consolas", 8),
                            bg=self.bg_primary, fg=self.text_secondary)
        dev_label.pack(pady=(16, 0))
        
        author_label = tk.Label(content_frame, text="warwakei", font=("Consolas", 11, "bold"),
                               bg=self.bg_primary, fg=self.accent)
        author_label.pack(pady=(2, 12))
        
        links_frame = tk.Frame(content_frame, bg=self.bg_primary)
        links_frame.pack(fill=tk.X, pady=8, padx=20)
        
        links = [
            ("GitHub Profile", "https://github.com/warwakei"),
            ("MediaEngine", "https://github.com/warwakei/MediaEngine"),
            ("SimpleChatbox", "https://github.com/warwakei/SimpleChatbox")
        ]
        
        for text, url in links:
            btn = tk.Button(links_frame, text=f"→ {text}", 
                           command=lambda u=url: self.open_link(u),
                           bg=self.bg_secondary, fg=self.accent, 
                           font=("Consolas", 8), relief=tk.FLAT, 
                           padx=10, pady=5, cursor="hand2",
                           activebackground=self.bg_tertiary, activeforeground=self.accent_light,
                           bd=2, highlightthickness=0, highlightcolor=self.border)
            btn.pack(fill=tk.X, pady=2)
        
        sep3 = tk.Frame(content_frame, height=2, bg=self.border)
        sep3.pack(fill=tk.X, pady=12)
        self.create_gradient_line(content_frame, 2)
        
        license_label = tk.Label(content_frame, text="MIT License", font=("Consolas", 7),
                                bg=self.bg_primary, fg=self.text_secondary)
        license_label.pack()
        
        spacer2 = tk.Frame(center_frame, bg=self.bg_primary)
        spacer2.pack(fill=tk.BOTH, expand=True)
    
    def open_link(self, url):
        """Открыть ссылку в браузере"""
        import webbrowser
        webbrowser.open(url)
    
    def setup_timers(self):
        """Настроить таймеры"""
        self.check_timer()
        self.auto_timer()
    
    def check_timer(self):
        """Проверить подключение каждую секунду"""
        self.check_connection()
        self.root.after(1000, self.check_timer)
    
    def auto_timer(self):
        """Таймер для автоотправки"""
        if self.auto_send_enabled:
            self.auto_send_track()
        self.root.after(100, self.auto_timer)
    
    def check_connection(self):
        """Проверить подключение к MediaEngine"""
        def check():
            status = self.media_client.get_status()
            if status:
                self.status_label.config(text="✓ Connected to MediaEngine", fg=self.accent)
                self.refresh_track()
            else:
                self.status_label.config(text="✗ Cannot connect to MediaEngine", fg=self.accent_light)
        
        threading.Thread(target=check, daemon=True).start()
    
    def refresh_track(self):
        """Обновить информацию о треке"""
        def fetch():
            track = self.media_client.get_current_track()
            if track:
                self.on_track_updated(track)
        
        threading.Thread(target=fetch, daemon=True).start()
    
    def on_track_updated(self, track):
        """Обновить отображение трека"""
        self.current_track = track
        self.update_preview()
    
    def update_preview(self):
        """Обновить preview с точным сообщением для VRChat"""
        import datetime
        
        if not self.current_track:
            self.track_label.config(text="No track playing")
            return
        
        parts = []
        
        if self.status_position_var.get() == "before_all" and self.show_status_var.get() and self._check_status_conditions():
            parts.append(self.status_msg_var.get())
        
        if self.time_position_var.get() == "before_all" and self.show_time_var.get():
            parts.append(self._get_time_string())
        
        music_msg = self.vrchat.format_track_message(self.current_track, self.config)
        parts.append(music_msg)
        
        if self.status_position_var.get() == "after_music" and self.show_status_var.get() and self._check_status_conditions():
            parts.append(self.status_msg_var.get())
        
        if self.time_position_var.get() == "after_music" and self.show_time_var.get():
            parts.append(self._get_time_string())
        
        if self.time_position_var.get() == "after_status" and self.show_time_var.get():
            parts.append(self._get_time_string())
        
        if self.show_sys_var.get():
            sys_msg = self.system_info.format_sys_message(self.config)
            parts.append(sys_msg)
        
        if self.status_position_var.get() == "after_sys" and self.show_status_var.get() and self._check_status_conditions():
            parts.append(self.status_msg_var.get())
        
        if self.time_position_var.get() == "after_sys" and self.show_time_var.get():
            parts.append(self._get_time_string())
        
        if self.status_position_var.get() == "at_end" and self.show_status_var.get() and self._check_status_conditions():
            parts.append(self.status_msg_var.get())
        
        if self.time_position_var.get() == "at_end" and self.show_time_var.get():
            parts.append(self._get_time_string())
        
        full_message = " | ".join(parts)
        self.track_label.config(text=full_message)
        self._animate_preview()
    
    def _animate_preview(self):
        """Анимация обновления preview"""
        original_fg = self.track_label.cget("foreground")
        self.track_label.config(foreground=self.accent_light)
        self.root.after(150, lambda: self.track_label.config(foreground=original_fg))
    
    def _get_time_string(self) -> str:
        """Получить строку времени"""
        import datetime
        
        time_format = self.time_format_var.get()
        
        if time_format == "custom":
            custom_time = self.time_custom_var.get().strip()
            if custom_time and ':' in custom_time:
                try:
                    start_h, start_m = map(int, custom_time.split(':'))
                    current_time = datetime.datetime.now()
                    elapsed = (current_time - self.time_start_time).total_seconds() if hasattr(self, 'time_start_time') else 0
                    
                    total_minutes = start_h * 60 + start_m + int(elapsed // 60)
                    hours = (total_minutes // 60) % 24
                    minutes = total_minutes % 60
                    return f"{hours:02d}:{minutes:02d}"
                except (ValueError, AttributeError):
                    return custom_time
        
        return datetime.datetime.now().strftime('%H:%M')
    
    def _check_status_conditions(self) -> bool:
        """Проверить условия для показа StatusMSG"""
        if self.status_if_music_var.get() and not hasattr(self, 'current_track'):
            return False
        if self.status_if_sys_var.get() and not self.show_sys_var.get():
            return False
        return True
    
    def send_to_vrchat(self):
        """Отправить текущий трек в VRChat"""
        if self.current_track:
            message = self.vrchat.format_track_message(self.current_track, self.config)
            
            if self.show_sys_var.get():
                sys_msg = self.system_info.format_sys_message(self.config)
                separator = self.config.get('sys_msg_separator', ' | ')
                message = f"{message}{separator}{sys_msg}"
            
            if self.vrchat.send_message(message):
                self.status_label.config(text="✓ Sent to VRChat", fg=self.accent)
            else:
                self.status_label.config(text="✗ Failed to send to VRChat", fg=self.accent_light)
    
    def toggle_auto_send(self):
        """Включить/выключить автоотправку"""
        self.auto_send_enabled = self.auto_send_var.get()
    
    def auto_send_track(self):
        """Автоматически отправить трек"""
        if self.auto_send_enabled:
            self.refresh_track()
            if self.current_track:
                self.send_to_vrchat()
    
    def on_format_changed(self):
        self.config.set('format', self.format_var.get())
        self.update_preview()
    
    def on_show_icon_changed(self):
        self.config.set('show_status_icon', self.show_icon_var.get())
        self.update_preview()
    
    def on_playing_icon_changed(self):
        self.config.set('playing_icon', self.playing_icon_var.get())
        self.update_preview()
    
    def on_paused_icon_changed(self):
        self.config.set('paused_icon', self.paused_icon_var.get())
        self.update_preview()
    
    def on_show_sys_changed(self):
        self.config.set('show_sys_msg', self.show_sys_var.get())
        self.update_preview()
    
    def on_separator_changed(self):
        self.config.set('sys_msg_separator', self.separator_var.get())
        self.update_preview()
    
    def on_cpu_usage_changed(self):
        self.config.set('show_cpu_usage', self.show_cpu_var.get())
        self.update_preview()
    
    def on_ram_usage_changed(self):
        self.config.set('show_ram_usage', self.show_ram_var.get())
        self.update_preview()
    
    def on_cpu_temp_changed(self):
        self.config.set('show_cpu_temp', self.show_cpu_temp_var.get())
        self.update_preview()
    
    def on_gpu_temp_changed(self):
        self.config.set('show_gpu_temp', self.show_gpu_temp_var.get())
        self.update_preview()
    
    def on_show_status_changed(self):
        self.config.set('show_status_msg', self.show_status_var.get())
        self.update_preview()
    
    def on_status_msg_changed(self):
        self.config.set('status_msg', self.status_msg_var.get())
        self.update_preview()
    
    def on_status_position_changed(self):
        self.config.set('status_position', self.status_position_var.get())
        self.update_preview()
    
    def on_status_sep_changed(self):
        self.config.set('status_sep_before', self.status_sep_before_var.get())
        self.config.set('status_sep_after', self.status_sep_after_var.get())
        self.update_preview()
    
    def on_status_condition_changed(self):
        self.config.set('status_if_music', self.status_if_music_var.get())
        self.config.set('status_if_sys', self.status_if_sys_var.get())
        self.update_preview()
    
    def on_show_time_changed(self):
        self.config.set('show_time_msg', self.show_time_var.get())
        self.update_preview()
    
    
    
    def on_time_format_changed(self):
        self.config.set('time_format', self.time_format_var.get())
        if self.time_format_var.get() == 'custom':
            self.config.set('time_custom', self.time_custom_var.get())
        self.update_preview()
    
    def on_time_custom_enter(self, event) -> None:
        """Начать отсчёт времени с введённого значения"""
        import datetime
        custom_time = self.time_custom_var.get().strip()
        if custom_time and ':' in custom_time:
            try:
                h, m = map(int, custom_time.split(':'))
                if 0 <= h < 24 and 0 <= m < 60:
                    self.time_start_time = datetime.datetime.now()
                    self.time_format_var.set('custom')
                    self.update_preview()
            except ValueError:
                pass
    
    def on_time_position_changed(self):
        self.config.set('time_position', self.time_position_var.get())
        self.update_preview()
    
    def on_time_sep_changed(self):
        self.config.set('time_sep_before', self.time_sep_before_var.get())
        self.config.set('time_sep_after', self.time_sep_after_var.get())
        self.update_preview()
    
    def on_media_url_changed(self):
        self.config.set('media_engine_url', self.media_url_var.get())
        self.media_client = MediaEngineClient(self.media_url_var.get())
    
    def on_vrchat_ip_changed(self):
        self.config.set('vrchat_ip', self.vrchat_ip_var.get())
        self.vrchat = VRChatChatbox(self.vrchat_ip_var.get(), int(self.vrchat_port_var.get()))
    
    def on_vrchat_port_changed(self):
        try:
            port = int(self.vrchat_port_var.get())
            self.config.set('vrchat_port', port)
            self.vrchat = VRChatChatbox(self.vrchat_ip_var.get(), port)
        except ValueError:
            pass

    def save_all_settings(self) -> None:
        """Сохранить все текущие настройки в конфиг"""
        settings = {
            'format': self.format_var.get(),
            'show_status_icon': self.show_icon_var.get(),
            'playing_icon': self.playing_icon_var.get(),
            'paused_icon': self.paused_icon_var.get(),
            'show_status_msg': self.show_status_var.get(),
            'status_msg': self.status_msg_var.get(),
            'status_position': self.status_position_var.get(),
            'show_time_msg': self.show_time_var.get(),
            'time_format': self.time_format_var.get(),
            'time_custom': self.time_custom_var.get(),
            'time_position': self.time_position_var.get(),
            'show_sys_msg': self.show_sys_var.get(),
            'sys_msg_separator': self.separator_var.get(),
            'show_cpu_usage': self.show_cpu_var.get(),
            'show_ram_usage': self.show_ram_var.get(),
            'show_cpu_temp': self.show_cpu_temp_var.get(),
            'show_gpu_temp': self.show_gpu_temp_var.get(),
            'media_engine_url': self.media_url_var.get(),
            'vrchat_ip': self.vrchat_ip_var.get(),
            'vrchat_port': int(self.vrchat_port_var.get()),
        }
        
        for key, value in settings.items():
            self.config.set(key, value)



def main():
    root = tk.Tk()
    app = SimpleChatboxApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()




