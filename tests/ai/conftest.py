"""
AI Test Configuration

This module provides pytest configuration and fixtures for AI testing.
"""

import asyncio
import os
import sys
from pathlib import Path

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Add the project root to Python path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

# Set test environment variables
os.environ['AI_GATEWAY_ENABLED'] = 'true'
os.environ['AI_GATEWAY_EXPERIMENTAL'] = 'false'
os.environ['OPENAI_API_KEY'] = 'TEST_API_KEY'
os.environ['DATABASE_URL'] = 'sqlite:///./data/test.db'
os.environ['REDIS_URL'] = 'redis://localhost:6379/0'


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mock_ai_provider():
    """Mock AI provider for testing."""
    provider = MagicMock()
    provider.name = "test_provider"
    provider.is_available.return_value = True
    provider.is_healthy.return_value = True
    provider.get_status.return_value = "healthy"
    provider.get_capabilities.return_value = ["semantic_search", "intelligent_search"]
    provider.estimate_cost.return_value = 0.01
    
    # Mock async methods
    provider.execute_task = AsyncMock(return_value={
        "content": [{"test": "data"}],
        "metadata": {"test": "metadata"},
        "provider": "test_provider",
        "task_type": "semantic_search",
        "cost": 0.01,
        "tokens_used": 100
    })
    
    return provider


@pytest.fixture
async def mock_openai_provider():
    """Mock OpenAI provider for testing."""
    provider = MagicMock()
    provider.name = "openai"
    provider.is_available.return_value = True
    provider.is_healthy.return_value = True
    provider.get_status.return_value = "healthy"
    provider.get_capabilities.return_value = ["semantic_search", "intelligent_search", "query_analysis"]
    provider.estimate_cost.return_value = 0.02
    
    # Mock async methods
    provider.execute_task = AsyncMock(return_value={
        "content": [{"test": "openai_data"}],
        "metadata": {"test": "openai_metadata"},
        "provider": "openai",
        "task_type": "semantic_search",
        "cost": 0.02,
        "tokens_used": 150
    })
    
    return provider


@pytest.fixture
def sample_parts_data():
    """Sample parts data for testing."""
    return [
        {
            "id": 1,
            "part_name": "لنت ترمز جلو",
            "brand_oem": "Chery",
            "vehicle_make": "Chery",
            "vehicle_model": "Tiggo 8",
            "category": "Brake System",
            "price": 100,
            "description": "High-quality front brake pads for Chery Tiggo 8"
        },
        {
            "id": 2,
            "part_name": "فیلتر روغن",
            "brand_oem": "JAC",
            "vehicle_make": "JAC",
            "vehicle_model": "J4",
            "category": "Engine Parts",
            "price": 50,
            "description": "Original oil filter for JAC J4"
        },
        {
            "id": 3,
            "part_name": "brake disc",
            "brand_oem": "Brilliance",
            "vehicle_make": "Brilliance",
            "vehicle_model": "V5",
            "category": "Brake System",
            "price": 150,
            "description": "Front brake disc for Brilliance V5"
        },
        {
            "id": 4,
            "part_name": "شمع موتور",
            "brand_oem": "Denso",
            "vehicle_make": "IKCO",
            "vehicle_model": "Samand",
            "category": "Engine Parts",
            "price": 25,
            "description": "Denso spark plug for IKCO Samand"
        },
        {
            "id": 5,
            "part_name": "air filter",
            "brand_oem": "Mahle",
            "vehicle_make": "Saipa",
            "vehicle_model": "Tiba",
            "category": "Air Intake",
            "price": 30,
            "description": "Mahle air filter for Saipa Tiba"
        }
    ]


@pytest.fixture
def sample_queries():
    """Sample queries for testing."""
    return {
        "persian": [
            "لنت ترمز چری تیگو 8",
            "فیلتر روغن JAC J4",
            "شمع موتور IKCO Samand",
            "فیلتر هوا Saipa Tiba"
        ],
        "english": [
            "brake pads for Chery Tiggo 8",
            "oil filter for JAC J4",
            "spark plug for IKCO Samand",
            "air filter for Saipa Tiba"
        ],
        "mixed": [
            "لنت ترمز brake pads Chery Tiggo 8",
            "فیلتر روغن oil filter JAC J4"
        ]
    }


