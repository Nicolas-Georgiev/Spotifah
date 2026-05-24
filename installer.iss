; ============================================================
;  EKHO - Inno Setup Installer Script
;  Requiere: Inno Setup 6+ (https://jrsoftware.org/isinfo.php)
;  Uso: Primero ejecuta build.bat, luego compila este .iss
; ============================================================

#define AppName      "EKHO"
#define AppVersion   "1.0.0"
#define AppPublisher "Nicolas Georgiev"
#define AppURL       "https://github.com/Nicolas-Georgiev/Spotifah"
#define AppExe       "EKHO.exe"
#define AppDataDir   "{userappdata}\EKHO"

[Setup]
AppId                    = {{8F3A2C1D-4E7B-4F9A-8D2E-1C6B5A3F9E0D}
AppName                  = {#AppName}
AppVersion               = {#AppVersion}
AppVerName               = {#AppName} {#AppVersion}
AppPublisher             = {#AppPublisher}
AppPublisherURL          = {#AppURL}
AppSupportURL            = {#AppURL}
AppUpdatesURL            = {#AppURL}
DefaultDirName           = {autopf}\{#AppName}
DefaultGroupName         = {#AppName}
AllowNoIcons             = yes
; Requiere permisos de administrador para instalar en Archivos de Programa
PrivilegesRequired       = admin
OutputDir                = dist\installer
OutputBaseFilename       = EKHO-Setup-{#AppVersion}
SetupIconFile            = assets\icons\logo-ekho.ico
UninstallDisplayIcon     = {app}\{#AppExe}
; onedir: todos los archivos de la app van en la misma carpeta
DiskSpanning             = no
UninstallDisplayName     = {#AppName} {#AppVersion}
Compression              = lzma2/ultra64
SolidCompression         = yes
WizardStyle              = modern
; Crear acceso directo de desinstalación en el Panel de Control
ChangesAssociations      = no
DisableProgramGroupPage  = yes
; No permitir que se instale encima de versiones anteriores sin desinstalar
CloseApplications        = yes
CloseApplicationsFilter  = {#AppExe}
RestartApplications      = no
; Mostrar README al final
InfoAfterFile            = README.md

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon";    Description: "Crear icono en el &Escritorio";         GroupDescription: "Iconos adicionales:"; Flags: unchecked
Name: "startupicon";    Description: "Ejecutar EKHO al &iniciar Windows";     GroupDescription: "Iconos adicionales:"; Flags: unchecked

[Files]
; Todos los archivos generados por PyInstaller --onedir
Source: "dist\EKHO\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Icono de la aplicación (copia extra para accesos directos)
Source: "assets\icons\logo-ekho.ico"; DestDir: "{app}\icons"; Flags: ignoreversion

[Dirs]
; Estructura de datos en AppData (se crea en primer arranque también, pero lo hacemos aquí por si acaso)
Name: "{#AppDataDir}\data\music"
Name: "{#AppDataDir}\data\BDD"
Name: "{#AppDataDir}\data\covers"
Name: "{#AppDataDir}\data\metadata"
Name: "{#AppDataDir}\data\temp"

[Icons]
; Menú inicio
Name: "{group}\{#AppName}";              Filename: "{app}\{#AppExe}"; IconFilename: "{app}\icons\logo-ekho.ico"
Name: "{group}\Desinstalar {#AppName}";  Filename: "{uninstallexe}"

; Escritorio (opcional)
Name: "{autodesktop}\{#AppName}";        Filename: "{app}\{#AppExe}"; IconFilename: "{app}\icons\logo-ekho.ico"; Tasks: desktopicon

; Inicio de Windows (opcional)
Name: "{userstartup}\{#AppName}";        Filename: "{app}\{#AppExe}"; IconFilename: "{app}\icons\logo-ekho.ico"; Tasks: startupicon

[Run]
; Ofrecer abrir la app al terminar la instalación
Filename: "{app}\{#AppExe}"; Description: "Abrir {#AppName} ahora"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Limpiar archivos temporales generados por la app en AppData al desinstalar
Type: filesandordirs; Name: "{#AppDataDir}\data\temp"

[Code]
// ---------------------------------------------------------------
//  Verificación de FFmpeg en el PATH antes de instalar
// ---------------------------------------------------------------
function FFmpegFound(): Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec(ExpandConstant('{cmd}'), '/C ffmpeg -version >nul 2>&1', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Result := Result and (ResultCode = 0);
end;

procedure CreateDefaultSettings();
var
  SettingsPath: String;
  MusicPath: String;
  JsonContent: String;
begin
  SettingsPath := ExpandConstant('{userappdata}\EKHO\data\settings.json');
  MusicPath    := ExpandConstant('{userdocs}\EKHO Music');
  if not FileExists(SettingsPath) then
  begin
    ForceDirectories(ExtractFileDir(SettingsPath));
    ForceDirectories(MusicPath);
    JsonContent := '{' + #13#10 +
      '  "volume": 80,' + #13#10 +
      '  "theme": "dark",' + #13#10 +
      '  "download_quality": "256",' + #13#10 +
      '  "autoplay": true,' + #13#10 +
      '  "crossfade": true,' + #13#10 +
      '  "automix": false,' + #13#10 +
      '  "crossfade_duration": 5,' + #13#10 +
      '  "download_path": "' + StringChange(MusicPath, '\', '/') + '"' + #13#10 +
      '}';
    SaveStringToFile(SettingsPath, JsonContent, False);
  end;
end;

procedure InitializeWizard();
begin
  // No bloquear, solo advertir
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = wpReady then
  begin
    if not FFmpegFound() then
    begin
      if MsgBox(
        'FFmpeg no fue encontrado en el PATH del sistema.' + #13#10 + #13#10 +
        'FFmpeg es necesario para descargar y convertir música.' + #13#10 +
        'Puedes instalarlo después con:' + #13#10 +
        '  winget install Gyan.FFmpeg' + #13#10 + #13#10 +
        '¿Deseas continuar la instalación de todas formas?',
        mbConfirmation, MB_YESNO
      ) = IDNO then
        Result := False;
    end;
  end;
end;

// ---------------------------------------------------------------
//  Al desinstalar: preguntar si borrar datos del usuario
// ---------------------------------------------------------------
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    CreateDefaultSettings();
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataPath: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    DataPath := ExpandConstant('{userappdata}\EKHO');
    if DirExists(DataPath) then
    begin
      if MsgBox(
        'Se encontraron datos de usuario en:' + #13#10 + DataPath + #13#10 + #13#10 +
        '¿Deseas eliminar también tu biblioteca de música y configuración?' + #13#10 +
        '(Esta acción no se puede deshacer)',
        mbConfirmation, MB_YESNO
      ) = IDYES then
        DelTree(DataPath, True, True, True);
    end;
  end;
end;
