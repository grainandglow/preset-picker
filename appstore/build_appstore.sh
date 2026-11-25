#!/bin/zsh
# Build the Mac App Store variant of Preset Picker: sandboxed, bundle id com.grainandglow.presetpicker.
#
#   appstore/build_appstore.sh            -> dist/Preset Picker.app, signed ad hoc for testing on this Mac
#
# Once enrolled in the Apple Developer Program (certificates in your keychain, provisioning profile
# downloaded from developer.apple.com and saved as appstore/embedded.provisionprofile):
#
#   SIGN_ID="Apple Distribution: Grain & Glow (TEAMID)" \
#   INSTALLER_ID="3rd Party Mac Developer Installer: Grain & Glow (TEAMID)" \
#   appstore/build_appstore.sh
#
#   -> dist/PresetPicker-AppStore.pkg, ready to upload with the Transporter app.
set -e
cd "$(dirname "$0")/.."

SIGN_ID="${SIGN_ID:--}"
APP="dist/Preset Picker.app"
ENT=appstore/PresetPicker.entitlements
INHERIT=appstore/Inherit.entitlements

[[ -d .venv ]] || python3 -m venv .venv
./.venv/bin/pip install -q -r requirements.txt pyinstaller
./.venv/bin/python tools/make_icon.py
rm -rf build dist
PRESETPICKER_APPSTORE=1 ./.venv/bin/pyinstaller preset_picker.spec --noconfirm

if [[ "$SIGN_ID" != "-" ]]; then
  [[ -f appstore/embedded.provisionprofile ]] || { echo "Missing appstore/embedded.provisionprofile"; exit 1; }
  cp appstore/embedded.provisionprofile "$APP/Contents/embedded.provisionprofile"
fi

# Sign every library inside the app first (innermost first), then the app itself with the sandbox.
echo "Signing with: $SIGN_ID"
find "$APP/Contents" -type f \( -name "*.so" -o -name "*.dylib" -o -perm -u+x \) ! -path "*/MacOS/*" -print0 |
  while IFS= read -r -d '' f; do
    if file -b "$f" | grep -q "Mach-O"; then
      codesign --force --timestamp=none --sign "$SIGN_ID" --entitlements "$INHERIT" "$f"
    fi
  done
for fw in "$APP"/Contents/Frameworks/*.framework(N); do
  codesign --force --timestamp=none --sign "$SIGN_ID" --entitlements "$INHERIT" "$fw"
done
codesign --force --timestamp=none --sign "$SIGN_ID" --entitlements "$ENT" "$APP"
codesign --verify --strict --deep "$APP"
echo "Signed: $APP"

if [[ "$SIGN_ID" != "-" ]]; then
  [[ -n "$INSTALLER_ID" ]] || { echo "Set INSTALLER_ID to make the .pkg"; exit 1; }
  productbuild --component "$APP" /Applications --sign "$INSTALLER_ID" dist/PresetPicker-AppStore.pkg
  echo "Ready to upload: dist/PresetPicker-AppStore.pkg"
fi
