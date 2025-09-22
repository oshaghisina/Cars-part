# AI Gateway Testing Suite

This directory contains comprehensive testing tools and validation scripts for the AI Gateway implementation.

## Overview

The AI Gateway testing suite provides:

- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **Performance Tests**: Load and performance testing
- **Validation Tests**: Correctness and accuracy testing
- **API Tests**: Endpoint functionality testing
- **End-to-End Tests**: Complete workflow testing

## Test Structure

```
tests/ai/
├── conftest.py              # Pytest configuration and fixtures
├── test_ai_framework.py     # Comprehensive test framework
├── README.md               # This documentation
└── reports/                # Generated test reports
    ├── ai_test_report.json
    ├── ai_test_report.html
    └── ai_test_report.md
```

## Running Tests

### Quick Test Run

```bash
# Run all tests
python run_ai_tests.py

# Run specific categories
python run_ai_tests.py --categories unit integration

# Run quick tests only
python run_ai_tests.py --quick
```

### Using Pytest

```bash
# Run all AI tests
pytest tests/ai/ -v

# Run specific test categories
pytest tests/ai/ -m unit -v
pytest tests/ai/ -m performance -v

# Run with coverage
pytest tests/ai/ --cov=app.services.ai --cov-report=html
```

### Validation Script

```bash
# Validate complete implementation
python validate_ai_implementation.py
```

## Test Categories

### 1. Unit Tests (`unit`)

Tests individual AI components in isolation:

- **Cache Manager**: Basic operations, data integrity
- **Performance Metrics**: Calculation accuracy, data recording
- **Resource Limiter**: Request slot management, limits enforcement
- **Query Optimizer**: Query processing, optimization rules
- **AI Response**: Response creation and validation
- **Provider Status**: Status enum functionality

### 2. Integration Tests (`integration`)

Tests component interactions:

- **Orchestrator Integration**: Component initialization and coordination
- **Cache Integration**: Cache operations with orchestrator
- **Performance Monitoring**: Metrics collection and reporting
- **Resource Management**: Resource allocation and cleanup
- **AI Provider Integration**: Provider status and capabilities

### 3. Performance Tests (`performance`)

Tests performance characteristics:

- **Cache Performance**: Operations per second, response times
- **Query Optimization**: Processing speed, optimization effectiveness
- **Concurrent Handling**: Multi-request processing, resource management
- **Memory Usage**: Memory consumption patterns, cleanup
- **Response Time Benchmarks**: Operation timing, performance baselines

### 4. Validation Tests (`validation`)

Tests correctness and accuracy:

- **AI Response Validation**: Response format and content validation
- **Cache Data Integrity**: Data consistency and serialization
- **Performance Metrics Accuracy**: Calculation correctness
- **Resource Limits Enforcement**: Limit compliance and behavior
- **Error Handling Validation**: Error recovery and graceful degradation

### 5. API Tests (`api`)

Tests API endpoint functionality:

- **AI Status Endpoint**: Status information retrieval
- **AI Chat Endpoint**: Chat functionality and authentication
- **AI Dashboard Endpoint**: Dashboard data provision
- **Health Check Endpoint**: System health monitoring

### 6. End-to-End Tests (`e2e`)

Tests complete workflows:

- **Complete Search Workflow**: Full search process from query to results
- **AI Chat Workflow**: Complete chat interaction flow
- **Performance Optimization Workflow**: Optimization process execution
- **Error Recovery Workflow**: Error handling and recovery processes

## Test Configuration

### Environment Variables

```bash
# Required for testing
export AI_GATEWAY_ENABLED=true
export AI_GATEWAY_EXPERIMENTAL=false
export OPENAI_API_KEY=TEST_API_KEY
export DATABASE_URL=sqlite:///./data/test.db
export REDIS_URL=redis://localhost:6379/0
```

### Test Fixtures

The test suite provides several fixtures:

- `mock_ai_provider`: Mock AI provider for testing
- `mock_openai_provider`: Mock OpenAI provider
- `sample_parts_data`: Sample car parts data
- `sample_queries`: Test queries in multiple languages
- `test_user`: Mock user for authentication
- `clean_cache`: Cache cleanup before/after tests
- `reset_performance_metrics`: Metrics reset functionality

## Test Reports

### JSON Report

```json
{
  "total_tests": 150,
  "passed_tests": 145,
  "failed_tests": 5,
  "success_rate": 96.7,
  "total_time": 45.2,
  "categories": {
    "unit_tests": {
      "status": "completed",
      "total_tests": 25,
      "passed_tests": 25
    }
  }
}
```

### HTML Report

Generates a comprehensive HTML report with:
- Test summary and statistics
- Category-wise results
- Individual test details
- Performance metrics
- Error details and stack traces

### Markdown Report

Creates a markdown report suitable for:
- GitHub/GitLab integration
- Documentation
- CI/CD pipeline reports

## Performance Benchmarks

### Expected Performance

| Test Category | Target | Current |
|---------------|--------|---------|
| Cache Operations | >1000 ops/sec | ~2000 ops/sec |
| Query Optimization | >1000 queries/sec | ~1500 queries/sec |
| Concurrent Requests | >10 requests/sec | ~15 requests/sec |
| Memory Usage | <50MB init | ~30MB init |
| Response Time | <1.0s average | ~0.5s average |

### Performance Monitoring

The test suite monitors:
- Response times for all operations
- Memory usage patterns
- CPU utilization
- Cache hit rates
- Error rates and types

## Continuous Integration

### GitHub Actions

```yaml
name: AI Gateway Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run AI tests
        run: python run_ai_tests.py
      - name: Upload test reports
        uses: actions/upload-artifact@v2
        with:
          name: test-reports
          path: ai_test_report.*
```

### Pre-commit Hooks

```yaml
repos:
  - repo: local
    hooks:
      - id: ai-tests
        name: AI Gateway Tests
        entry: python run_ai_tests.py --quick
        language: system
        pass_filenames: false
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path configuration
   - Verify module structure

2. **Test Failures**
   - Check environment variables
   - Verify database connectivity
   - Review error logs

3. **Performance Issues**
   - Monitor system resources
   - Check for memory leaks
   - Review concurrent request handling

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python run_ai_tests.py --verbose

# Run specific test with debugging
pytest tests/ai/test_ai_framework.py::test_cache_performance -v -s
```

## Contributing

### Adding New Tests

1. Create test function following naming convention
2. Add appropriate markers (`@pytest.mark.unit`, etc.)
3. Include proper error handling and assertions
4. Update documentation

### Test Guidelines

- Use descriptive test names
- Include setup and teardown
- Test both success and failure cases
- Include performance assertions where applicable
- Document test purpose and expected behavior

## Maintenance

### Regular Tasks

- Update test data and fixtures
- Review and update performance benchmarks
- Clean up old test reports
- Update documentation

### Monitoring

- Track test execution times
- Monitor test success rates
- Review error patterns
- Update test coverage

## Support

For issues with the test suite:

1. Check the logs in `ai_tests.log`
2. Review test reports for detailed error information
3. Run validation script for implementation issues
4. Check system requirements and dependencies

## License

This testing suite is part of the China Car Parts AI Gateway project and follows the same license terms.
