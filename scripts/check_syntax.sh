#!/bin/bash
# Syntax check script for CI/pre-commit
# Checks all Python files for syntax errors before deployment

set -e

cd "$(dirname "$0")/.."

echo "Checking Python syntax in apps/api/app directory..."
python -m compileall apps/api/app

echo "✓ All Python files have valid syntax"

# Optional: also check if app.main can be imported
echo "Checking if app.main can be imported..."
cd apps/api
# Use explicit test database URI to avoid accidental production connections
MONGODB_URI="${MONGODB_URI:-mongodb://localhost:27017/test_syntax_check}" python -c "import app.main; print('✓ app.main imported successfully')"

echo "All syntax checks passed!"
