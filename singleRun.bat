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
set i=0
set n=%~4
set output=%~3

:start

set timeStart=%TIME%
%~1 > nul
set timeStop=%TIME%
if %ERRORLEVEL% NEQ 0 exit %ERRORLEVEL%

for /f "delims=:,. tokens=1-4" %%a in ("%timeStart%") do set timeS_H=%%a& set timeS_M=%%b& set timeS_S=%%c& set timeS_MS=%%d
for /f "delims=:,. tokens=1-4" %%a in ("%timeStop%") do set timeE_H=%%a& set timeE_M=%%b& set timeE_S=%%c& set timeE_MS=%%d

(for /f "tokens=* delims=0" %%N in ("%timeE_H%") do set "timeE_H=%%N")||set "timeE_H=0"
(for /f "tokens=* delims=0" %%N in ("%timeS_H%") do set "timeS_H=%%N")||set "timeS_H=0"
(for /f "tokens=* delims=0" %%N in ("%timeE_M%") do set "timeE_M=%%N")||set "timeE_M=0"
(for /f "tokens=* delims=0" %%N in ("%timeS_M%") do set "timeS_M=%%N")||set "timeS_M=0"
(for /f "tokens=* delims=0" %%N in ("%timeE_S%") do set "timeE_S=%%N")||set "timeE_S=0"
(for /f "tokens=* delims=0" %%N in ("%timeS_S%") do set "timeS_S=%%N")||set "timeS_S=0"
(for /f "tokens=* delims=0" %%N in ("%timeE_MS%") do set "timeE_MS=%%N")||set "timeE_MS=0"
(for /f "tokens=* delims=0" %%N in ("%timeS_MS%") do set "timeS_MS=%%N")||set "timeS_MS=0"

set /a timeH_Diff=(timeE_H-timeS_H)
set /a timeM_Diff=(timeE_M-timeS_M)
set /a timeS_Diff=(timeE_S-timeS_S)
set /a timeMS_Diff=(timeE_MS-timeS_MS)
set /a measuredTime=TimeH_Diff*60*60*1000
set /a measuredTime=timeM_Diff*60*1000 + measuredTime
set /a measuredTime=timeS_Diff*1000 + measuredTime
set /a measuredTime=timeMS_Diff*10 + measuredTime
if %timeE_H% LSS %timeS_H% set /a measuredTime=measuredTime+(24*60*60*1000)

if %measuredTime% LSS 0 exit -10
set output=%output%%~2%measuredTime%

set /a i=i+1
if %i% LSS %n% goto start

echo %output%
