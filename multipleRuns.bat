:: (C) Copyright 2018-2019 Hewlett Packard Enterprise Development LP

:: Permission is hereby granted, free of charge, to any person obtaining a
:: copy of this software and associated documentation files (the "Software"),
:: to deal in the Software without restriction, including without limitation
:: the rights to use, copy, modify, merge, publish, distribute, sublicense,
:: and/or sell copies of the Software, and to permit persons to whom the
:: Software is furnished to do so, subject to the following conditions:

:: The above copyright notice and this permission notice shall be included
:: in all copies or substantial portions of the Software.

:: THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
:: IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
:: FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
:: THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
:: OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
:: ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
:: OTHER DEALINGS IN THE SOFTWARE.

@echo off
setlocal
set thread_count=%~2
set OMP_DYNAMIC=0
goto startLoop

:cmd
cmd /c singleRun.bat "%~1" %5 "%~6%thread_count%" %7
if %ERRORLEVEL% NEQ 0 exit %ERRORLEVEL%
goto afterrun

:ps
powershell.exe .\singleRun.ps1 -executable "'%~1'" -delim "'%~5'" -testCase "%~6%thread_count%" -n %7
if %ERRORLEVEL% NEQ 0 exit %ERRORLEVEL%
goto afterrun

:startLoop
set OMP_NUM_THREADS=%thread_count%

if "%~8" EQU "cmd" goto cmd
if "%~8" EQU "ps" goto ps
%~1 %5 "%~6%thread_count%" 1 > nul
%~1 %5 "%~6%thread_count%" %7
if %ERRORLEVEL% NEQ 0 exit %ERRORLEVEL%

:afterrun
set /a thread_count=thread_count+%~3
if %thread_count% LEQ %~4 goto startLoop
goto end



:end
