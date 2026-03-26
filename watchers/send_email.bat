@echo off
REM Quick Email Send via MCP Server
REM Usage: send_email.bat <to> <subject> <body>

if "%1"=="" (
    echo ============================================
    echo  Quick Email Send via MCP
    echo ============================================
    echo.
    echo Usage: send_email.bat ^<to^> ^<subject^> ^<body^>
    echo.
    echo Example:
    echo   send_email.bat "client@example.com" "Hello" "Dear Client, This is a test."
    echo.
    exit /b 1
)

set TO=%1
set SUBJECT=%2
set BODY=%3

echo Sending email to %TO%...

python mcp-client.py call -s "npx -y @modelcontextprotocol/server-email" -t email_send -p "{\"to\": \"%TO%\", \"subject\": \"%SUBJECT%\", \"body\": \"%BODY%\"}"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Email sent successfully!
) else (
    echo.
    echo Failed to send email.
)
