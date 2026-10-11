; 本地数字人工作台 — 精简安装包
; 构建：先跑 installer\build-staging.ps1 组装 staging，再用 ISCC 编译本脚本。
#define MyAppName "本地数字人工作台"
#define MyAppVersion "1.0.0"
#define MyAppId "{{3F9C2E71-7C4A-4C2E-9A7D-2E6C1B5A8D40}"

[Setup]
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=LocalDigitalHuman
DefaultDirName={localappdata}\Programs\LocalDigitalHuman
DefaultGroupName={#MyAppName}
PrivilegesRequired=lowest
OutputDir={#SourcePath}\output
OutputBaseFilename=本地数字人工作台-安装器-v{#MyAppVersion}
Compression=lzma2/max
SolidCompression=no
LZMAUseSeparateProcess=yes
SetupIconFile={#SourcePath}\staging\assets\app-icon.ico
WizardStyle=modern
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\assets\app-icon.ico

[Languages]
Name: "chs"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Files]
Source: "{#SourcePath}\staging\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\启动本地数字人.vbs"; IconFilename: "{app}\assets\app-icon.ico"; Tasks: desktopicon
Name: "{group}\{#MyAppName}"; Filename: "{app}\启动本地数字人.vbs"; IconFilename: "{app}\assets\app-icon.ico"

[Tasks]
Name: "desktopicon"; Description: "在桌面创建快捷方式"; GroupDescription: "附加选项："

[Run]
Filename: "{app}\启动本地数字人.vbs"; Description: "立即启动本地数字人工作台"; Flags: postinstall skipifsilent shellexec unchecked

[Code]
procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel2.Caption :=
    '安装完成后首次启动会打开「组件与下载」向导，' + #13#10 +
    '按提示安装口型模型运行环境（约 3.5GB）即可开始使用。' + #13#10 +
    '如果拿到了「组件离线包」，在向导里选择它的文件夹即可离线安装，无需联网下载。' + #13#10 + #13#10 +
    '需要 NVIDIA 显卡（建议 8GB 显存以上）；联网下载时源均为国内站点，无需翻墙。';
end;