@pytest.fixture
def test_user():
    """Test user for authentication."""
    return {
        "id": "test_user_123",
        "username": "test_user",
        "email": "test@example.com",
        "role": "admin",
        "is_active": True
    }


@pytest.fixture
def mock_auth_token():
    """Mock authentication token."""
    return "mock_jwt_token_12345"


@pytest.fixture
def ai_test_config():
    """AI test configuration."""
    return {
        "cache_ttl": 60,
        "max_concurrent_requests": 10,
        "performance_test_iterations": 100,
        "concurrent_test_requests": 50,
        "memory_test_entries": 1000,
        "benchmark_iterations": 10
    }


@pytest.fixture
async def clean_cache():
    """Clean cache before and after tests."""
    from app.services.ai_cache import cache_manager
    
    # Clean before test
    await cache_manager.clear()
    
    yield
    
    # Clean after test
    await cache_manager.clear()


@pytest.fixture
async def reset_performance_metrics():
    """Reset performance metrics before and after tests."""
    from app.services.ai_performance import performance_monitor
    
    # Reset before test
    performance_monitor.reset_metrics()
    
    yield
    
    # Reset after test
    performance_monitor.reset_metrics()


@pytest.fixture
def mock_redis():
    """Mock Redis connection for testing."""
    with patch('redis.from_url') as mock_redis:
        mock_redis_instance = MagicMock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.get.return_value = None
        mock_redis_instance.setex.return_value = True
        mock_redis_instance.delete.return_value = 1
        mock_redis_instance.keys.return_value = []
        mock_redis.return_value = mock_redis_instance
        yield mock_redis_instance


@pytest.fixture
def mock_database():
    """Mock database connection for testing."""
    with patch('app.db.database.SessionLocal') as mock_db:
        mock_session = MagicMock()
        mock_db.return_value = mock_session
        yield mock_session


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    with patch('openai.AsyncOpenAI') as mock_client:
        mock_instance = MagicMock()
        
        # Mock embeddings
        mock_embeddings = MagicMock()
        mock_embeddings.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_instance.embeddings.create = AsyncMock(return_value=mock_embeddings)
        
        # Mock chat completions
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content="Test response"))]
        mock_instance.chat.completions.create = AsyncMock(return_value=mock_completion)
        
        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_http_client():
    """Mock HTTP client for testing."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock()
        mock_instance.post = AsyncMock()
        mock_client.return_value = mock_instance
        yield mock_instance


# Test markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "api: API tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "ai: AI-specific tests")


# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add markers based on test name patterns
        if "unit" in item.name:
            item.add_marker(pytest.mark.unit)
        elif "integration" in item.name:
            item.add_marker(pytest.mark.integration)
        elif "performance" in item.name:
            item.add_marker(pytest.mark.performance)
        elif "api" in item.name:
            item.add_marker(pytest.mark.api)
        elif "e2e" in item.name or "end_to_end" in item.name:
            item.add_marker(pytest.mark.e2e)
        
        # Add AI marker for all AI tests
        if "ai" in item.name or "test_ai" in item.name:
            item.add_marker(pytest.mark.ai)
        
        # Add slow marker for performance tests
        if "performance" in item.name or "benchmark" in item.name:
            item.add_marker(pytest.mark.slow)


# Test reporting
def pytest_html_report_title(report):
    """Set custom HTML report title."""
    report.title = "AI Gateway Test Report"


def pytest_html_results_table_header(cells):
    """Customize HTML report table header."""
    cells.insert(1, '<th class="sortable" data-column-type="text">Test Category</th>')
    cells.insert(2, '<th class="sortable" data-column-type="text">Duration</th>')


def pytest_html_results_table_row(report, cells):
    """Customize HTML report table rows."""
    # Add test category based on markers
    category = "Unknown"
    if hasattr(report, 'keywords'):
        if 'unit' in str(report.keywords):
            category = "Unit"
        elif 'integration' in str(report.keywords):
            category = "Integration"
        elif 'performance' in str(report.keywords):
            category = "Performance"
        elif 'api' in str(report.keywords):
            category = "API"
        elif 'e2e' in str(report.keywords):
            category = "E2E"
    
    cells.insert(1, f'<td class="col-category">{category}</td>')
    cells.insert(2, f'<td class="col-duration">{report.duration:.3f}s</td>')
