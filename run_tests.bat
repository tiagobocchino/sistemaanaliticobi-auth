@echo off
REM Test Runner Script for Windows
REM Runs all tests and evaluates accuracy

echo ===================================
echo Analytics Platform - Test Runner
echo ===================================
echo.

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo WARNING: Virtual environment not activated
    echo Please activate your virtual environment first
    echo.
    pause
    exit /b 1
)

REM Install test dependencies if not installed
echo Installing test dependencies...
pip install -q -r requirements-test.txt

echo.
echo Starting test execution...
echo.

REM Run the test runner
python run_tests.py %*

echo.
echo Test execution completed!
echo Check test_reports/ directory for detailed reports
echo.
pause
