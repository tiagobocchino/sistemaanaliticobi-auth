#!/usr/bin/env python3
"""
Test script to verify all imports are working correctly
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test all critical imports"""
    results = []

    # Test auth service
    try:
        from src.auth.service import auth_service
        results.append("✅ Auth service: OK")
    except Exception as e:
        results.append(f"❌ Auth service: {e}")

    # Test analysis service
    try:
        from src.analyses.service import analysis_service
        results.append("✅ Analysis service: OK")
    except Exception as e:
        results.append(f"❌ Analysis service: {e}")

    # Test auth routes
    try:
        from src.auth.routes import router as auth_router
        results.append("✅ Auth routes: OK")
    except Exception as e:
        results.append(f"❌ Auth routes: {e}")

    # Test analysis routes
    try:
        from src.analyses.routes import router as analyses_router
        results.append("✅ Analysis routes: OK")
    except Exception as e:
        results.append(f"❌ Analysis routes: {e}")

    # Test Power BI dashboards
    try:
        from src.analyses.powerbi_dashboards import PowerBIDashboards
        results.append("✅ Power BI dashboards: OK")
    except Exception as e:
        results.append(f"❌ Power BI dashboards: {e}")

    # Test models
    try:
        from src.auth.models import UserSignUp, UserSignIn, UserResponse
        from src.analyses.models import AnalysisResponse
        results.append("✅ Models: OK")
    except Exception as e:
        results.append(f"❌ Models: {e}")

    # Test supabase client
    try:
        from src.supabase_client import supabase_client
        results.append("✅ Supabase client: OK")
    except Exception as e:
        results.append(f"❌ Supabase client: {e}")

    return results

if __name__ == "__main__":
    print("🔍 VERIFICANDO IMPORTS DO SISTEMA")
    print("=" * 50)

    results = test_imports()

    for result in results:
        print(result)

    print("=" * 50)

    # Check if all are OK
    all_ok = all("✅" in result for result in results)

    if all_ok:
        print("🎉 SISTEMA OK: Todos os imports funcionando!")
        sys.exit(0)
    else:
        print("❌ PROBLEMAS DETECTADOS: Alguns imports falharam")
        sys.exit(1)
