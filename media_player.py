from pathlib import Path
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, QObject

ASSET_DIR = Path(__file__).parent / 'asset'


class MyMediaPlayer(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.alarm_player = QMediaPlayer()
        self.dingdong_player = QMediaPlayer()

        self.clock_player = QMediaPlayer()
        self.clock_player.setMedia(QMediaContent(QUrl.fromLocalFile(str(ASSET_DIR / 'clock.mp3'))))
        self._should_loop = False

        def handle_media_status(status):
            if status == QMediaPlayer.EndOfMedia and self._should_loop:
                self.clock_player.setPosition(0)
                self.clock_player.play()

        self.clock_player.mediaStatusChanged.connect(handle_media_status)

        self.dingdong_enabled = True
        self.bgm_enabled = False
        self.alarm_enabled = True

    def play_alarm(self):
        if not self.alarm_enabled:
            return
        self.alarm_player.setMedia(QMediaContent(QUrl.fromLocalFile(str(ASSET_DIR / 'alarm.wav'))))
        self.alarm_player.play()

    def play_dingdong(self):
        if not self.dingdong_enabled:
            return
        self.dingdong_player.setMedia(QMediaContent(QUrl.fromLocalFile(str(ASSET_DIR / 'ding-dong.wav'))))
        self.dingdong_player.play()

    def start_clock(self):
        if not self.bgm_enabled:
            return
        self._should_loop = True
        self.clock_player.play()

    def stop_clock(self):
        self._should_loop = False
        self.clock_player.stop()
