# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Analysis: 스크립트와 의존성을 분석
a = Analysis(
    ['launcher.py'],  # 진입점 스크립트
    pathex=['C:\\path\\to\\your\\project'],  # 프로젝트 경로
    binaries=[],  # 바이너리 파일 (예: DLL, SO 파일)
    datas=[],  # 데이터 파일 (예: 리소스 파일)
    hiddenimports=['rasterio.sample', 'rasterio.vrt', 'rasterio._features'],  # 누락된 모듈 명시적 추가
    hookspath=['./hooks'],  # hooks 폴더 경로 추가
    hooksconfig={},  # 훅 설정
    runtime_hooks=[],  # 런타임 훅
    excludes=[],  # 제외할 모듈
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

# PYZ: Python 바이트코드를 압축하여 저장
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# EXE: 실행 파일 생성
exe = EXE(
    pyz,  # PYZ 객체
    a.scripts,  # 스크립트 파일
    a.binaries,  # 바이너리 파일
    a.datas,  # 데이터 파일
    [],  # 추가적인 리소스
    name='launcher',  # 실행 파일 이름
    debug=False,  # 디버그 모드
    bootloader_ignore_signals=False,
    strip=False,  # 심볼 테이블 제거
    upx=True,  # UPX로 압축
    upx_exclude=[],  # UPX에서 제외할 파일
    runtime_tmpdir=None,  # 런타임 임시 디렉토리
    console=False,  # 콘솔 창 표시 여부 (GUI 애플리케이션인 경우 False)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,  # 타겟 아키텍처
    codesign_identity=None,  # 코드 서명 (macOS)
    entitlements_file=None,  # 권한 설정 파일 (macOS)
)
