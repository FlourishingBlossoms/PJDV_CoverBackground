@echo off
set "MSVC=C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Tools\MSVC\14.51.36231"
set "SDK=C:\Program Files (x86)\Windows Kits\10"
set "SDKVER=10.0.26100.0"
setlocal
set "INCLUDE=%MSVC%\include;%SDK%\Include\%SDKVER%\ucrt;%SDK%\Include\%SDKVER%\um;%SDK%\Include\%SDKVER%\shared"
set "LIB=%MSVC%\lib\x64;%SDK%\Lib\%SDKVER%\ucrt\x64;%SDK%\Lib\%SDKVER%\um\x64"
cd /d "%~dp0"
"%MSVC%\bin\Hostx64\x64\cl.exe" /nologo /LD /O2 /MT /EHsc /utf-8 /std:c++17 BgToggle.cpp /Fe:"BgToggle.dll" /link /OUT:"BgToggle.dll" user32.lib gdi32.lib
if errorlevel 1 ( echo BUILD FAILED & exit /b 1 )
echo BUILD OK
