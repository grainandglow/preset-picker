# PyInstaller build for Windows (x64 / ARM64) and macOS. Run via build.sh or the GitHub workflow:
#   pyinstaller preset_picker.spec --noconfirm
import os
import sys

from PyInstaller.utils.hooks import collect_data_files

sys.path.insert(0, os.path.abspath(SPECPATH))
from presetpicker import APP_NAME, __version__  # noqa: E402

mac = sys.platform == "darwin"
# PRESETPICKER_APPSTORE=1 (set by appstore/build_appstore.sh) makes the Mac App Store variant.
appstore = mac and bool(os.environ.get("PRESETPICKER_APPSTORE"))

a = Analysis(
    ["main.py"],
    datas=[("presetpicker/ui", "presetpicker/ui")] + collect_data_files("webview"),
    hiddenimports=["exifread", "pillow_heif"] if not mac else [],
    excludes=["tkinter", "PyQt5", "PyQt6", "PySide6", "gi", "unittest", "test"],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name=APP_NAME,
    console=False,
    icon="assets/AppIcon.icns" if mac else "assets/AppIcon.ico",
)
coll = COLLECT(exe, a.binaries, a.datas, name=APP_NAME)

if mac:
    app = BUNDLE(
        coll,
        name=f"{APP_NAME}.app",
        icon="assets/AppIcon.icns",
        bundle_identifier="com.grainandglow.presetpicker" if appstore else "io.github.presetpicker",
        version=__version__,
        info_plist={
            "CFBundleDisplayName": APP_NAME,
            "CFBundleShortVersionString": __version__,
            "LSMinimumSystemVersion": "11.0",
            "NSHighResolutionCapable": True,
            "NSRequiresAquaSystemAppearance": False,
            "NSRemovableVolumesUsageDescription": "Preset Picker reads photos from your camera's memory card.",
            "NSDesktopFolderUsageDescription": "Preset Picker saves exported photos to your Desktop.",
            "NSDocumentsFolderUsageDescription": "Preset Picker reads presets and photos you choose.",
            "NSHumanReadableCopyright": "© 2026 Grain & Glow",
            "LSApplicationCategoryType": "public.app-category.photography",
            "ITSAppUsesNonExemptEncryption": False,
        },
    )
