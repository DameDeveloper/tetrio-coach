"""
TetrioCoach 통합 빌드 스크립트.
Usage: python build.py [--skip-nsis] [--version X.Y.Z]
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

APP_NAME = "TetrioCoach"
DEFAULT_VERSION = "1.0.0"


def check_prerequisites():
    """필수 도구 확인."""
    errors = []

    try:
        subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'],
                      capture_output=True, check=True, timeout=10)
    except (subprocess.CalledProcessError, FileNotFoundError):
        errors.append("PyInstaller가 설치되어 있지 않습니다. `pip install pyinstaller`")

    if not errors:
        print("[OK] PyInstaller")

    try:
        subprocess.run(['makensis', '/VERSION'], capture_output=True, check=True, timeout=10)
        print("[OK] NSIS")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[WARN] NSIS를 찾을 수 없습니다. 인스톨러 빌드를 건너뜁니다.")
        print("       NSIS 설치: https://nsis.sourceforge.io/Download")

    for pkg in ['matplotlib', 'numpy', 'sklearn']:
        try:
            __import__(pkg)
            print(f"[OK] {pkg}")
        except ImportError:
            errors.append(f"{pkg}가 설치되어 있지 않습니다. `pip install {pkg}`")

    if errors:
        print("\n[ERROR] 빌드 전 문제를 해결하세요:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)


def clean():
    """이전 빌드 결과물 삭제."""
    for d in ['build', 'dist']:
        if Path(d).exists():
            shutil.rmtree(d)
            print(f"[CLEAN] {d}/ 삭제됨")


def generate_icon():
    """간단한 앱 아이콘 생성 (assets/tetrio_coach.ico가 없을 경우)."""
    ico_path = Path('assets/tetrio_coach.ico')
    if ico_path.exists():
        print(f"[OK] 아이콘: {ico_path}")
        return

    os.makedirs('assets', exist_ok=True)

    try:
        from PIL import Image, ImageDraw, ImageFont

        sizes = [256, 48, 32, 16]
        images = []
        for size in sizes:
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            pad = size // 8
            draw.rounded_rectangle(
                [pad, pad, size - pad, size - pad],
                radius=size // 6,
                fill=(124, 92, 252),
            )

            try:
                font = ImageFont.truetype("arial.ttf", size // 3)
            except Exception:
                font = ImageFont.load_default()

            text = "TC"
            bbox = draw.textbbox((0, 0), text, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(((size - tw) / 2, (size - th) / 2 - size // 10), text, fill='white', font=font)

            images.append(img)

        images[0].save(str(ico_path), format='ICO', sizes=[(s, s) for s in sizes])
        print(f"[OK] 아이콘 생성됨: {ico_path}")

    except ImportError:
        print("[WARN] Pillow가 없어 아이콘을 생성할 수 없습니다. 기본 아이콘 없이 빌드합니다.")
        print("       `pip install Pillow`로 설치 후 다시 시도하세요.")


def build_exe(version: str):
    """PyInstaller로 exe 빌드."""
    print(f"\n[BUILD] PyInstaller 빌드 시작 (v{version})...")

    spec_file = 'tetrio_coach.spec'
    if not Path(spec_file).exists():
        print(f"[ERROR] {spec_file}를 찾을 수 없습니다.")
        sys.exit(1)

    cmd = [
        sys.executable, '-m', 'PyInstaller',
        spec_file,
        '--noconfirm',
        '--clean',
    ]

    result = subprocess.run(cmd, timeout=600)
    if result.returncode != 0:
        print("[ERROR] PyInstaller 빌드 실패")
        sys.exit(1)

    exe_path = Path(f'dist/{APP_NAME}/{APP_NAME}.exe')
    if not exe_path.exists():
        print(f"[ERROR] 빌드된 exe를 찾을 수 없습니다: {exe_path}")
        sys.exit(1)

    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"[OK] EXE 빌드 완료: {exe_path} ({size_mb:.1f} MB)")

    dist_dir = Path(f'dist/{APP_NAME}')
    total_size = sum(f.stat().st_size for f in dist_dir.rglob('*') if f.is_file())
    print(f"[OK] 전체 배포 크기: {total_size / (1024*1024):.1f} MB")


def build_installer(version: str):
    """NSIS 인스톨러 빌드."""
    print(f"\n[BUILD] NSIS 인스톨러 빌드 시작...")

    nsi_file = 'installer.nsi'
    if not Path(nsi_file).exists():
        print(f"[ERROR] {nsi_file}를 찾을 수 없습니다.")
        return False

    try:
        subprocess.run(['makensis', '/VERSION'], capture_output=True, check=True, timeout=10)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[SKIP] NSIS가 설치되어 있지 않습니다. 인스톨러 빌드를 건너뜁니다.")
        return False

    cmd = ['makensis', f'/DAPPVERSION={version}', nsi_file]
    result = subprocess.run(cmd, timeout=300)

    if result.returncode != 0:
        print("[ERROR] NSIS 빌드 실패")
        return False

    installer_path = Path(f'dist/{APP_NAME}_Setup_{version}.exe')
    if installer_path.exists():
        size_mb = installer_path.stat().st_size / (1024 * 1024)
        print(f"[OK] 인스톨러 생성: {installer_path} ({size_mb:.1f} MB)")
        return True

    print("[WARN] 인스톨러 파일을 찾을 수 없습니다.")
    return False


def main():
    parser = argparse.ArgumentParser(description=f'{APP_NAME} 빌드 스크립트')
    parser.add_argument('--version', default=DEFAULT_VERSION, help='버전 번호 (기본: 1.0.0)')
    parser.add_argument('--skip-nsis', action='store_true', help='NSIS 인스톨러 빌드 건너뛰기')
    parser.add_argument('--skip-clean', action='store_true', help='이전 빌드 결과물 유지')
    args = parser.parse_args()

    print(f"{'='*50}")
    print(f"  {APP_NAME} Build Script v{args.version}")
    print(f"{'='*50}\n")

    check_prerequisites()

    if not args.skip_clean:
        clean()

    generate_icon()
    build_exe(args.version)

    if not args.skip_nsis:
        build_installer(args.version)

    print(f"\n{'='*50}")
    print(f"  빌드 완료!")
    print(f"  EXE: dist/{APP_NAME}/{APP_NAME}.exe")
    installer = Path(f'dist/{APP_NAME}_Setup_{args.version}.exe')
    if installer.exists():
        print(f"  인스톨러: {installer}")
    print(f"{'='*50}")


if __name__ == '__main__':
    main()
