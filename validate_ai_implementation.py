#!/usr/bin/env python3
"""
AI Implementation Validation Script

This script validates the complete AI Gateway implementation by checking
all components, dependencies, and functionality.
"""

import asyncio
import importlib
import inspect
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add the project root to Python path
project_root = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Set test environment variables
os.environ['AI_GATEWAY_ENABLED'] = 'true'
os.environ['AI_GATEWAY_EXPERIMENTAL'] = 'false'
os.environ['OPENAI_API_KEY'] = 'TEST_API_KEY'
os.environ['DATABASE_URL'] = 'sqlite:///./data/test.db'
os.environ['REDIS_URL'] = 'redis://localhost:6379/0'


class AIImplementationValidator:
    """Validates the complete AI Gateway implementation."""
    
    def __init__(self):
        self.validation_results = {}
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0
    
    async def validate_all(self) -> Dict[str, Any]:
        """Run all validation checks."""
        logger.info("Starting AI Implementation Validation...")
        print("🔍 Starting AI Implementation Validation...")
        print("=" * 60)
        
        # Run validation categories
        validation_categories = [
            ("import_validation", self.validate_imports),
            ("component_validation", self.validate_components),
            ("api_validation", self.validate_api_endpoints),
            ("frontend_validation", self.validate_frontend),
            ("configuration_validation", self.validate_configuration),
            ("dependency_validation", self.validate_dependencies),
            ("integration_validation", self.validate_integration),
            ("performance_validation", self.validate_performance)
        ]
        
        for category_name, validation_function in validation_categories:
            logger.info(f"Running {category_name}...")
            print(f"🔍 Running {category_name}...")
            
            try:
                category_results = await validation_function()
                self.validation_results[category_name] = category_results
            except Exception as e:
                logger.error(f"Error in {category_name}: {e}")
                self.validation_results[category_name] = {
                    "status": "error",
                    "error": str(e),
                    "checks": 0,
                    "passed": 0
                }
        
        # Generate summary
        summary = self._generate_summary()
        
        # Print results
        self._print_results()
        
        return summary
    
    async def validate_imports(self) -> Dict[str, Any]:
        """Validate that all required modules can be imported."""
        results = {"checks": 0, "passed": 0, "errors": []}
        
        # Core AI modules
        ai_modules = [
            "app.services.ai_orchestrator",
            "app.services.ai_provider",
            "app.services.ai_client",
            "app.services.ai_cache",
            "app.services.ai_performance",
            "app.services.ai_resource_manager",
            "app.services.ai_policy_engine",
            "app.services.ai_context",
            "app.services.ai_normalizer",
            "app.services.ai_fallback_manager",
            "app.services.ai_tracing",
            "app.services.ai_metrics",
            "app.services.ai_language_processor",
            "app.services.ai_hybrid_search",
            "app.services.ai_recommendations",
            "app.services.ai_query_processor"
        ]
        
        for module_name in ai_modules:
            results["checks"] += 1
            try:
                importlib.import_module(module_name)
                results["passed"] += 1
                logger.debug(f"✅ Imported {module_name}")
            except ImportError as e:
                error_msg = f"Failed to import {module_name}: {e}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
        
        # API modules
        api_modules = [
            "app.api.routers.ai_advanced",
            "app.api.routers.ai_chat"
        ]
        
        for module_name in api_modules:
            results["checks"] += 1
            try:
                importlib.import_module(module_name)
                results["passed"] += 1
                logger.debug(f"✅ Imported {module_name}")
            except ImportError as e:
                error_msg = f"Failed to import {module_name}: {e}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
        
        results["status"] = "completed" if results["errors"] == [] else "failed"
        return results
    
    async def validate_components(self) -> Dict[str, Any]:
        """Validate AI component instantiation and basic functionality."""
        results = {"checks": 0, "passed": 0, "errors": []}
        
        try:
            # Test AI Orchestrator
            results["checks"] += 1
            from app.services.ai_orchestrator import AIOrchestrator
            orchestrator = AIOrchestrator()
            orchestrator.initialize()
            assert orchestrator._initialized, "Orchestrator not initialized"
            results["passed"] += 1
            logger.debug("✅ AI Orchestrator initialized")
        except Exception as e:
            error_msg = f"AI Orchestrator validation failed: {e}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        try:
            # Test AI Cache Manager
            results["checks"] += 1
            from app.services.ai_cache import AICacheManager
            cache_manager = AICacheManager(enable_redis=False)
            assert cache_manager is not None, "Cache manager not created"
            results["passed"] += 1
            logger.debug("✅ AI Cache Manager created")
        except Exception as e:
            error_msg = f"AI Cache Manager validation failed: {e}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        try:
            # Test Performance Monitor
            results["checks"] += 1
            from app.services.ai_performance import performance_monitor
            assert performance_monitor is not None, "Performance monitor not available"
            results["passed"] += 1
            logger.debug("✅ Performance Monitor available")
        except Exception as e:
            error_msg = f"Performance Monitor validation failed: {e}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        try:
            # Test Resource Manager
            results["checks"] += 1
            from app.services.ai_resource_manager import resource_limiter
            assert resource_limiter is not None, "Resource limiter not available"
            results["passed"] += 1
            logger.debug("✅ Resource Limiter available")
        except Exception as e:
            error_msg = f"Resource Limiter validation failed: {e}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        results["status"] = "completed" if results["errors"] == [] else "failed"
        return results
    
    async def validate_api_endpoints(self) -> Dict[str, Any]:
        """Validate API endpoints are properly configured."""
        results = {"checks": 0, "passed": 0, "errors": []}
        
        try:
            # Test FastAPI app creation
            results["checks"] += 1
            from app.api.main import app
            assert app is not None, "FastAPI app not created"
            results["passed"] += 1
            logger.debug("✅ FastAPI app created")
        except Exception as e:
            error_msg = f"FastAPI app validation failed: {e}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        try:
            # Test AI status endpoint
            results["checks"] += 1
            from fastapi.testclient import TestClient
            client = TestClient(app)
            response = client.get("/api/v1/ai/status")
            assert response.status_code == 200, f"AI status endpoint failed: {response.status_code}"
            results["passed"] += 1
            logger.debug("✅ AI status endpoint working")
        except Exception as e:
            error_msg = f"AI status endpoint validation failed: {e}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        try:
            # Test health endpoint
            results["checks"] += 1
            response = client.get("/health")
            assert response.status_code == 200, f"Health endpoint failed: {response.status_code}"
            results["passed"] += 1
            logger.debug("✅ Health endpoint working")
        except Exception as e:
            error_msg = f"Health endpoint validation failed: {e}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        results["status"] = "completed" if results["errors"] == [] else "failed"
        return results
    
    async def validate_frontend(self) -> Dict[str, Any]:
        """Validate frontend components."""
        results = {"checks": 0, "passed": 0, "errors": []}
        
        # Check if frontend files exist
        frontend_files = [
            "app/frontend/panel/src/components/AIChat.vue",
            "app/frontend/panel/src/views/AIChat.vue",
            "app/frontend/panel/src/views/AIDashboard.vue"
        ]
        
        for file_path in frontend_files:
            results["checks"] += 1
            if Path(file_path).exists():
                results["passed"] += 1
                logger.debug(f"✅ Frontend file exists: {file_path}")
            else:
                error_msg = f"Frontend file missing: {file_path}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
        
        # Check router configuration
        results["checks"] += 1
        router_file = Path("app/frontend/panel/src/router/index.js")
        if router_file.exists():
            router_content = router_file.read_text()
            if "ai-chat" in router_content and "ai-dashboard" in router_content:
                results["passed"] += 1
                logger.debug("✅ Router configured for AI routes")
            else:
                error_msg = "Router missing AI routes configuration"
                results["errors"].append(error_msg)
                logger.error(error_msg)
        else:
            error_msg = "Router file not found"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        results["status"] = "completed" if results["errors"] == [] else "failed"
        return results
    
    async def validate_configuration(self) -> Dict[str, Any]:
        """Validate configuration settings."""
        results = {"checks": 0, "passed": 0, "errors": []}
        
        try:
            # Test configuration loading
            results["checks"] += 1
            from app.core.config import settings
            assert settings is not None, "Settings not loaded"
            results["passed"] += 1
            logger.debug("✅ Configuration loaded")
        except Exception as e:
            error_msg = f"Configuration validation failed: {e}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        try:
            # Test AI Gateway settings
            results["checks"] += 1
            ai_gateway_enabled = getattr(settings, 'ai_gateway_enabled', False)
            assert isinstance(ai_gateway_enabled, bool), "AI Gateway enabled setting not boolean"
            results["passed"] += 1
            logger.debug("✅ AI Gateway settings valid")
        except Exception as e:
            error_msg = f"AI Gateway settings validation failed: {e}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        results["status"] = "completed" if results["errors"] == [] else "failed"
        return results
    
    async def validate_dependencies(self) -> Dict[str, Any]:
        """Validate required dependencies are available."""
        results = {"checks": 0, "passed": 0, "errors": []}
        
        # Required packages
        required_packages = [
            "fastapi",
            "pydantic",
            "asyncio",
            "redis",
            "openai",
            "numpy",
            "pandas"
        ]
        
        for package in required_packages:
            results["checks"] += 1
            try:
                importlib.import_module(package)
                results["passed"] += 1
                logger.debug(f"✅ Package available: {package}")
            except ImportError:
                error_msg = f"Required package not available: {package}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
        
        results["status"] = "completed" if results["errors"] == [] else "failed"
        return results
    
    async def validate_integration(self) -> Dict[str, Any]:
        """Validate component integration."""
        results = {"checks": 0, "passed": 0, "errors": []}
        
        try:
            # Test orchestrator integration
            results["checks"] += 1
            from app.services.ai_orchestrator import AIOrchestrator
            orchestrator = AIOrchestrator()
            orchestrator.initialize()
            
            # Test that all components are integrated
            assert orchestrator.cache_manager is not None, "Cache manager not integrated"
            assert orchestrator.performance_monitor is not None, "Performance monitor not integrated"
            assert orchestrator.resource_limiter is not None, "Resource limiter not integrated"
            
            results["passed"] += 1
            logger.debug("✅ Component integration working")
        except Exception as e:
            error_msg = f"Integration validation failed: {e}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        try:
            # Test API integration
            results["checks"] += 1
            from app.api.main import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            response = client.get("/api/v1/ai/status")
            
            assert response.status_code == 200, "API integration failed"
            data = response.json()
            assert "enabled" in data, "API response missing expected fields"
            
            results["passed"] += 1
            logger.debug("✅ API integration working")
        except Exception as e:
            error_msg = f"API integration validation failed: {e}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        results["status"] = "completed" if results["errors"] == [] else "failed"
        return results
    
    async def validate_performance(self) -> Dict[str, Any]:
        """Validate performance characteristics."""
        results = {"checks": 0, "passed": 0, "errors": []}
        
        try:
            # Test cache performance
            results["checks"] += 1
            from app.services.ai_cache import AICacheManager
            import time
            
            cache_manager = AICacheManager(enable_redis=False)
            
            # Test cache operations speed
            start_time = time.time()
            for i in range(100):
                await cache_manager.set("perf_test", f"test_{i}", {"id": i}, {"data": f"value_{i}"})
            duration = time.time() - start_time
            
            # Should complete 100 operations in less than 1 second
            assert duration < 1.0, f"Cache operations too slow: {duration:.3f}s"
            results["passed"] += 1
            logger.debug("✅ Cache performance acceptable")
        except Exception as e:
            error_msg = f"Performance validation failed: {e}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        try:
            # Test memory usage
            results["checks"] += 1
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Create some objects
            from app.services.ai_orchestrator import AIOrchestrator
            orchestrator = AIOrchestrator()
            orchestrator.initialize()
            
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = current_memory - initial_memory
            
            # Should not use more than 50MB for initialization
            assert memory_increase < 50, f"Memory usage too high: {memory_increase:.2f}MB"
            results["passed"] += 1
            logger.debug("✅ Memory usage acceptable")
        except Exception as e:
            error_msg = f"Memory usage validation failed: {e}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        results["status"] = "completed" if results["errors"] == [] else "failed"
        return results
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate validation summary."""
        total_checks = sum(cat.get("checks", 0) for cat in self.validation_results.values())
        total_passed = sum(cat.get("passed", 0) for cat in self.validation_results.values())
        total_errors = sum(len(cat.get("errors", [])) for cat in self.validation_results.values())
        
        success_rate = (total_passed / total_checks * 100) if total_checks > 0 else 0
        
        return {
            "total_checks": total_checks,
            "passed_checks": total_passed,
            "failed_checks": total_checks - total_passed,
            "total_errors": total_errors,
            "success_rate": success_rate,
            "categories": self.validation_results,
            "timestamp": asyncio.get_event_loop().time()
        }
    
    def _print_results(self):
        """Print validation results."""
        summary = self._generate_summary()
        
        print("\n" + "=" * 60)
        print("AI IMPLEMENTATION VALIDATION RESULTS")
        print("=" * 60)
        print(f"Total Checks: {summary['total_checks']}")
        print(f"Passed: {summary['passed_checks']}")
        print(f"Failed: {summary['failed_checks']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Total Errors: {summary['total_errors']}")
        print("=" * 60)
        
        # Print category results
        for category, results in summary['categories'].items():
            status_icon = "✅" if results.get('status') == 'completed' else "❌"
            print(f"\n{status_icon} {category.upper()}:")
            print(f"  Checks: {results.get('checks', 0)}")
            print(f"  Passed: {results.get('passed', 0)}")
            print(f"  Status: {results.get('status', 'unknown')}")
            
            if results.get('errors'):
                print("  Errors:")
                for error in results['errors']:
                    print(f"    - {error}")
        
        print("\n" + "=" * 60)
        
        # Print overall status
        if summary['success_rate'] >= 95:
            print("🎉 Excellent! Implementation is fully validated.")
        elif summary['success_rate'] >= 90:
            print("✅ Very good! Implementation is mostly validated.")
        elif summary['success_rate'] >= 80:
            print("⚠️  Good! Implementation has minor issues.")
        elif summary['success_rate'] >= 70:
            print("⚠️  Warning! Implementation has some issues.")
        else:
            print("❌ Critical! Implementation has major issues.")


async def main():
    """Main function to run validation."""
    validator = AIImplementationValidator()
    
    try:
        results = await validator.validate_all()
        
        # Save results to file
        with open("ai_validation_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Validation results saved to: ai_validation_results.json")
        
        # Exit with appropriate code
        if results['success_rate'] >= 90:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure
            
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        print(f"❌ Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
