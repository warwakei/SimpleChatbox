import sys
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QSpinBox, QCheckBox,
                             QComboBox, QLineEdit, QTabWidget, QGroupBox, QScrollArea)
from PyQt5.QtCore import QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont

from media_engine_client import MediaEngineClient
from vrchat_chatbox import VRChatChatbox
from system_info import SystemInfo
from config import Config


class UpdateSignals(QObject):
    track_updated = pyqtSignal(dict)
    status_changed = pyqtSignal(str)


class SimpleChatboxApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.media_client = MediaEngineClient()
        self.vrchat = VRChatChatbox(
            ip=self.config.get('vrchat_ip'),
            port=self.config.get('vrchat_port')
        )
        self.system_info = SystemInfo()
        self.signals = UpdateSignals()
        self.current_track = None
        self.auto_send_enabled = False
        
        self.init_ui()
        self.setup_timer()
        
        self.signals.track_updated.connect(self.on_track_updated)
        self.signals.status_changed.connect(self.on_status_changed)
    
    def init_ui(self):
        self.setWindowTitle("SimpleChatbox - VRChat Music Display")
        self.setGeometry(100, 100, 600, 550)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # Статус подключения
        self.status_label = QLabel("Connecting to MediaEngine...")
        self.status_label.setFont(QFont("Arial", 10))
        main_layout.addWidget(self.status_label)
        
        # Автоотправка
        auto_layout = QHBoxLayout()
        self.auto_send_checkbox = QCheckBox("Auto-send every (ms):")
        self.auto_send_checkbox.setChecked(False)
        self.auto_send_checkbox.stateChanged.connect(self.toggle_auto_send)
        auto_layout.addWidget(self.auto_send_checkbox)
        
        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setMinimum(100)
        self.delay_spinbox.setMaximum(60000)
        self.delay_spinbox.setValue(self.config.get('auto_send_delay', 3000))
        self.delay_spinbox.setSingleStep(100)
        auto_layout.addWidget(self.delay_spinbox)
        auto_layout.addStretch()
        main_layout.addLayout(auto_layout)
        
        # Preview панель
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        
        self.track_label = QLabel("No track playing")
        self.track_label.setFont(QFont("Arial", 11, QFont.Bold))
        preview_layout.addWidget(self.track_label)
        
        self.sys_label = QLabel("")
        self.sys_label.setFont(QFont("Arial", 10))
        preview_layout.addWidget(self.sys_label)
        
        preview_group.setLayout(preview_layout)
        main_layout.addWidget(preview_group)
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        
        self.send_button = QPushButton("Send to VRChat")
        self.send_button.clicked.connect(self.send_to_vrchat)
        button_layout.addWidget(self.send_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_track)
        button_layout.addWidget(self.refresh_button)
        
        main_layout.addLayout(button_layout)
        
        # Табы для настроек
        tabs = QTabWidget()
        
        # Таб 1: Music Message
        music_widget = self.create_music_tab()
        tabs.addTab(music_widget, "MusicMSG")
        
        # Таб 2: System Message
        sys_widget = self.create_sys_tab()
        tabs.addTab(sys_widget, "SysMSG")
        
        # Таб 3: Advanced
        advanced_widget = self.create_advanced_tab()
        tabs.addTab(advanced_widget, "Advanced")
        
        main_layout.addWidget(tabs)
        central_widget.setLayout(main_layout)
    
    def create_music_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addSpacing(20)
        
        # Формат сообщения
        format_group = QGroupBox("Message Format")
        format_layout = QVBoxLayout()
        
        format_label = QLabel("Select format:")
        format_layout.addWidget(format_label)
        
        self.format_combo = QComboBox()
        self.format_combo.addItem("Display (from API)", "display")
        self.format_combo.addItem("Artist - Track", "artist_track")
        self.format_combo.addItem("Track - Artist", "track_artist")
        self.format_combo.addItem("Track by Artist", "track_by_artist")
        self.format_combo.addItem("Track only", "track_only")
        
        current_format = self.config.get('format', 'display')
        index = self.format_combo.findData(current_format)
        if index >= 0:
            self.format_combo.setCurrentIndex(index)
        
        self.format_combo.currentIndexChanged.connect(self.on_format_changed)
        format_layout.addWidget(self.format_combo)
        
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        layout.addSpacing(20)
        
        # Иконки статуса
        icons_group = QGroupBox("Status Icons")
        icons_layout = QVBoxLayout()
        
        self.show_icon_checkbox = QCheckBox("Show status icon")
        self.show_icon_checkbox.setChecked(self.config.get('show_status_icon', True))
        self.show_icon_checkbox.stateChanged.connect(self.on_show_icon_changed)
        icons_layout.addWidget(self.show_icon_checkbox)
        
        playing_layout = QHBoxLayout()
        playing_layout.addWidget(QLabel("Playing icon:"))
        self.playing_icon_input = QLineEdit()
        self.playing_icon_input.setText(self.config.get('playing_icon', '▶'))
        self.playing_icon_input.setMaxLength(5)
        self.playing_icon_input.setMaximumWidth(100)
        self.playing_icon_input.textChanged.connect(self.on_playing_icon_changed)
        playing_layout.addWidget(self.playing_icon_input)
        playing_layout.addStretch()
        icons_layout.addLayout(playing_layout)
        
        paused_layout = QHBoxLayout()
        paused_layout.addWidget(QLabel("Paused icon:"))
        self.paused_icon_input = QLineEdit()
        self.paused_icon_input.setText(self.config.get('paused_icon', '⏸'))
        self.paused_icon_input.setMaxLength(5)
        self.paused_icon_input.setMaximumWidth(100)
        self.paused_icon_input.textChanged.connect(self.on_paused_icon_changed)
        paused_layout.addWidget(self.paused_icon_input)
        paused_layout.addStretch()
        icons_layout.addLayout(paused_layout)
        
        icons_group.setLayout(icons_layout)
        layout.addWidget(icons_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_sys_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Включить/выключить SysMSG
        self.show_sys_checkbox = QCheckBox("Show system info in message")
        self.show_sys_checkbox.setChecked(self.config.get('show_sys_msg', False))
        self.show_sys_checkbox.stateChanged.connect(self.on_show_sys_changed)
        layout.addWidget(self.show_sys_checkbox)
        
        layout.addSpacing(20)
        
        # Сепаратор
        sep_layout = QHBoxLayout()
        sep_layout.addWidget(QLabel("Message separator:"))
        self.separator_input = QLineEdit()
        self.separator_input.setText(self.config.get('sys_msg_separator', ' | '))
        self.separator_input.setMaxLength(10)
        self.separator_input.setMaximumWidth(150)
        self.separator_input.textChanged.connect(self.on_separator_changed)
        sep_layout.addWidget(self.separator_input)
        sep_layout.addStretch()
        layout.addLayout(sep_layout)
        
        layout.addSpacing(20)
        
        # Что показывать
        display_group = QGroupBox("What to Display")
        display_layout = QVBoxLayout()
        
        self.show_cpu_usage_checkbox = QCheckBox("CPU Usage")
        self.show_cpu_usage_checkbox.setChecked(self.config.get('show_cpu_usage', True))
        self.show_cpu_usage_checkbox.stateChanged.connect(self.on_cpu_usage_changed)
        display_layout.addWidget(self.show_cpu_usage_checkbox)
        
        self.show_ram_usage_checkbox = QCheckBox("RAM Usage")
        self.show_ram_usage_checkbox.setChecked(self.config.get('show_ram_usage', True))
        self.show_ram_usage_checkbox.stateChanged.connect(self.on_ram_usage_changed)
        display_layout.addWidget(self.show_ram_usage_checkbox)
        
        self.show_cpu_temp_checkbox = QCheckBox("CPU Temperature")
        self.show_cpu_temp_checkbox.setChecked(self.config.get('show_cpu_temp', True))
        self.show_cpu_temp_checkbox.stateChanged.connect(self.on_cpu_temp_changed)
        display_layout.addWidget(self.show_cpu_temp_checkbox)
        
        self.show_gpu_temp_checkbox = QCheckBox("GPU Temperature")
        self.show_gpu_temp_checkbox.setChecked(self.config.get('show_gpu_temp', True))
        self.show_gpu_temp_checkbox.stateChanged.connect(self.on_gpu_temp_changed)
        display_layout.addWidget(self.show_gpu_temp_checkbox)
        
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_advanced_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # MediaEngine URL
        media_layout = QHBoxLayout()
        media_layout.addWidget(QLabel("MediaEngine URL:"))
        self.media_url_input = QLineEdit()
        self.media_url_input.setText(self.config.get('media_engine_url', 'http://localhost:5000'))
        self.media_url_input.textChanged.connect(self.on_media_url_changed)
        media_layout.addWidget(self.media_url_input)
        layout.addLayout(media_layout)
        
        # VRChat IP
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(QLabel("VRChat IP:"))
        self.vrchat_ip_input = QLineEdit()
        self.vrchat_ip_input.setText(self.config.get('vrchat_ip', '127.0.0.1'))
        self.vrchat_ip_input.textChanged.connect(self.on_vrchat_ip_changed)
        ip_layout.addWidget(self.vrchat_ip_input)
        layout.addLayout(ip_layout)
        
        # VRChat Port
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("VRChat Port:"))
        self.vrchat_port_input = QSpinBox()
        self.vrchat_port_input.setMinimum(1)
        self.vrchat_port_input.setMaximum(65535)
        self.vrchat_port_input.setValue(self.config.get('vrchat_port', 9000))
        self.vrchat_port_input.valueChanged.connect(self.on_vrchat_port_changed)
        port_layout.addWidget(self.vrchat_port_input)
        port_layout.addStretch()
        layout.addLayout(port_layout)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_connection)
        self.timer.start(1000)
        
        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(self.auto_send_track)
    
    def check_connection(self):
        """Проверить подключение к MediaEngine"""
        status = self.media_client.get_status()
        if status:
            self.signals.status_changed.emit("✓ Connected to MediaEngine")
            self.refresh_track()
        else:
            self.signals.status_changed.emit("✗ Cannot connect to MediaEngine")
    
    def refresh_track(self):
        """Обновить информацию о треке"""
        track = self.media_client.get_current_track()
        if track:
            self.signals.track_updated.emit(track)
            # Обновляем системную информацию при обновлении трека
            if self.show_sys_checkbox.isChecked():
                sys_msg = self.system_info.format_sys_message(self.config)
                self.sys_label.setText(sys_msg)
    
    def on_track_updated(self, track):
        self.current_track = track
        message = self.vrchat.format_track_message(track, self.config)
        is_paused = track.get('isPaused', False)
        status = "PAUSED" if is_paused else "PLAYING"
        self.track_label.setText(f"{status}\n{message}")
    
    def on_status_changed(self, status):
        self.status_label.setText(status)
    
    def send_to_vrchat(self):
        """Отправить текущий трек в VRChat"""
        if self.current_track:
            message = self.vrchat.format_track_message(self.current_track, self.config)
            
            # Добавить системную информацию если включено
            if self.show_sys_checkbox.isChecked():
                sys_msg = self.system_info.format_sys_message(self.config)
                separator = self.config.get('sys_msg_separator', ' | ')
                message = f"{message}{separator}{sys_msg}"
            
            if self.vrchat.send_message(message):
                self.status_label.setText("✓ Sent to VRChat")
            else:
                self.status_label.setText("✗ Failed to send to VRChat")
    
    def toggle_auto_send(self, state):
        """Включить/выключить автоотправку"""
        if state:
            delay = self.delay_spinbox.value()
            self.auto_timer.start(delay)
            self.auto_send_enabled = True
        else:
            self.auto_timer.stop()
            self.auto_send_enabled = False
    
    def auto_send_track(self):
        """Автоматически отправить трек"""
        self.refresh_track()
        if self.current_track:
            self.send_to_vrchat()
    
    def on_format_changed(self):
        """Изменение формата сообщения"""
        format_type = self.format_combo.currentData()
        self.config.set('format', format_type)
        self.refresh_track()
    
    def on_show_icon_changed(self):
        """Изменение показа иконки"""
        show = self.show_icon_checkbox.isChecked()
        self.config.set('show_status_icon', show)
        self.refresh_track()
    
    def on_playing_icon_changed(self):
        """Изменение иконки воспроизведения"""
        icon = self.playing_icon_input.text()
        self.config.set('playing_icon', icon)
        self.refresh_track()
    
    def on_paused_icon_changed(self):
        """Изменение иконки паузы"""
        icon = self.paused_icon_input.text()
        self.config.set('paused_icon', icon)
        self.refresh_track()
    
    def on_show_sys_changed(self):
        """Изменение показа системной информации"""
        show = self.show_sys_checkbox.isChecked()
        self.config.set('show_sys_msg', show)
        self.refresh_track()
    
    def on_separator_changed(self):
        """Изменение сепаратора"""
        sep = self.separator_input.text()
        self.config.set('sys_msg_separator', sep)
    
    def on_cpu_usage_changed(self):
        """Изменение показа CPU Usage"""
        show = self.show_cpu_usage_checkbox.isChecked()
        self.config.set('show_cpu_usage', show)
        self.refresh_track()
    
    def on_ram_usage_changed(self):
        """Изменение показа RAM Usage"""
        show = self.show_ram_usage_checkbox.isChecked()
        self.config.set('show_ram_usage', show)
        self.refresh_track()
    
    def on_cpu_temp_changed(self):
        """Изменение показа CPU Temperature"""
        show = self.show_cpu_temp_checkbox.isChecked()
        self.config.set('show_cpu_temp', show)
        self.refresh_track()
    
    def on_gpu_temp_changed(self):
        """Изменение показа GPU Temperature"""
        show = self.show_gpu_temp_checkbox.isChecked()
        self.config.set('show_gpu_temp', show)
        self.refresh_track()
    
    def on_media_url_changed(self):
        """Изменение URL MediaEngine"""
        url = self.media_url_input.text()
        self.config.set('media_engine_url', url)
        self.media_client = MediaEngineClient(url)
    
    def on_vrchat_ip_changed(self):
        """Изменение IP VRChat"""
        ip = self.vrchat_ip_input.text()
        self.config.set('vrchat_ip', ip)
        self.vrchat = VRChatChatbox(ip=ip, port=self.config.get('vrchat_port'))
    
    def on_vrchat_port_changed(self):
        """Изменение порта VRChat"""
        port = self.vrchat_port_input.value()
        self.config.set('vrchat_port', port)
        self.vrchat = VRChatChatbox(ip=self.config.get('vrchat_ip'), port=port)


def main():
    app = QApplication(sys.argv)
    window = SimpleChatboxApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
