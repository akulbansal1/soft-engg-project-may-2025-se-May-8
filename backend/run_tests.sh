#!/bin/bash

# Test runner script for the FastAPI backend
# This script runs different types of tests and generates reports

set -e  # Exit on any error

echo "🧪 FastAPI Backend Test Suite"
echo "================================"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
fi

# Install test dependencies if not already installed
echo "📋 Checking test dependencies..."
pip install -q pytest pytest-cov pytest-asyncio pytest-timeout httpx

# Create test results directory
mkdir -p test-results

# Run different test categories
echo ""
echo "🏥 Running Health Check Tests..."
pytest tests/test_main.py::TestServerHealth -v

echo ""
echo "🗄️ Running Database Tests..."
pytest tests/test_database.py -v

echo ""
echo "🔧 Running Configuration Tests..."
pytest tests/test_config.py -v

echo ""
echo "🌐 Running API Tests..."
pytest tests/test_api.py -v

echo ""
echo "📊 Running All Tests with Coverage..."
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing --cov-report=xml

echo ""
echo "✅ Test Summary:"
echo "- Health Check Tests: Server status and basic functionality"
echo "- Database Tests: Database connectivity and model validation"
echo "- Configuration Tests: Settings and environment validation"
echo "- API Tests: Endpoint behavior and request handling"
echo ""
echo "📄 Coverage report generated in htmlcov/index.html"
echo "🎉 All tests completed!"
