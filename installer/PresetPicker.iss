; Inno Setup script for the Windows installer. Built by .github/workflows/build.yml:
;   iscc /DAppVersion=1.2.3 installer\PresetPicker.iss   ->  dist\PresetPicker-Setup-x64.exe
; Installs per user (no admin prompt) into %LOCALAPPDATA%\Programs\Preset Picker.

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif
#define AppName "Preset Picker"
#define AppExe "Preset Picker.exe"

[Setup]
AppId={{8C1F2E6A-4B7D-4E1A-9F3C-5D2B7A0E9C41}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher=Grain & Glow
AppPublisherURL=https://grainandglow.github.io/preset-picker/
AppSupportURL=https://github.com/grainandglow/preset-picker/issues
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
; x64 build; Windows 11 on ARM runs it through its built-in x64 emulation.
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
SourceDir=..
OutputDir=dist
OutputBaseFilename=PresetPicker-Setup-x64
SetupIconFile=assets\AppIcon.ico
UninstallDisplayIcon={app}\{#AppExe}
UninstallDisplayName={#AppName}
WizardStyle=modern
Compression=lzma2/max
SolidCompression=yes
CloseApplications=yes

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\{#AppName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent
