@echo off
setlocal
call :setESC

:req
	echo %ESC%[34m[+] Note: This script has only been tested for docker using WSL2. It might work with Hyper-V, but it was not tested.%ESC%[0m
	REM echo %ESC%[93m[+] Challenge Integrity is disabled for Windows%ESC%[0m
	where docker > NUL 2>&1
	if %ERRORLEVEL% NEQ 0 (
		ECHO %ESC%[31m[+] docker command not found. Is docker installed?%ESC%[0m
		exit /B 1
	)
	docker ps >NUL 2>&1
	if %ERRORLEVEL% NEQ 0 (
		ECHO %ESC%[31m[+] "docker ps" failed. Is docker running?%ESC%[0m
		exit /B 1
	)
	
	

:build
	echo %ESC%[34m[+] Building Challenge Container%ESC%[0m
	REM !!! THIS DOES NOT WORK IF YOU ARE IN A SYMLINKED FOLDER !!!
  docker build -t localhost/chall-crypto --platform linux/amd64 --pull=true   .

:run
	echo %ESC[34m[+] Running Challenge Container on 127.0.0.1:1337%ESC%[0m"
  docker run --name chall-crypto --rm -p 127.0.0.1:1337:1337 -e HOST=127.0.0.1 -e PORT=1337 -e TIMEOUT=30 --read-only --privileged --pull=never --platform linux/amd64 localhost/chall-crypto

:setESC
for /F "tokens=1,2 delims=#" %%a in ('"prompt ### & echo on & for %%b in (1) do rem"') do (
	  set ESC=%%b
	    exit /B 0
    )
    exit /B 0
