@echo off
chcp 65001 >nul
title Network scanner

echo ========================================
echo       Network Scanner Launcher
echo ========================================
echo.

echo Проверяю версию python...
python --version
echo Если Python не установлен, необходимо его установить.

if not exist venv\ (
    echo Создаю виртуальное окружение...
    python -m venv venv
	echo Обновляю pip...
	call .\venv\Scripts\python.exe -m pip install --upgrade pip

    if errorlevel 1 (
        echo Ошибка создания виртуального окружения!
        pause
        exit /b 1
    )
    echo Виртуальное окружение создано
    echo.
    
    echo Устанавливаю зависимости...
    call .\venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Ошибка установки зависимостей!
        pause
        exit /b 1
    )
    echo Зависимости установлены
    echo.
)

echo Запускаю скрипт...
call .\venv\Scripts\python.exe network_scanner.py

if errorlevel 1 (
    echo.
    echo Скрипт завершился с ошибкой
)

echo.
pause