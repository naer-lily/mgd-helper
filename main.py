from datetime import datetime, timedelta
from pathlib import Path

from pydantic import BaseModel
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from config import Config, get_config, save_config, LOG_PATH
from media_player import MyMediaPlayer
from mention_dialog import DialogParam, DialogResult, MentionDialog
from tray_holder import TrayHolder
from settings_dialog import SettingsDialog


class AppState(BaseModel):
    is_running: bool = False
    is_showing_dialog: bool = False
    next_mention_time: datetime | None = None
    can_delay: bool = True
    current_round: int = 1
    paused_until: datetime | None = None


class Main:
    def __init__(self, config: Config, tray: TrayHolder, media_player: MyMediaPlayer) -> None:
        self._config = config
        self._state = AppState()
        self._tray = tray
        self._media_player = media_player

        self._apply_audio_config()
        self._tray.set_mode_label(self._config.mode)

        self._timer = QTimer()
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._loop)

        self._init_tray_signals()

    def _apply_audio_config(self):
        self._media_player.dingdong_enabled = self._config.dingdong_enabled
        self._media_player.bgm_enabled = self._config.bgm_enabled
        self._media_player.alarm_enabled = self._config.alarm_enabled
        self._media_player.stop_clock()

    def _init_tray_signals(self):
        t = self._tray

        @t.shortMention.connect
        def _():
            self._state.can_delay = False
            self._do_mention(False)

        @t.longMention.connect
        def _():
            self._state.can_delay = False
            self._do_mention(True)

        @t.resetTimer.connect
        def _():
            self._state.next_mention_time = self._next_mention_time()

        @t.switchMode.connect
        def _():
            self._config.mode = 'tray_only' if self._config.mode == 'popup' else 'popup'
            save_config(self._config)
            self._tray.set_mode_label(self._config.mode)

        @t.pausePopup.connect
        def _(minutes: int):
            self._state.paused_until = datetime.now() + timedelta(minutes=minutes)
            self._tray.set_paused(True, self._state.paused_until)

        @t.openSettings.connect
        def _():
            self._open_settings()

    def _open_settings(self):
        dlg = SettingsDialog(self._config)
        if dlg.exec():
            result = dlg.get_result()
            if result:
                self._config = result
                save_config(self._config)
                self._apply_audio_config()
                self._tray.set_mode_label(self._config.mode)

    def _loop(self):
        if not self._state.is_running:
            return

        now = datetime.now()

        if self._state.paused_until:
            if now < self._state.paused_until:
                self._tray.set_paused(True, self._state.paused_until)
                return
            self._state.paused_until = None
            self._tray.set_paused(False)

        self._update_tray()

        if self._state.next_mention_time and now < self._state.next_mention_time:
            return

        self._do_mention(self._state.current_round >= self._config.long_mention_rounds)

    def _do_mention(self, long_mention: bool):
        if self._config.mode == 'tray_only':
            self._do_tray_notification(long_mention)
            return

        if self._state.is_showing_dialog:
            return

        is_long = long_mention
        duration = 60 * (self._config.long_mention_time if is_long else self._config.short_mention_time)
        msg = self._config.long_mention_msg if is_long else self._config.short_mention_msg

        dialog = MentionDialog(DialogParam(
            title='',
            duration=duration,
            msg=msg,
            can_delay=self._state.can_delay,
            delay_msg=self._config.delay_msg,
            debug=self._config.debug,
            popup_style=self._config.popup_style,
        ), self._media_player)

        self._state.is_showing_dialog = True
        response = dialog.start_mentioning()
        self._state.is_showing_dialog = False

        self._advance_state(response, long_mention)
        self._append_log(response)

    def _do_tray_notification(self, long_mention: bool):
        msg = self._config.long_mention_msg if long_mention else self._config.short_mention_msg
        duration_ms = 10000
        self._tray.show_notification('护眼提醒', msg, duration_ms)

        response = DialogResult(
            action='NORMAL',
            note='',
            open_time=datetime.now(),
            close_time=datetime.now(),
        )
        self._advance_state(response, long_mention)
        self._append_log(response)

    def _advance_state(self, response: DialogResult, long_mention: bool):
        if response.action == 'DELAY':
            self._state.next_mention_time = datetime.now() + timedelta(minutes=self._config.delay_time)
            self._state.can_delay = False
            return

        self._state.can_delay = True
        self._state.next_mention_time = self._next_mention_time()
        self._state.current_round += 1
        if long_mention:
            self._state.current_round = 1

    def _next_mention_time(self) -> datetime:
        return datetime.now() + timedelta(minutes=self._config.mention_duration)

    def _update_tray(self):
        self._tray.current_round = self._state.current_round
        self._tray.rounds = self._config.long_mention_rounds
        if self._state.next_mention_time:
            self._tray.next_mention_time = self._state.next_mention_time

    def _append_log(self, response: DialogResult):
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open('at', encoding='utf-8') as f:
            f.write(response.model_dump_json())
            f.write('\n')

    def start(self):
        self._state.is_running = True
        self._state.next_mention_time = self._next_mention_time()
        self._timer.start()


if __name__ == '__main__':
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)

    config = get_config()

    icon_path = Path(__file__).parent / 'asset' / 'icon.ico'
    tray = TrayHolder(QIcon(str(icon_path)))
    player = MyMediaPlayer()

    main = Main(config, tray, player)
    main.start()
    app.exec()
