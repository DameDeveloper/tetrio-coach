"""리소스 경로 유틸리티. PyInstaller 번들과 개발 환경 모두 지원."""

import sys
from pathlib import Path


def get_base_dir() -> Path:
    """번들 리소스(DLL, models, locales, assets) 기본 경로."""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


def get_app_dir() -> Path:
    """쓰기 가능한 앱 설치 디렉토리 (설정 파일 등)."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent
