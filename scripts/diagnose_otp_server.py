#!/usr/bin/env python3
"""
Diagnostic tool for OTP issues on the server.

What it does:
- Prints runtime config (env, DB URL, cwd)
- Inspects DB tables and highlights missing OTP tables
- Optionally creates missing OTP tables with --fix
- Smoke-tests RateLimit query to confirm the table works

Usage:
  python scripts/diagnose_otp_server.py           # read-only diagnostics
  python scripts/diagnose_otp_server.py --fix     # also create missing OTP tables
"""

import argparse
import os
import sys
from typing import List

from sqlalchemy import inspect

# Ensure project root is on path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.core.config import settings
from app.db.database import Base, engine, get_db


def print_header(title: str) -> None:
    print("\n" + title)
    print("=" * len(title))


def ensure_models_imported() -> None:
    """Import model modules so their tables register with Base.metadata."""
    # OTP models
    from app.models.otp_models import OTPCode, PhoneVerification, RateLimit  # noqa: F401

    # Related models used by the app (harmless to import; ensures metadata is complete)
    try:
        from app.db.models import User  # noqa: F401
    except Exception:
        pass

    try:
        from app.models.sms_models import SMSLog, SMSTemplate, StockAlert  # noqa: F401
    except Exception:
        pass

    try:
        from app.models.telegram_models import (  # noqa: F401
            TelegramBotSession,
            TelegramDeepLink,
            TelegramLinkToken,
            TelegramUser,
        )
    except Exception:
        pass


def list_tables() -> List[str]:
    inspector = inspect(engine)
    return sorted(inspector.get_table_names())


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose OTP server state")
    parser.add_argument("--fix", action="store_true", help="Create missing OTP tables if needed")
    args = parser.parse_args()

    print_header("Runtime Configuration")
    print(f"CWD: {os.getcwd()}")
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"APP_ENV: {settings.app_env}")
    print(f"DEBUG: {settings.debug}")
    print(f"DATABASE_URL: {settings.database_url}")

    print_header("DB Tables")
    ensure_models_imported()
    before_tables = list_tables()
    print(f"Found {len(before_tables)} tables")
    print(", ".join(before_tables) if before_tables else "(no tables)")

    critical = ["otp_codes", "rate_limits", "phone_verifications"]
    missing = [t for t in critical if t not in before_tables]
    if missing:
        print(f"\nMissing critical tables: {missing}")
        if args.fix:
            print("Creating missing tables via Base.metadata.create_all() ...")
            try:
                Base.metadata.create_all(bind=engine)
                after_tables = list_tables()
                print("Done. Tables now:")
                print(", ".join(after_tables))
                still_missing = [t for t in critical if t not in after_tables]
                if still_missing:
                    print(f"WARNING: Still missing: {still_missing}")
                else:
                    print("All critical tables present.")
            except Exception as e:
                print(f"ERROR: Failed to create tables: {e}")
                return 2
        else:
            print("(Run with --fix to create them)")
    else:
        print("All critical OTP tables exist.")

    print_header("RateLimit Smoke Test")
    try:
        from app.services.otp_service import OTPService

        db = next(get_db())
        svc = OTPService(db)
        ok, msg = svc.check_rate_limit("127.0.0.1", "ip", "otp_request")
        print(f"check_rate_limit returned: ok={ok}, msg='{msg}'")
        db.close()
    except Exception as e:
        print(f"ERROR during rate-limit test: {e}")
        return 3

    print("\nDiagnostics complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

