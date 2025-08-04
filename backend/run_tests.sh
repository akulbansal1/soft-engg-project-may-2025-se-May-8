#!/bin/bash

# Test runner script for the FastAPI backend
# This script runs different types of tests and generates reports

set -e  # Exit on any error

echo "🧪 FastAPI Backend Test Suite"
echo "================================"


# Create and activate virtual environment if it doesn't exist (cross-platform)
if [ ! -d ".venv" ]; then
    echo "🆕 Creating virtual environment..."
    python3 -m venv .venv || python -m venv .venv
fi


# Cross-platform venv activation
if [ -f ".venv/bin/activate" ]; then
    # Unix/macOS
    source .venv/bin/activate
    PYTHON_EXE=".venv/bin/python"
    PIP_EXE=".venv/bin/pip"
elif [ -f ".venv/Scripts/activate" ]; then
    # Windows
    .venv/Scripts/activate
    PYTHON_EXE=".venv/Scripts/python.exe"
    PIP_EXE=".venv/Scripts/pip.exe"
else
    echo "❌ Could not find a valid virtual environment activation script."
    exit 1
fi

echo "📦 Virtual environment activated successfully"

# Install test dependencies
echo "📋 Installing test dependencies..."
$PIP_EXE install -q -r requirements.txt

# Create test results directory
mkdir -p test-results

# Run test categories
echo ""
echo "📊 Running All Tests with Coverage..."
$PYTHON_EXE -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing --cov-report=xml

echo ""
echo "✅ Test Summary:"
echo "- Health Check Tests: Server status and basic functionality"
echo "- Database Tests: Database connectivity and model validation"
echo "- Configuration Tests: Settings and environment validation"
echo "- API Tests: Endpoint behavior and request handling"
echo ""
echo "📄 Coverage report generated in htmlcov/index.html"
echo "🎉 All tests completed!"
