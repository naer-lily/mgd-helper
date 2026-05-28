from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QSpinBox, QLineEdit, QCheckBox, QComboBox,
    QPushButton, QFormLayout,
)

from config import Config


class SettingsDialog(QDialog):
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self._config = config
        self._result_config: Config | None = None

        self.setWindowTitle('MGD-Helper 设置')
        self.setMinimumSize(600, 520)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QTabWidget::pane {
                border: 1px solid #45475a;
                background-color: #1e1e2e;
            }
            QTabBar::tab {
                background-color: #313244;
                color: #cdd6f4;
                padding: 10px 20px;
                font-size: 16px;
                border: 1px solid #45475a;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #1e1e2e;
                border-bottom: 2px solid #89b4fa;
            }
            QLabel {
                color: #cdd6f4;
                font-size: 16px;
            }
            QSpinBox, QLineEdit, QComboBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 16px;
            }
            QSpinBox:focus, QLineEdit:focus, QComboBox:focus {
                border: 1px solid #89b4fa;
            }
            QCheckBox {
                color: #cdd6f4;
                font-size: 16px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 1px solid #45475a;
                border-radius: 3px;
                background-color: #313244;
            }
            QCheckBox::indicator:checked {
                background-color: #89b4fa;
            }
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #585b70;
            }
            QPushButton#saveBtn {
                background-color: #a6e3a1;
                color: #1e1e2e;
                font-weight: bold;
            }
            QPushButton#saveBtn:hover {
                background-color: #94e2d5;
            }
            QListWidget {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                font-size: 16px;
            }
        """)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        self.setLayout(layout)

        tabs = QTabWidget()
        tabs.addTab(self._timer_tab(), '计时')
        tabs.addTab(self._audio_tab(), '音频')
        tabs.addTab(self._display_tab(), '外观')
        layout.addWidget(tabs)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton('保存')
        save_btn.setObjectName('saveBtn')
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def _timer_tab(self) -> QWidget:
        w = QWidget()
        layout = QFormLayout(w)
        layout.setSpacing(10)

        self._mention_duration = QSpinBox()
        self._mention_duration.setRange(1, 120)
        self._mention_duration.setValue(self._config.mention_duration)
        self._mention_duration.setSuffix(' 分钟')
        layout.addRow('提醒间隔：', self._mention_duration)

        self._short_time = QSpinBox()
        self._short_time.setRange(1, 60)
        self._short_time.setValue(self._config.short_mention_time)
        self._short_time.setSuffix(' 分钟')
        layout.addRow('短休时长：', self._short_time)

        self._long_time = QSpinBox()
        self._long_time.setRange(1, 120)
        self._long_time.setValue(self._config.long_mention_time)
        self._long_time.setSuffix(' 分钟')
        layout.addRow('长休时长：', self._long_time)

        self._long_rounds = QSpinBox()
        self._long_rounds.setRange(1, 20)
        self._long_rounds.setValue(self._config.long_mention_rounds)
        self._long_rounds.setSuffix(' 轮')
        layout.addRow('每 N 轮长休：', self._long_rounds)

        self._delay_time = QSpinBox()
        self._delay_time.setRange(1, 60)
        self._delay_time.setValue(self._config.delay_time)
        self._delay_time.setSuffix(' 分钟')
        layout.addRow('推迟时长：', self._delay_time)

        self._short_msg = QLineEdit(self._config.short_mention_msg)
        layout.addRow('短休提示语：', self._short_msg)

        self._long_msg = QLineEdit(self._config.long_mention_msg)
        layout.addRow('长休提示语：', self._long_msg)

        self._delay_msg = QLineEdit(self._config.delay_msg)
        layout.addRow('推迟按钮文字：', self._delay_msg)

        return w

    def _audio_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)

        self._dingdong_check = QCheckBox('弹窗提示音 (ding-dong)')
        self._dingdong_check.setChecked(self._config.dingdong_enabled)
        layout.addWidget(self._dingdong_check)

        self._bgm_check = QCheckBox('休息背景音乐 (BGM)')
        self._bgm_check.setChecked(self._config.bgm_enabled)
        layout.addWidget(self._bgm_check)

        self._alarm_check = QCheckBox('超时警报')
        self._alarm_check.setChecked(self._config.alarm_enabled)
        layout.addWidget(self._alarm_check)

        layout.addStretch()
        return w

    def _display_tab(self) -> QWidget:
        w = QWidget()
        layout = QFormLayout(w)
        layout.setSpacing(10)

        self._mode_combo = QComboBox()
        self._mode_combo.addItem('弹窗模式', 'popup')
        self._mode_combo.addItem('角落浮窗', 'corner')
        self._mode_combo.addItem('纯托盘通知', 'tray_only')
        idx = self._mode_combo.findData(self._config.mode)
        if idx >= 0:
            self._mode_combo.setCurrentIndex(idx)
        layout.addRow('默认模式：', self._mode_combo)

        self._style_combo = QComboBox()
        self._style_combo.addItem('紧凑', 'compact')
        self._style_combo.addItem('标准', 'standard')
        idx = self._style_combo.findData(self._config.popup_style)
        if idx >= 0:
            self._style_combo.setCurrentIndex(idx)
        layout.addRow('弹窗样式：', self._style_combo)

        self._debug_check = QCheckBox('Debug 模式（显示调试关闭按钮）')
        self._debug_check.setChecked(self._config.debug)
        layout.addRow(self._debug_check)

        return w

    def _on_save(self):
        self._config.mention_duration = self._mention_duration.value()
        self._config.short_mention_time = self._short_time.value()
        self._config.long_mention_time = self._long_time.value()
        self._config.long_mention_rounds = self._long_rounds.value()
        self._config.delay_time = self._delay_time.value()
        self._config.short_mention_msg = self._short_msg.text()
        self._config.long_mention_msg = self._long_msg.text()
        self._config.delay_msg = self._delay_msg.text()
        self._config.dingdong_enabled = self._dingdong_check.isChecked()
        self._config.bgm_enabled = self._bgm_check.isChecked()
        self._config.alarm_enabled = self._alarm_check.isChecked()
        self._config.mode = self._mode_combo.currentData()
        self._config.popup_style = self._style_combo.currentData()
        self._config.debug = self._debug_check.isChecked()

        self._result_config = self._config
        self.accept()

    def get_result(self) -> Config | None:
        return self._result_config
