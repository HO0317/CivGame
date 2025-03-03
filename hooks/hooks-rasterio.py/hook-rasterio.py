# hooks/hook-rasterio.py
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# rasterio와 관련된 모든 모듈 포함
hiddenimports = collect_submodules('rasterio')

# rasterio와 관련된 데이터 파일 포함
datas = collect_data_files('rasterio')
