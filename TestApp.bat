chcp 65001 > NUL
@echo off

pushd %~dp0
echo Running test_app.py...
venv\Scripts\python test_app.py

if %errorlevel% neq 0 ( pause & popd & exit /b %errorlevel% )

popd
pause