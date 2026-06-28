; TetrioCoach NSIS Installer Script
; Requires NSIS 3.x with MUI2

!include "MUI2.nsh"
!include "FileFunc.nsh"

; ── App Info ──
!define APPNAME "TetrioCoach"
!define APPVERSION "1.0.0"
!define PUBLISHER "TetrioCoach"
!define HELPURL "https://github.com/tetriocoach"
!define INSTALLSIZE 200000

; ── General ──
Name "${APPNAME} ${APPVERSION}"
OutFile "dist\TetrioCoach_Setup_${APPVERSION}.exe"
InstallDir "$LOCALAPPDATA\${APPNAME}"
InstallDirRegKey HKCU "Software\${APPNAME}" "InstallDir"
RequestExecutionLevel user
Unicode true

; ── MUI Settings ──
!define MUI_ABORTWARNING
!define MUI_ICON "assets\tetrio_coach.ico"
!define MUI_UNICON "assets\tetrio_coach.ico"

; ── Pages ──
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\TetrioCoach.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch TetrioCoach"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; ── Languages ──
!insertmacro MUI_LANGUAGE "Korean"
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "SimpChinese"
!insertmacro MUI_LANGUAGE "Japanese"

; ── Language Selection on Init ──
Function .onInit
    !insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd

; ── Install Section ──
Section "Install"
    SetOutPath "$INSTDIR"

    ; Copy all files from PyInstaller dist
    File /r "dist\TetrioCoach\*.*"

    ; Write language preference
    FileOpen $0 "$INSTDIR\install_lang.txt" w
    FileWrite $0 "$LANGUAGE"
    FileClose $0

    ; Save install dir to registry
    WriteRegStr HKCU "Software\${APPNAME}" "InstallDir" "$INSTDIR"

    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"

    ; Desktop shortcut
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\TetrioCoach.exe" "" "$INSTDIR\TetrioCoach.exe" 0

    ; Start Menu
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\TetrioCoach.exe" "" "$INSTDIR\TetrioCoach.exe" 0
    CreateShortCut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"

    ; Add/Remove Programs registry
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" '"$INSTDIR\Uninstall.exe" /S'
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$INSTDIR\TetrioCoach.exe"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${PUBLISHER}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${APPVERSION}"
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1

    ; Estimated size
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" "$0"
SectionEnd

; ── Uninstall Section ──
Section "Uninstall"
    ; Remove app files
    RMDir /r "$INSTDIR"

    ; Remove shortcuts
    Delete "$DESKTOP\${APPNAME}.lnk"
    RMDir /r "$SMPROGRAMS\${APPNAME}"

    ; Remove registry
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
    DeleteRegKey HKCU "Software\${APPNAME}"

    ; Ask about user data
    MessageBox MB_YESNO "Remove user settings and training reports?" IDNO skip_userdata
        RMDir /r "$PROFILE\.tetrio_coach_reports"
        Delete "$PROFILE\.tetrio_coach_lang"
    skip_userdata:
SectionEnd
