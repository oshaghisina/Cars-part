#!/usr/bin/env python3
"""
CI Guardrails for Parts & Inventory Integration
==============================================

This script runs in CI to prevent regressions in the parts & inventory system.
It checks for:
- API endpoint availability
- Response structure compliance
- Database schema integrity
- Frontend build validation

Usage:
    python scripts/ci_guardrails_parts.py [--fail-fast]

Exit Codes:
    0: All checks passed
    1: One or more checks failed
    2: Configuration error
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Add project root to Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

class CIGuardrails:
    def __init__(self, fail_fast: bool = False):
        self.fail_fast = fail_fast
        self.errors = []
        self.warnings = []
        self.session = self._create_session()
    
    def _create_session(self):
        """Create HTTP session with retry strategy."""
        session = requests.Session()
        retry_strategy = Retry(
            total=2,  # Reduced for CI speed
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def error(self, message: str):
        """Add an error and optionally fail fast."""
        self.errors.append(message)
        print(f"❌ ERROR: {message}")
        if self.fail_fast:
            self._exit_with_summary()
    
    def warning(self, message: str):
        """Add a warning."""
        self.warnings.append(message)
        print(f"⚠️  WARNING: {message}")
    
    def success(self, message: str):
        """Log a success."""
        print(f"✅ {message}")
    
    def _exit_with_summary(self):
        """Print summary and exit."""
        self._print_summary()
        sys.exit(1 if self.errors else 0)
    
    def _print_summary(self):
        """Print final summary."""
        print(f"\n{'='*60}")
        print(f"CI Guardrails Summary")
        print(f"{'='*60}")
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")
        
        if self.errors:
            print(f"\nErrors:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print(f"\nWarnings:")
            for warning in self.warnings:
                print(f"  - {warning}")
    
    def check_api_endpoints(self):
        """Check that required API endpoints are available."""
        print(f"\n🔍 Checking API endpoints...")
        
        # Test endpoints that should be available
        endpoints = [
            ("/api/v1/parts/", "GET", "List Parts"),
            ("/api/v1/parts/categories/", "GET", "List Categories"),
            ("/api/v1/admin/parts/", "POST", "Create Part (Admin)"),
        ]
        
        for endpoint, method, name in endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"http://localhost:8001{endpoint}", timeout=5)
                elif method == "POST":
                    response = self.session.post(f"http://localhost:8001{endpoint}", 
                                               json={}, timeout=5)
                
                # We expect 200 for GET, 422/401 for POST (validation/unauthorized)
                if response.status_code in [200, 401, 422]:
                    self.success(f"Endpoint {name} is available")
                else:
                    self.error(f"Endpoint {name} returned unexpected status {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.error(f"Endpoint {name} is not accessible: {e}")
    
    def check_response_structure(self):
        """Check API response structure includes required fields."""
        print(f"\n🔍 Checking API response structure...")
        
        try:
            response = self.session.get("http://localhost:8001/api/v1/parts/", timeout=5)
            if response.status_code != 200:
                self.error(f"Parts API returned status {response.status_code}")
                return
            
            parts = response.json()
            if not isinstance(parts, list):
                self.error("Parts API should return a list")
                return
            
            if not parts:
                self.warning("No parts found in database")
                return
            
            # Check first part structure
            part = parts[0]
            required_fields = ['id', 'part_name', 'brand_oem', 'vehicle_make', 'vehicle_model']
            missing_fields = [field for field in required_fields if field not in part]
            
            if missing_fields:
                self.error(f"Parts missing required fields: {missing_fields}")
            else:
                self.success("Parts have required fields")
            
            # Check for price and stock data (optional but recommended)
            has_price = 'price' in part
            has_stock = 'stock' in part
            
            if has_price and has_stock:
                self.success("Parts include price and stock data")
            elif has_price or has_stock:
                self.warning("Parts have partial price/stock data")
            else:
                self.warning("Parts missing price and stock data")
                
        except requests.exceptions.RequestException as e:
            self.error(f"Failed to check response structure: {e}")
        except json.JSONDecodeError as e:
            self.error(f"Invalid JSON response: {e}")
    
    def check_database_schema(self):
        """Check database schema integrity."""
        print(f"\n🔍 Checking database schema...")
        
        try:
            from sqlalchemy import inspect
            from app.db.database import engine
            
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            # Check required tables exist
            required_tables = ['parts', 'part_categories']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                self.error(f"Missing required tables: {missing_tables}")
            else:
                self.success("Required tables exist")
            
            # Check new tables exist (optional)
            new_tables = ['stock_levels', 'prices_new']
            missing_new_tables = [table for table in new_tables if table not in tables]
            
            if missing_new_tables:
                self.warning(f"Missing new tables: {missing_new_tables}")
            else:
                self.success("New pricing/stock tables exist")
                
        except Exception as e:
            self.error(f"Failed to check database schema: {e}")
    
    def check_frontend_builds(self):
        """Check frontend build artifacts."""
        print(f"\n🔍 Checking frontend builds...")
        
        # Check web portal build
        web_dist = project_root / "app" / "frontend" / "web" / "dist"
        if web_dist.exists():
            self.success("Web portal build exists")
        else:
            self.error("Web portal build missing")
        
        # Check admin panel build
        admin_dist = project_root / "app" / "frontend" / "panel" / "dist"
        if admin_dist.exists():
            self.success("Admin panel build exists")
        else:
            self.error("Admin panel build missing")
    
    def check_hardcoded_urls(self):
        """Check for hardcoded localhost URLs in built frontend."""
        print(f"\n🔍 Checking for hardcoded URLs...")
        
        # Check web portal dist
        web_dist = project_root / "app" / "frontend" / "web" / "dist"
        if web_dist.exists():
            hardcoded_found = False
            for js_file in web_dist.rglob("*.js"):
                try:
                    content = js_file.read_text(encoding='utf-8')
                    if 'localhost:8001' in content:
                        self.error(f"Hardcoded localhost URL found in {js_file.relative_to(web_dist)}")
                        hardcoded_found = True
                except Exception:
                    continue
            
            if not hardcoded_found:
                self.success("No hardcoded localhost URLs in web portal")
        
        # Check admin panel dist
        admin_dist = project_root / "app" / "frontend" / "panel" / "dist"
        if admin_dist.exists():
            hardcoded_found = False
            for js_file in admin_dist.rglob("*.js"):
                try:
                    content = js_file.read_text(encoding='utf-8')
                    if 'localhost:8001' in content:
                        self.error(f"Hardcoded localhost URL found in {js_file.relative_to(admin_dist)}")
                        hardcoded_found = True
                except Exception:
                    continue
            
            if not hardcoded_found:
                self.success("No hardcoded localhost URLs in admin panel")
    
    def check_environment_config(self):
        """Check environment configuration files."""
        print(f"\n🔍 Checking environment configuration...")
        
        # Check for production config files
        prod_configs = [
            project_root / "app" / "frontend" / "panel" / "config.production.js",
        ]
        
        for config_file in prod_configs:
            if config_file.exists():
                self.success(f"Production config exists: {config_file.name}")
            else:
                self.warning(f"Production config missing: {config_file.name}")
    
    def run_all_checks(self):
        """Run all guardrail checks."""
        print(f"🚀 Starting CI Guardrails for Parts & Inventory Integration")
        print(f"{'='*60}")
        
        try:
            self.check_api_endpoints()
            self.check_response_structure()
            self.check_database_schema()
            self.check_frontend_builds()
            self.check_hardcoded_urls()
            self.check_environment_config()
            
        except KeyboardInterrupt:
            print(f"\n⚠️  Checks interrupted by user")
            sys.exit(1)
        except Exception as e:
            self.error(f"Unexpected error during checks: {e}")
        
        # Final summary
        self._print_summary()
        sys.exit(1 if self.errors else 0)

def main():
    parser = argparse.ArgumentParser(description="CI Guardrails for Parts & Inventory Integration")
    parser.add_argument("--fail-fast", action="store_true", 
                       help="Stop on first error")
    args = parser.parse_args()
    
    guardrails = CIGuardrails(fail_fast=args.fail_fast)
    guardrails.run_all_checks()

if __name__ == "__main__":
    main()
