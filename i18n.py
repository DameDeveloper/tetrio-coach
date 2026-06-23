"""다국어 지원 (i18n). JSON 기반 로케일 파일에서 번역을 로드한다."""

import json
from pathlib import Path
from _paths import get_base_dir, get_app_dir

SUPPORTED_LANGS = ('ko', 'en', 'zh', 'ja')
_current_lang: str = 'en'
_strings: dict[str, dict[str, str]] = {}
_loaded = False

CONFIG_FILE = Path.home() / '.tetrio_coach_lang'

LANG_NAMES = {
    'ko': '한국어',
    'en': 'English',
    'zh': '中文',
    'ja': '日本語',
}


def load_translations() -> None:
    """locales/ 디렉토리에서 모든 언어 파일을 로드."""
    global _strings, _loaded
    locale_dir = get_base_dir() / 'locales'
    for lang in SUPPORTED_LANGS:
        path = locale_dir / f'{lang}.json'
        if path.exists():
            try:
                _strings[lang] = json.loads(path.read_text(encoding='utf-8'))
            except Exception:
                _strings[lang] = {}
        else:
            _strings[lang] = {}
    _loaded = True


def set_language(lang: str) -> None:
    global _current_lang
    if lang in SUPPORTED_LANGS:
        _current_lang = lang
        try:
            CONFIG_FILE.write_text(lang, encoding='utf-8')
        except Exception:
            pass


def get_language() -> str:
    return _current_lang


def detect_language() -> str:
    """저장된 설정 또는 설치 시 선택된 언어를 감지."""
    if CONFIG_FILE.exists():
        try:
            lang = CONFIG_FILE.read_text(encoding='utf-8').strip()
            if lang in SUPPORTED_LANGS:
                return lang
        except Exception:
            pass

    install_lang_file = get_app_dir() / 'install_lang.txt'
    if install_lang_file.exists():
        try:
            nsis_lang_id = install_lang_file.read_text(encoding='utf-8').strip()
            nsis_map = {'1042': 'ko', '1033': 'en', '2052': 'zh', '1041': 'ja'}
            lang = nsis_map.get(nsis_lang_id, '')
            if lang:
                return lang
        except Exception:
            pass

    return 'en'


def init() -> None:
    """i18n 시스템 초기화."""
    if not _loaded:
        load_translations()
    set_language(detect_language())


def t(key: str, **kwargs) -> str:
    """번역 키를 현재 언어로 변환. kwargs로 변수 보간."""
    if not _loaded:
        init()

    text = _strings.get(_current_lang, {}).get(key)
    if text is None:
        text = _strings.get('ko', {}).get(key)
    if text is None:
        return key

    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text
