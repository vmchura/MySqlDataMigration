#!/bin/bash

# MySQL Migration Runner Script
# This script sets up the environment and runs the Python migration orchestrator

set -e  # Exit on any error

echo "🚀 MySQL Migration Orchestrator"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is required but not installed."
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt

# Set default environment variables if not set
export STAGING_DB_USER=${STAGING_DB_USER:-root}
export STAGING_DB_PASSWORD=${STAGING_DB_PASSWORD:-password}
export PRODUCT_DB_USER=${PRODUCT_DB_USER:-root}
export PRODUCT_DB_PASSWORD=${PRODUCT_DB_PASSWORD:-password}

print_status "Environment variables set:"
echo "  STAGING_DB_USER: $STAGING_DB_USER"
echo "  STAGING_DB_PASSWORD: [HIDDEN]"
echo "  PRODUCT_DB_USER: $PRODUCT_DB_USER"
echo "  PRODUCT_DB_PASSWORD: [HIDDEN]"

# Check if configuration file exists
if [ ! -f "migration_config.yaml" ]; then
    print_error "migration_config.yaml not found!"
    exit 1
fi

# Check if dump file exists
DUMP_FILE=$(python3 -c "import yaml; print(yaml.safe_load(open('migration_config.yaml'))['connections']['staging']['dump_file'])")
if [ ! -f "$DUMP_FILE" ]; then
    print_warning "Dump file not found: $DUMP_FILE"
    print_warning "Make sure your MySQL dump is available at the specified location"
fi

# Run the migration
print_status "Starting migration process..."
echo "============================================"

if python3 orchestrator.py; then
    print_success "Migration completed successfully! 🎉"
    echo ""
    echo "Check migration.log for detailed logs"
    exit 0
else
    print_error "Migration failed! ❌"
    echo ""
    echo "Check migration.log for error details"
    exit 1
fi
