from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
)

from media_player import MyMediaPlayer


class DialogParam(BaseModel):
    title: str = ''
    duration: int
    msg: str
    delay_msg: str = ''
    can_delay: bool = True
    debug: bool = False
    popup_style: str = 'compact'


class DialogResult(BaseModel):
    action: str = 'NORMAL'
    note: str = ''
    open_time: datetime = Field(default_factory=datetime.now)
    close_time: datetime = Field(default_factory=datetime.now)


class MentionDialog(QDialog):
    def __init__(self, config: DialogParam, media_player: MyMediaPlayer):
        super().__init__()
        self._config = config
        self._media_player = media_player
        self._open_time = datetime.now()
        self._timeout_reached = False

        is_compact = config.popup_style == 'compact'
        if is_compact:
            self.setMinimumSize(580, 460)
            base_font_size = 22
        else:
            self.setMinimumSize(800, 600)
            base_font_size = 36

        self.setStyleSheet(f"""
            MentionDialog {{
                background-color: #1e1e2e;
                color: #cdd6f4;
            }}
            QLabel {{
                color: #cdd6f4;
                font-size: {base_font_size}px;
            }}
            QLabel#msgLabel {{
                font-size: {base_font_size + 3}px;
                font-weight: bold;
            }}
            QLabel#timerLabel {{
                font-size: {base_font_size}px;
                font-family: 'Consolas', 'Microsoft YaHei UI';
            }}
            QTextEdit {{
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 10px;
                font-size: {base_font_size - 1}px;
            }}
            QPushButton {{
                background-color: #45475a;
                color: #cdd6f4;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: {base_font_size - 1}px;
            }}
            QPushButton:hover {{
                background-color: #585b70;
            }}
            QPushButton:disabled {{
                background-color: #313244;
                color: #585b70;
            }}
            QPushButton#closeBtn {{
                background-color: #a6e3a1;
                color: #1e1e2e;
                font-weight: bold;
                font-size: {base_font_size + 1}px;
            }}
            QPushButton#closeBtn:hover {{
                background-color: #94e2d5;
            }}
            QPushButton#closeBtn:disabled {{
                background-color: #313244;
                color: #585b70;
            }}
        """)

        self.setWindowTitle(config.title or '护眼提醒')
        self.setWindowFlags(
            Qt.Window
            | Qt.WindowStaysOnTopHint
            | Qt.CustomizeWindowHint
        )
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

        self._build_ui(base_font_size)

        self._timer = QTimer(self)
        self._timer.setInterval(200)
        self._timer.timeout.connect(self._on_tick)
        self._timer.start()

    def _build_ui(self, font_size: int):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)
        self.setLayout(layout)

        msg_label = QLabel(self._config.msg, self)
        msg_label.setObjectName('msgLabel')
        msg_label.setWordWrap(True)
        layout.addWidget(msg_label)

        self._timer_label = QLabel(self)
        self._timer_label.setObjectName('timerLabel')
        layout.addWidget(self._timer_label)

        self._note_edit = QTextEdit(self)
        self._note_edit.setPlaceholderText('随便写点感想...（可选）')
        self._note_edit.setMaximumHeight(100 if self._config.popup_style == 'compact' else 160)
        layout.addWidget(self._note_edit)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        if self._config.can_delay:
            self._delay_btn = QPushButton(self._config.delay_msg or '推迟', self)
            self._delay_btn.clicked.connect(self._on_delay)
            btn_layout.addWidget(self._delay_btn)

        btn_layout.addStretch()

        self._close_btn = QPushButton('关闭（请等待...）', self)
        self._close_btn.setObjectName('closeBtn')
        self._close_btn.setEnabled(False)
        self._close_btn.clicked.connect(self._on_close)
        btn_layout.addWidget(self._close_btn)

        if self._config.debug:
            debug_btn = QPushButton('DEBUG CLOSE', self)
            debug_btn.clicked.connect(self._on_debug_close)
            btn_layout.addWidget(debug_btn)

        layout.addLayout(btn_layout)

    def _on_tick(self):
        expect_close = self._open_time + timedelta(seconds=self._config.duration)
        remain = expect_close - datetime.now()
        seconds = remain.total_seconds()

        if seconds > 0:
            m = int(seconds // 60)
            s = int(seconds % 60)
            self._timer_label.setText(f'关闭时间剩余：{m}:{s:02d}（至 {expect_close:%H:%M}）')
            return

        self._timer_label.setText('时间到！可以关闭了')
        self._timer.stop()

        if not self._timeout_reached:
            self._timeout_reached = True
            self._media_player.play_alarm()

        self._close_btn.setText('关闭')
        self._close_btn.setEnabled(True)

    def _on_delay(self):
        self._media_player.stop_clock()
        self.done(2)

    def _on_close(self):
        self._media_player.stop_clock()
        self.done(0)

    def _on_debug_close(self):
        self._media_player.stop_clock()
        self.done(1)

    def start_mentioning(self) -> DialogResult:
        self._open_time = datetime.now()
        self._media_player.play_dingdong()
        self._media_player.start_clock()

        code = self.exec()
        self._timer.stop()
        self._media_player.stop_clock()

        result = DialogResult(
            open_time=self._open_time,
            close_time=datetime.now(),
            note=self._note_edit.toPlainText().strip(),
        )

        if code == 1:
            result.action = 'DEBUG_CLOSE'
        elif code == 2:
            result.action = 'DELAY'
        else:
            result.action = 'NORMAL'

        return result

    def closeEvent(self, event):
        event.ignore()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            event.ignore()
        else:
            super().keyPressEvent(event)
