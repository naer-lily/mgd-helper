from datetime import datetime
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, QObject


class TrayHolder(QObject):
    shortMention = pyqtSignal()
    longMention = pyqtSignal()
    resetTimer = pyqtSignal()
    switchMode = pyqtSignal()
    pausePopup = pyqtSignal(int)
    openSettings = pyqtSignal()

    def __init__(self, icon: QIcon):
        super().__init__()
        self._icon = icon
        self._paused_icon = self._make_gray_icon(icon)

        self._tray_icon = QSystemTrayIcon(self)
        self._tray_icon.setIcon(icon)
        self._tray_icon.setVisible(True)
        self._tray_icon.setToolTip('MGD-Helper')

        self._menu = QMenu()
        self._tray_icon.setContextMenu(self._menu)

        self._next_mention_label = QAction('下一次提醒: --:--:--')
        self._menu.addAction(self._next_mention_label)

        self._current_round_label = QAction('当前轮次：-/-')
        self._menu.addAction(self._current_round_label)

        self._menu.addSeparator()

        self._short_action = QAction('立即短休（轮次+1）')
        self._short_action.triggered.connect(self.shortMention)
        self._menu.addAction(self._short_action)

        self._long_action = QAction('立即长休（轮次重置）')
        self._long_action.triggered.connect(self.longMention)
        self._menu.addAction(self._long_action)

        self._reset_action = QAction('重设定时')
        self._reset_action.triggered.connect(self.resetTimer)
        self._menu.addAction(self._reset_action)

        self._menu.addSeparator()

        self._mode_action = QAction('模式：弹窗模式')
        self._mode_action.triggered.connect(self.switchMode)
        self._menu.addAction(self._mode_action)

        self._pause_menu = self._menu.addMenu('暂停弹窗')
        for mins in (15, 30, 60, 90):
            action = QAction(f'{mins} 分钟')
            action.triggered.connect(lambda checked, m=mins: self.pausePopup.emit(m))
            self._pause_menu.addAction(action)

        self._menu.addSeparator()

        self._settings_action = QAction('设置...')
        self._settings_action.triggered.connect(self.openSettings)
        self._menu.addAction(self._settings_action)

        self._current_round = -1
        self._rounds = -1
        self._next_mention_time_str = '--:--:--'
        self._paused = False

    @property
    def current_round(self):
        return self._current_round

    @current_round.setter
    def current_round(self, x: int):
        self._current_round = x
        self._current_round_label.setText(f'当前轮次：{self._current_round}/{self._rounds}')

    @property
    def rounds(self):
        return self._rounds

    @rounds.setter
    def rounds(self, x: int):
        self._rounds = x
        self._current_round_label.setText(f'当前轮次：{self._current_round}/{self._rounds}')

    @property
    def next_mention_time(self):
        return self._next_mention_time_str

    @next_mention_time.setter
    def next_mention_time(self, x: datetime):
        self._next_mention_time_str = x.strftime('%H:%M:%S')
        self._next_mention_label.setText(f'下一次提醒: {self._next_mention_time_str}')

    def set_mode_label(self, mode: str):
        label = '弹窗模式' if mode == 'popup' else '纯托盘通知'
        self._mode_action.setText(f'模式：{label}')

    def set_paused(self, paused: bool, until: datetime | None = None):
        self._paused = paused
        if paused and until:
            self._tray_icon.setIcon(self._paused_icon)
            self._tray_icon.setToolTip(f'MGD-Helper · 暂停中 · {until.strftime("%H:%M")} 恢复')
        else:
            self._tray_icon.setIcon(self._icon)
            self._tray_icon.setToolTip('MGD-Helper')

    def show_notification(self, title: str, message: str, duration_ms: int = 5000):
        self._tray_icon.showMessage(title, message, QSystemTrayIcon.Information, duration_ms)

    @staticmethod
    def _make_gray_icon(icon: QIcon) -> QIcon:
        from PyQt5.QtGui import QPixmap, QPainter, QColor
        pixmap = icon.pixmap(64, 64)
        gray = QPixmap(pixmap.size())
        gray.fill(QColor(0, 0, 0, 0))
        painter = QPainter(gray)
        painter.setOpacity(0.35)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        return QIcon(gray)
