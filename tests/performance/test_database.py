"""
Database performance tests
"""

import pytest
import time
import statistics
from sqlalchemy import text
from app.db.database import engine


class TestDatabasePerformance:
    """Database performance test suite"""

    def test_simple_query_performance(self, benchmark):
        """Test basic database query performance."""
        def simple_query():
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as test"))
                return result.fetchone()[0]
        
        result = benchmark(simple_query)
        assert result == 1

    def test_connection_pool_performance(self, benchmark):
        """Test database connection pool performance."""
        def connection_test():
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM alembic_version"))
                return result.fetchone()[0]
        
        result = benchmark(connection_test)
        assert result >= 0

    def test_concurrent_database_operations(self):
        """Test database performance under concurrent load."""
        import threading
        import queue

        results = queue.Queue()
        errors = queue.Queue()

        def db_operation():
            try:
                start_time = time.time()
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 1 as test"))
                    row = result.fetchone()
                end_time = time.time()
                results.put(end_time - start_time)
            except Exception as e:
                errors.put(e)

        # Create 20 concurrent database operations
        threads = []
        for _ in range(20):
            thread = threading.Thread(target=db_operation)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check for errors
        assert errors.empty(), f"Database operations failed: {list(errors.queue)}"

        # Analyze performance
        response_times = list(results.queue)
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)

        # Database operations should be fast
        assert avg_response_time < 0.1  # Average < 100ms
        assert max_response_time < 0.5  # Max < 500ms

    def test_transaction_performance(self, benchmark):
        """Test database transaction performance."""
        def transaction_test():
            with engine.begin() as conn:
                # Simple transaction
                conn.execute(text("SELECT 1"))
                conn.execute(text("SELECT 2"))
                conn.execute(text("SELECT 3"))
        
        benchmark(transaction_test)

    def test_bulk_operations_performance(self, benchmark):
        """Test bulk database operations performance."""
        def bulk_test():
            with engine.begin() as conn:
                # Simulate bulk insert (without actually inserting)
                for i in range(100):
                    conn.execute(text("SELECT :val"), {"val": i})
        
        benchmark(bulk_test)

    def test_query_complexity_performance(self):
        """Test performance of different query complexities."""
        queries = [
            ("Simple SELECT", "SELECT 1"),
            ("Count query", "SELECT COUNT(*) FROM alembic_version"),
            ("Complex query", "SELECT * FROM alembic_version WHERE version_num IS NOT NULL"),
        ]

        results = {}
        for name, query in queries:
            start_time = time.time()
            with engine.connect() as conn:
                result = conn.execute(text(query))
                result.fetchall()  # Consume all results
            end_time = time.time()
            results[name] = end_time - start_time

        # All queries should complete within reasonable time
        for name, response_time in results.items():
            assert response_time < 1.0, f"{name} took too long: {response_time}s"

    def test_connection_leak_detection(self):
        """Test for database connection leaks."""
        import gc
        import weakref

        # Get initial connection count (approximate)
        if not hasattr(engine.pool, "_checked_in_connections"):
            pytest.skip("Connection pool does not expose _checked_in_connections")

        initial_connections = len(engine.pool._checked_in_connections)

        # Create and close many connections
        for _ in range(100):
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

        # Force garbage collection
        gc.collect()

        # Check final connection count
        final_connections = len(engine.pool._checked_in_connections)

        # Connection count should not increase significantly
        connection_increase = final_connections - initial_connections
        assert connection_increase < 10, f"Potential connection leak: {connection_increase} extra connections"
