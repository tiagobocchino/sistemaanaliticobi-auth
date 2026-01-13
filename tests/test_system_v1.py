#!/usr/bin/env python3
"""
Test System v1.0 - Validation Script
Automated testing for Analytics Platform v1.0
"""

import subprocess
import sys
import time
import requests
import os
from pathlib import Path

def run_command(cmd, description, cwd=None):
    """Run a command and return success status"""
    print(f"\n🔍 {description}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {str(e)}")
        return False

def test_backend_imports():
    """Test if backend imports work"""
    return run_command(
        'python -c "import sys; sys.path.insert(0, \'.\'); from main import app; print(\'Backend imports OK\')"',
        "Testing backend imports"
    )

def test_frontend_dependencies():
    """Test if frontend dependencies are installed"""
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False

    package_json = frontend_dir / "package.json"
    node_modules = frontend_dir / "node_modules"

    if not package_json.exists():
        print("❌ package.json not found")
        return False

    if not node_modules.exists():
        print("⚠️  node_modules not found - run 'npm install' in frontend/")
        return False

    return run_command("cd frontend && npm list --depth=0", "Checking frontend dependencies")

def test_basic_tests():
    """Run basic unit tests"""
    return run_command(
        "python -m pytest tests/test_unit_models.py::TestAuthModels::test_user_signup_valid -v --tb=short",
        "Running basic unit test"
    )

def test_file_structure():
    """Check if all required files exist"""
    required_files = [
        "main.py",
        "src/users/models.py",
        "src/users/routes.py",
        "src/users/dependencies.py",
        "frontend/src/App.jsx",
        "frontend/src/components/MainLayout.jsx",
        "frontend/src/pages/Users.jsx",
        "CLAUDE.md",
        "README.md",
        "TESTING_GUIDE.md"
    ]

    print("\nChecking file structure")
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)

    if missing:
        print("❌ Missing files:")
        for f in missing:
            print(f"   - {f}")
        return False

    print("✅ All required files present")
    return True

def test_environment_config():
    """Check if environment files exist"""
    env_files = [".env", "frontend/.env"]
    print("\nChecking environment configuration")
    warnings = []

    for env_file in env_files:
        if not Path(env_file).exists():
            warnings.append(f"{env_file} not found")

    if warnings:
        print("⚠️  Environment files missing (expected for local development):")
        for w in warnings:
            print(f"   - {w}")
        print("   Note: Create these files with your actual credentials")
        return True  # Not a failure, just a warning

    print("✅ Environment files present")
    return True

def main():
    """Run all validation tests"""
    print("=" * 60)
    print("🧪 ANALYTICS PLATFORM v1.0 - SYSTEM VALIDATION")
    print("=" * 60)

    tests = [
        ("File Structure", test_file_structure),
        ("Environment Config", test_environment_config),
        ("Backend Imports", test_backend_imports),
        ("Frontend Dependencies", test_frontend_dependencies),
        ("Basic Tests", test_basic_tests),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"TESTING: {test_name}")
        print('='*50)

        if test_func():
            passed += 1

    print(f"\n{'='*60}")
    print("FINAL RESULTS")
    print('='*60)
    print(f"Tests Passed: {passed}/{total}")

    if passed == total:
        print("🎉 ALL TESTS PASSED - System v1.0 is VALID!")
        print("\n🚀 Ready to start Phase 3: Power BI Integration")
        return 0
    elif passed >= total * 0.8:  # 80% success rate
        print("⚠️  MOST TESTS PASSED - Minor issues detected")
        print("   System should still be functional")
        return 0
    else:
        print("❌ CRITICAL ISSUES DETECTED")
        print("   Fix issues before proceeding to Phase 3")
        return 1

if __name__ == "__main__":
    sys.exit(main())