from pathlib import Path
from pydantic import BaseModel

CONFIG_DIR = Path.home() / '.config'
CONFIG_PATH = CONFIG_DIR / 'mgd-helper.json'
LOG_PATH = CONFIG_DIR / 'mgd-helper-log.jsonl'
LEGACY_CONFIG = Path('config.json')


class Config(BaseModel):
    mention_duration: int = 20
    long_mention_rounds: int = 3
    delay_time: int = 5
    short_mention_time: int = 4
    short_mention_msg: str = '该短休了！眺望并用力闭眼1分钟，冥想 3 分钟！'
    long_mention_time: int = 13
    long_mention_msg: str = '该长休了，眺望并用力闭眼 3 分钟，冥想 10 分钟！'
    delay_msg: str = '推迟 5 分钟显示'
    mode: str = 'popup'
    popup_style: str = 'compact'
    dingdong_enabled: bool = True
    bgm_enabled: bool = False
    alarm_enabled: bool = True
    debug: bool = False


def _migrate_legacy() -> Config | None:
    if not LEGACY_CONFIG.exists():
        return None
    try:
        raw = LEGACY_CONFIG.read_bytes()
        cfg = Config.model_validate_json(raw)
        _save(cfg)
        LEGACY_CONFIG.rename(LEGACY_CONFIG.with_suffix('.json.bak'))
        return cfg
    except Exception:
        return None


def _save(cfg: Config) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(cfg.model_dump_json(indent=4), encoding='utf-8')


def get_config() -> Config:
    if CONFIG_PATH.exists():
        try:
            return Config.model_validate_json(CONFIG_PATH.read_bytes())
        except Exception:
            pass

    migrated = _migrate_legacy()
    if migrated is not None:
        return migrated

    default = Config()
    _save(default)
    return default


def save_config(cfg: Config) -> None:
    _save(cfg)
