#!/bin/bash

# Test runner script for Self-Growth backend
# Usage: ./run_tests.sh [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Self-Growth Backend Test Suite${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Warning: Virtual environment not activated${NC}"
    echo -e "${YELLOW}Activating .venv...${NC}"
    source .venv/bin/activate || {
        echo -e "${RED}Failed to activate virtual environment${NC}"
        echo -e "${YELLOW}Please run: python -m venv .venv && source .venv/bin/activate${NC}"
        exit 1
    }
fi

# Install test dependencies if needed
echo -e "${YELLOW}Checking test dependencies...${NC}"
pip install -q pytest pytest-cov pytest-mock 2>/dev/null || true

# Parse command line arguments
TEST_PATH="tests/"
COVERAGE=false
VERBOSE=false
MARKERS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -m|--markers)
            MARKERS="-m $2"
            shift 2
            ;;
        -k|--keyword)
            KEYWORD="-k $2"
            shift 2
            ;;
        -f|--file)
            TEST_PATH="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: ./run_tests.sh [options]"
            echo ""
            echo "Options:"
            echo "  -c, --coverage       Run tests with coverage report"
            echo "  -v, --verbose        Verbose output"
            echo "  -m, --markers MARK   Run tests with specific marker"
            echo "  -k, --keyword EXPR   Run tests matching keyword expression"
            echo "  -f, --file PATH      Run specific test file or directory"
            echo "  -h, --help           Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./run_tests.sh                          # Run all tests"
            echo "  ./run_tests.sh -c                       # Run with coverage"
            echo "  ./run_tests.sh -m unit                  # Run only unit tests"
            echo "  ./run_tests.sh -k test_create           # Run tests matching 'test_create'"
            echo "  ./run_tests.sh -f tests/test_models.py  # Run specific file"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Build pytest command
PYTEST_CMD="python -m pytest $TEST_PATH"

if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -vv"
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=src --cov-report=term-missing --cov-report=html"
fi

if [ -n "$MARKERS" ]; then
    PYTEST_CMD="$PYTEST_CMD $MARKERS"
fi

if [ -n "$KEYWORD" ]; then
    PYTEST_CMD="$PYTEST_CMD $KEYWORD"
fi

# Run tests
echo -e "${YELLOW}Running tests...${NC}"
echo -e "${YELLOW}Command: $PYTEST_CMD${NC}"
echo ""

if $PYTEST_CMD; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo -e "${GREEN}========================================${NC}"
    
    if [ "$COVERAGE" = true ]; then
        echo ""
        echo -e "${YELLOW}Coverage report generated in htmlcov/index.html${NC}"
    fi
    
    exit 0
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}✗ Some tests failed${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi
