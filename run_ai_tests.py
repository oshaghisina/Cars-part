#!/usr/bin/env python3
"""
AI Test Runner

This script runs the comprehensive AI testing suite and generates detailed reports.
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ai_tests.log')
    ]
)

logger = logging.getLogger(__name__)

# Set test environment variables
os.environ['AI_GATEWAY_ENABLED'] = 'true'
os.environ['AI_GATEWAY_EXPERIMENTAL'] = 'false'
os.environ['OPENAI_API_KEY'] = 'TEST_API_KEY'
os.environ['DATABASE_URL'] = 'sqlite:///./data/test.db'
os.environ['REDIS_URL'] = 'redis://localhost:6379/0'

from tests.ai.test_ai_framework import AITestSuite


class AITestRunner:
    """AI Test Runner with reporting and analysis."""
    
    def __init__(self):
        self.test_suite = AITestSuite()
        self.results = None
        self.start_time = None
        self.end_time = None
    
    async def run_tests(self, categories=None, verbose=False):
        """Run AI tests with optional category filtering."""
        self.start_time = time.time()
        
        logger.info("Starting AI Test Suite...")
        print("🚀 Starting AI Test Suite...")
        print("=" * 60)
        
        try:
            if categories:
                # Run specific test categories
                results = await self._run_specific_categories(categories)
            else:
                # Run all tests
                results = await self.test_suite.run_all_tests()
            
            self.results = results
            self.end_time = time.time()
            
            # Generate reports
            await self._generate_reports()
            
            # Print summary
            self._print_summary()
            
            return results
            
        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            print(f"❌ Test suite failed: {e}")
            raise
    
    async def _run_specific_categories(self, categories):
        """Run specific test categories."""
        results = {"categories": {}, "total_tests": 0, "passed_tests": 0}
        
        category_functions = {
            "unit": self.test_suite.run_unit_tests,
            "integration": self.test_suite.run_integration_tests,
            "performance": self.test_suite.run_performance_tests,
            "validation": self.test_suite.run_validation_tests,
            "api": self.test_suite.run_api_tests,
            "e2e": self.test_suite.run_end_to_end_tests
        }
        
        for category in categories:
            if category in category_functions:
                logger.info(f"Running {category} tests...")
                print(f"🧪 Running {category} tests...")
                
                try:
                    category_results = await category_functions[category]()
                    results["categories"][category] = category_results
                    results["total_tests"] += category_results.get("total_tests", 0)
                    results["passed_tests"] += category_results.get("passed_tests", 0)
                except Exception as e:
                    logger.error(f"Error in {category} tests: {e}")
                    results["categories"][category] = {
                        "status": "error",
                        "error": str(e),
                        "total_tests": 0,
                        "passed_tests": 0
                    }
            else:
                logger.warning(f"Unknown test category: {category}")
                print(f"⚠️  Unknown test category: {category}")
        
        # Calculate success rate
        results["failed_tests"] = results["total_tests"] - results["passed_tests"]
        results["success_rate"] = (results["passed_tests"] / results["total_tests"] * 100) if results["total_tests"] > 0 else 0
        results["total_time"] = time.time() - (self.start_time or 0)
        results["timestamp"] = datetime.now().isoformat()
        
        return results
    
    async def _generate_reports(self):
        """Generate test reports."""
        if not self.results:
            return
        
        # Generate JSON report
        await self._generate_json_report()
        
        # Generate HTML report
        await self._generate_html_report()
        
        # Generate Markdown report
        await self._generate_markdown_report()
    
    async def _generate_json_report(self):
        """Generate JSON test report."""
        report_path = "ai_test_report.json"
        
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        logger.info(f"JSON report generated: {report_path}")
        print(f"📄 JSON report generated: {report_path}")
    
    async def _generate_html_report(self):
        """Generate HTML test report."""
        html_content = self._generate_html_content()
        report_path = "ai_test_report.html"
        
        with open(report_path, 'w') as f:
            f.write(html_content)
        
        logger.info(f"HTML report generated: {report_path}")
        print(f"🌐 HTML report generated: {report_path}")
    
    async def _generate_markdown_report(self):
        """Generate Markdown test report."""
        markdown_content = self._generate_markdown_content()
        report_path = "ai_test_report.md"
        
        with open(report_path, 'w') as f:
            f.write(markdown_content)
        
        logger.info(f"Markdown report generated: {report_path}")
        print(f"📝 Markdown report generated: {report_path}")
    
    def _generate_html_content(self):
        """Generate HTML report content."""
        results = self.results
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AI Gateway Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .category {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .passed {{ color: #28a745; }}
        .failed {{ color: #dc3545; }}
        .error {{ color: #ffc107; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>AI Gateway Test Report</h1>
        <p>Generated: {results.get('timestamp', 'Unknown')}</p>
        <p>Total Time: {results.get('total_time', 0):.2f} seconds</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Total Tests:</strong> {results.get('total_tests', 0)}</p>
        <p><strong>Passed:</strong> <span class="passed">{results.get('passed_tests', 0)}</span></p>
        <p><strong>Failed:</strong> <span class="failed">{results.get('failed_tests', 0)}</span></p>
        <p><strong>Success Rate:</strong> {results.get('success_rate', 0):.1f}%</p>
    </div>
    
    <h2>Test Categories</h2>
"""
        
        for category, category_results in results.get('categories', {}).items():
            status_class = "passed" if category_results.get('status') == 'completed' else "error"
            html += f"""
    <div class="category">
        <h3 class="{status_class}">{category.title()} Tests</h3>
        <p><strong>Status:</strong> {category_results.get('status', 'Unknown')}</p>
        <p><strong>Tests:</strong> {category_results.get('total_tests', 0)}</p>
        <p><strong>Passed:</strong> {category_results.get('passed_tests', 0)}</p>
"""
            
            if 'tests' in category_results:
                html += """
        <table>
            <tr>
                <th>Test Name</th>
                <th>Status</th>
                <th>Duration</th>
            </tr>
"""
                for test in category_results['tests']:
                    status_class = "passed" if test.get('status') == 'passed' else "failed"
                    html += f"""
            <tr>
                <td>{test.get('name', 'Unknown')}</td>
                <td class="{status_class}">{test.get('status', 'Unknown')}</td>
                <td>{test.get('duration', 0):.3f}s</td>
            </tr>
"""
                html += "        </table>"
            
            html += "    </div>"
        
        html += """
</body>
</html>
"""
        return html
    
    def _generate_markdown_content(self):
        """Generate Markdown report content."""
        results = self.results
        
        markdown = f"""# AI Gateway Test Report

**Generated:** {results.get('timestamp', 'Unknown')}  
**Total Time:** {results.get('total_time', 0):.2f} seconds

## Summary

- **Total Tests:** {results.get('total_tests', 0)}
- **Passed:** {results.get('passed_tests', 0)}
- **Failed:** {results.get('failed_tests', 0)}
- **Success Rate:** {results.get('success_rate', 0):.1f}%

## Test Categories

"""
        
        for category, category_results in results.get('categories', {}).items():
            status_icon = "✅" if category_results.get('status') == 'completed' else "❌"
            markdown += f"""### {status_icon} {category.title()} Tests

- **Status:** {category_results.get('status', 'Unknown')}
- **Tests:** {category_results.get('total_tests', 0)}
- **Passed:** {category_results.get('passed_tests', 0)}

"""
            
            if 'tests' in category_results:
                markdown += "| Test Name | Status | Duration |\n"
                markdown += "|-----------|--------|----------|\n"
                
                for test in category_results['tests']:
                    status_icon = "✅" if test.get('status') == 'passed' else "❌"
                    markdown += f"| {test.get('name', 'Unknown')} | {status_icon} {test.get('status', 'Unknown')} | {test.get('duration', 0):.3f}s |\n"
                
                markdown += "\n"
        
        return markdown
    
    def _print_summary(self):
        """Print test summary to console."""
        results = self.results
        
        print("\n" + "=" * 60)
        print("AI TEST SUITE RESULTS")
        print("=" * 60)
        print(f"Total Tests: {results.get('total_tests', 0)}")
        print(f"Passed: {results.get('passed_tests', 0)}")
        print(f"Failed: {results.get('failed_tests', 0)}")
        print(f"Success Rate: {results.get('success_rate', 0):.1f}%")
        print(f"Total Time: {results.get('total_time', 0):.2f}s")
        print("=" * 60)
        
        # Print category results
        for category, category_results in results.get('categories', {}).items():
            status_icon = "✅" if category_results.get('status') == 'completed' else "❌"
            print(f"\n{status_icon} {category.upper()}:")
            print(f"  Tests: {category_results.get('total_tests', 0)}")
            print(f"  Passed: {category_results.get('passed_tests', 0)}")
            print(f"  Status: {category_results.get('status', 'unknown')}")
        
        print("\n" + "=" * 60)
        
        # Print overall status
        if results.get('success_rate', 0) >= 90:
            print("🎉 Excellent! All tests are passing.")
        elif results.get('success_rate', 0) >= 80:
            print("✅ Good! Most tests are passing.")
        elif results.get('success_rate', 0) >= 70:
            print("⚠️  Warning! Some tests are failing.")
        else:
            print("❌ Critical! Many tests are failing.")


async def main():
    """Main function to run AI tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run AI Gateway tests")
    parser.add_argument("--categories", nargs="+", 
                       choices=["unit", "integration", "performance", "validation", "api", "e2e"],
                       help="Specific test categories to run")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose output")
    parser.add_argument("--quick", action="store_true",
                       help="Run quick tests only (unit and integration)")
    
    args = parser.parse_args()
    
    # Set categories
    if args.quick:
        categories = ["unit", "integration"]
    elif args.categories:
        categories = args.categories
    else:
        categories = None
    
    # Run tests
    runner = AITestRunner()
    
    try:
        results = await runner.run_tests(categories=categories, verbose=args.verbose)
        
        # Exit with appropriate code
        if results.get('success_rate', 0) >= 80:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure
            
    except Exception as e:
        logger.error(f"Test runner failed: {e}")
        print(f"❌ Test runner failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
