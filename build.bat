@echo off

set VERSION=1.0.0
set DISTPATH=dist
set BUILDPATH=_build

@echo __version__ = "%VERSION%" > .\gampy\__init__.py

call poetry run black gampy
call poetry run black main.py
call poetry run pyinstaller --distpath %DISTPATH% ^
                            --workpath %BUILDPATH% ^
                            --specpath %BUILDPATH% ^
                            --add-data ..\3rdparty\GAMP\gamp.exe;. ^
                            --add-data ..\3rdparty\GAMP\gamp.cfg;. ^
                            --add-data ..\3rdparty\RNXCMP\crx2rnx.exe;. ^
                            --add-data ..\3rdparty\GZIP\gzip.exe;. ^
                            --name gampy ^
                            --onefile ^
                            --clean ^
                            main.py

copy .\dist\gampy.exe .
call tar -acf .\dist\gampy-v%VERSION%-win64.zip gampy.exe README.md gampy.cfg
del gampy.exe
