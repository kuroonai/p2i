; p2i Inno Setup Installer Script
; Build the exe first with:
;   python -m nuitka --standalone --mingw64 --windows-console-mode=disable --windows-icon-from-ico=resources/icon/app_icon.ico --enable-plugin=tk-inter --include-data-dir=resources=resources --output-filename=p2i.exe --output-dir=dist --assume-yes-for-downloads main.py
; Then compile this script with Inno Setup to create the installer.

[Setup]
AppId={{A3F2B8D1-7E4C-4A9F-B6D3-8F2E1C5A7B90}
AppName=p2i
AppVersion=1.1.0
AppVerName=p2i 1.1.0
AppPublisher=Naveen Vasudevan
AppPublisherURL=https://github.com/kuroonai/p2i
AppSupportURL=https://github.com/kuroonai/p2i/issues
AppUpdatesURL=https://github.com/kuroonai/p2i/releases
DefaultDirName={autopf}\p2i
DefaultGroupName=p2i
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=installer_output
OutputBaseFilename=p2i-1.1.0-setup
SetupIconFile=resources\icon\app_icon.ico
UninstallDisplayIcon={app}\p2i.exe
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Include all files from the Nuitka standalone output
Source: "dist\main.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Include the license file in the installation directory
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\p2i"; Filename: "{app}\p2i.exe"; IconFilename: "{app}\resources\icon\app_icon.ico"
Name: "{group}\{cm:UninstallProgram,p2i}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\p2i"; Filename: "{app}\p2i.exe"; IconFilename: "{app}\resources\icon\app_icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\p2i.exe"; Description: "Launch p2i"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
var
  SupportPage: TWizardPage;
  GitHubBtn: TNewButton;
  PatreonBtn: TNewButton;
  CoffeeBtn: TNewButton;
  PayPalBtn: TNewButton;
  WebsiteBtn: TNewButton;
  IssuesBtn: TNewButton;

procedure OpenURL(Url: String);
var
  ErrCode: Integer;
begin
  ShellExec('open', Url, '', '', SW_SHOWNORMAL, ewNoWait, ErrCode);
end;

procedure GitHubBtnClick(Sender: TObject);
begin
  OpenURL('https://github.com/sponsors/kuroonai');
end;

procedure PatreonBtnClick(Sender: TObject);
begin
  OpenURL('https://www.patreon.com/kuroonai');
end;

procedure CoffeeBtnClick(Sender: TObject);
begin
  OpenURL('https://www.buymeacoffee.com/kuroonai');
end;

procedure PayPalBtnClick(Sender: TObject);
begin
  OpenURL('https://www.paypal.me/kuroonai');
end;

procedure WebsiteBtnClick(Sender: TObject);
begin
  OpenURL('https://github.com/kuroonai/p2i');
end;

procedure IssuesBtnClick(Sender: TObject);
begin
  OpenURL('https://github.com/kuroonai/p2i/issues');
end;

procedure InitializeWizard;
var
  SupportLabel: TNewStaticText;
  NoteLabel: TNewStaticText;
  BtnTop: Integer;
  BtnWidth: Integer;
  BtnHeight: Integer;
  Col1Left: Integer;
  Col2Left: Integer;
begin
  // Create custom "Support p2i" page shown after installation
  SupportPage := CreateCustomPage(wpInfoAfter,
    'Support p2i Development',
    'Thank you for installing p2i! Consider supporting the project.');

  SupportLabel := TNewStaticText.Create(SupportPage);
  SupportLabel.Parent := SupportPage.Surface;
  SupportLabel.Top := 0;
  SupportLabel.Left := 0;
  SupportLabel.Width := SupportPage.SurfaceWidth;
  SupportLabel.Height := 36;
  SupportLabel.WordWrap := True;
  SupportLabel.Caption := 'p2i is free, open-source software developed by Naveen Vasudevan. ' +
    'Your support helps maintain and improve it. Choose an option below:';

  BtnWidth := (SupportPage.SurfaceWidth - 20) div 2;
  BtnHeight := 36;
  Col1Left := 0;
  Col2Left := BtnWidth + 20;
  BtnTop := 50;

  // Row 1: GitHub Sponsors | Patreon
  GitHubBtn := TNewButton.Create(SupportPage);
  GitHubBtn.Parent := SupportPage.Surface;
  GitHubBtn.Top := BtnTop;
  GitHubBtn.Left := Col1Left;
  GitHubBtn.Width := BtnWidth;
  GitHubBtn.Height := BtnHeight;
  GitHubBtn.Caption := 'GitHub Sponsors';
  GitHubBtn.OnClick := @GitHubBtnClick;

  PatreonBtn := TNewButton.Create(SupportPage);
  PatreonBtn.Parent := SupportPage.Surface;
  PatreonBtn.Top := BtnTop;
  PatreonBtn.Left := Col2Left;
  PatreonBtn.Width := BtnWidth;
  PatreonBtn.Height := BtnHeight;
  PatreonBtn.Caption := 'Patreon';
  PatreonBtn.OnClick := @PatreonBtnClick;

  // Row 2: Buy Me A Coffee | PayPal
  BtnTop := BtnTop + BtnHeight + 10;

  CoffeeBtn := TNewButton.Create(SupportPage);
  CoffeeBtn.Parent := SupportPage.Surface;
  CoffeeBtn.Top := BtnTop;
  CoffeeBtn.Left := Col1Left;
  CoffeeBtn.Width := BtnWidth;
  CoffeeBtn.Height := BtnHeight;
  CoffeeBtn.Caption := 'Buy Me A Coffee';
  CoffeeBtn.OnClick := @CoffeeBtnClick;

  PayPalBtn := TNewButton.Create(SupportPage);
  PayPalBtn.Parent := SupportPage.Surface;
  PayPalBtn.Top := BtnTop;
  PayPalBtn.Left := Col2Left;
  PayPalBtn.Width := BtnWidth;
  PayPalBtn.Height := BtnHeight;
  PayPalBtn.Caption := 'PayPal Donate';
  PayPalBtn.OnClick := @PayPalBtnClick;

  // Row 3: Website | Report Issues
  BtnTop := BtnTop + BtnHeight + 10;

  WebsiteBtn := TNewButton.Create(SupportPage);
  WebsiteBtn.Parent := SupportPage.Surface;
  WebsiteBtn.Top := BtnTop;
  WebsiteBtn.Left := Col1Left;
  WebsiteBtn.Width := BtnWidth;
  WebsiteBtn.Height := BtnHeight;
  WebsiteBtn.Caption := 'Visit Website';
  WebsiteBtn.OnClick := @WebsiteBtnClick;

  IssuesBtn := TNewButton.Create(SupportPage);
  IssuesBtn.Parent := SupportPage.Surface;
  IssuesBtn.Top := BtnTop;
  IssuesBtn.Left := Col2Left;
  IssuesBtn.Width := BtnWidth;
  IssuesBtn.Height := BtnHeight;
  IssuesBtn.Caption := 'Report Issues';
  IssuesBtn.OnClick := @IssuesBtnClick;

  // Note about Ghostscript
  BtnTop := BtnTop + BtnHeight + 20;

  NoteLabel := TNewStaticText.Create(SupportPage);
  NoteLabel.Parent := SupportPage.Surface;
  NoteLabel.Top := BtnTop;
  NoteLabel.Left := 0;
  NoteLabel.Width := SupportPage.SurfaceWidth;
  NoteLabel.Height := 60;
  NoteLabel.WordWrap := True;
  NoteLabel.Caption := 'Note: For optimal PDF compression, install Ghostscript from ' +
    'https://www.ghostscript.com/releases/gsdnld.html and ensure gswin64c is on your PATH.' + #13#10 + #13#10 +
    'Thank you for using p2i!';
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := False;
end;
