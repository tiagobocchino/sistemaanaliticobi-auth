"""
Test Runner Script with Accuracy Evaluation
Executes all tests and evaluates if accuracy meets 85% threshold
"""
import subprocess
import sys
import json
import os
from datetime import datetime
from typing import Dict, Any


class TestRunner:
    """Test runner with accuracy evaluation"""

    def __init__(self, accuracy_threshold: float = 85.0):
        self.accuracy_threshold = accuracy_threshold
        self.results = {
            "backend": {},
            "e2e": {},
            "overall": {}
        }

    def run_backend_tests(self) -> Dict[str, Any]:
        """Run backend API tests"""
        print("=" * 60)
        print("RUNNING BACKEND TESTS (pytest)")
        print("=" * 60)

        cmd = [
            sys.executable, "-m", "pytest",
            "tests/",
            "--ignore=tests/e2e/",
            "-v",
            "--tb=short",
            "--json-report",
            "--json-report-file=test_reports/backend_report.json",
            "--html=test_reports/backend_report.html",
            "--self-contained-html"
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(result.stdout)

            # Parse JSON report
            report_path = "test_reports/backend_report.json"
            if os.path.exists(report_path):
                with open(report_path, 'r') as f:
                    report = json.load(f)

                    passed = report.get("summary", {}).get("passed", 0)
                    failed = report.get("summary", {}).get("failed", 0)
                    total = report.get("summary", {}).get("total", 0)

                    accuracy = (passed / total * 100) if total > 0 else 0

                    self.results["backend"] = {
                        "passed": passed,
                        "failed": failed,
                        "total": total,
                        "accuracy": accuracy
                    }

                    return self.results["backend"]

        except Exception as e:
            print(f"Error running backend tests: {e}")

        return {"passed": 0, "failed": 0, "total": 0, "accuracy": 0}

    def run_e2e_tests(self) -> Dict[str, Any]:
        """Run E2E Selenium tests"""
        print("\n" + "=" * 60)
        print("RUNNING E2E TESTS (Selenium)")
        print("=" * 60)
        print("NOTE: Make sure backend (localhost:8000) and frontend (localhost:5173) are running!")
        print("=" * 60)

        cmd = [
            sys.executable, "-m", "pytest",
            "tests/e2e/",
            "-v",
            "-m", "e2e",
            "--tb=short",
            "--json-report",
            "--json-report-file=test_reports/e2e_report.json",
            "--html=test_reports/e2e_report.html",
            "--self-contained-html"
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(result.stdout)

            # Parse JSON report
            report_path = "test_reports/e2e_report.json"
            if os.path.exists(report_path):
                with open(report_path, 'r') as f:
                    report = json.load(f)

                    passed = report.get("summary", {}).get("passed", 0)
                    failed = report.get("summary", {}).get("failed", 0)
                    total = report.get("summary", {}).get("total", 0)

                    accuracy = (passed / total * 100) if total > 0 else 0

                    self.results["e2e"] = {
                        "passed": passed,
                        "failed": failed,
                        "total": total,
                        "accuracy": accuracy
                    }

                    return self.results["e2e"]

        except Exception as e:
            print(f"Error running E2E tests: {e}")

        return {"passed": 0, "failed": 0, "total": 0, "accuracy": 0}

    def calculate_overall_accuracy(self):
        """Calculate overall accuracy"""
        backend = self.results.get("backend", {})
        e2e = self.results.get("e2e", {})

        total_passed = backend.get("passed", 0) + e2e.get("passed", 0)
        total_failed = backend.get("failed", 0) + e2e.get("failed", 0)
        total_tests = backend.get("total", 0) + e2e.get("total", 0)

        overall_accuracy = (total_passed / total_tests * 100) if total_tests > 0 else 0

        self.results["overall"] = {
            "passed": total_passed,
            "failed": total_failed,
            "total": total_tests,
            "accuracy": overall_accuracy
        }

    def print_summary(self):
        """Print test summary and evaluation"""
        print("\n" + "=" * 60)
        print("TEST EXECUTION SUMMARY")
        print("=" * 60)

        backend = self.results.get("backend", {})
        e2e = self.results.get("e2e", {})
        overall = self.results.get("overall", {})

        print("\nBACKEND TESTS:")
        print(f"  Passed:   {backend.get('passed', 0)}")
        print(f"  Failed:   {backend.get('failed', 0)}")
        print(f"  Total:    {backend.get('total', 0)}")
        print(f"  Accuracy: {backend.get('accuracy', 0):.2f}%")

        print("\nE2E TESTS:")
        print(f"  Passed:   {e2e.get('passed', 0)}")
        print(f"  Failed:   {e2e.get('failed', 0)}")
        print(f"  Total:    {e2e.get('total', 0)}")
        print(f"  Accuracy: {e2e.get('accuracy', 0):.2f}%")

        print("\nOVERALL:")
        print(f"  Passed:   {overall.get('passed', 0)}")
        print(f"  Failed:   {overall.get('failed', 0)}")
        print(f"  Total:    {overall.get('total', 0)}")
        print(f"  Accuracy: {overall.get('accuracy', 0):.2f}%")

        print("\n" + "=" * 60)
        print("ACCURACY EVALUATION")
        print("=" * 60)
        print(f"Threshold: {self.accuracy_threshold}%")
        print(f"Achieved:  {overall.get('accuracy', 0):.2f}%")

        if overall.get('accuracy', 0) >= self.accuracy_threshold:
            print("\n✅ PASSED - Accuracy meets threshold!")
            print(f"   {overall.get('accuracy', 0):.2f}% >= {self.accuracy_threshold}%")
            print("\n   → Ready to proceed to next phase")
        else:
            print("\n❌ FAILED - Accuracy below threshold")
            print(f"   {overall.get('accuracy', 0):.2f}% < {self.accuracy_threshold}%")
            print("\n   → Need to fix failing tests before proceeding")
            print(f"   → Need {self.accuracy_threshold - overall.get('accuracy', 0):.2f}% more to pass")

        print("=" * 60)

        # Save summary to file
        self.save_summary()

    def save_summary(self):
        """Save test summary to JSON file"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "threshold": self.accuracy_threshold,
            "results": self.results,
            "passed": self.results["overall"].get("accuracy", 0) >= self.accuracy_threshold
        }

        os.makedirs("test_reports", exist_ok=True)

        with open("test_reports/summary.json", 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\nSummary saved to: test_reports/summary.json")

    def run_all(self, include_e2e: bool = True):
        """Run all tests"""
        # Create reports directory
        os.makedirs("test_reports", exist_ok=True)

        # Run backend tests
        self.run_backend_tests()

        # Run E2E tests if requested
        if include_e2e:
            self.run_e2e_tests()

        # Calculate overall accuracy
        self.calculate_overall_accuracy()

        # Print summary
        self.print_summary()

        # Return exit code
        overall_accuracy = self.results["overall"].get("accuracy", 0)
        return 0 if overall_accuracy >= self.accuracy_threshold else 1


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Run tests with accuracy evaluation")
    parser.add_argument(
        "--threshold",
        type=float,
        default=85.0,
        help="Accuracy threshold percentage (default: 85.0)"
    )
    parser.add_argument(
        "--backend-only",
        action="store_true",
        help="Run only backend tests (skip E2E)"
    )
    parser.add_argument(
        "--e2e-only",
        action="store_true",
        help="Run only E2E tests (skip backend)"
    )

    args = parser.parse_args()

    runner = TestRunner(accuracy_threshold=args.threshold)

    if args.e2e_only:
        runner.run_e2e_tests()
        runner.calculate_overall_accuracy()
        runner.print_summary()
    elif args.backend_only:
        runner.run_backend_tests()
        runner.calculate_overall_accuracy()
        runner.print_summary()
    else:
        exit_code = runner.run_all(include_e2e=True)
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
