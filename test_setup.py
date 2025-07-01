#!/usr/bin/env python3
"""
Test setup script to validate the migration environment
"""

import os
import sys
import yaml
from pathlib import Path

def test_configuration():
    """Test configuration file"""
    print("🔍 Testing configuration...")
    
    if not os.path.exists('migration_config.yaml'):
        print("❌ migration_config.yaml not found")
        return False
    
    try:
        with open('migration_config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Check required sections
        required_sections = ['connections', 'migrations']
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing required section: {section}")
                return False
        
        print("✅ Configuration file valid")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_dump_file():
    """Test if dump file exists"""
    print("🔍 Testing dump file...")
    
    try:
        with open('migration_config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        dump_file = config['connections']['staging']['dump_file']
        
        if os.path.exists(dump_file):
            file_size = os.path.getsize(dump_file) / 1024  # KB
            print(f"✅ Dump file found: {dump_file} ({file_size:.1f} KB)")
            return True
        else:
            print(f"⚠️ Dump file not found: {dump_file}")
            print("   This is expected if you haven't created the dump yet")
            return True  # Not a critical error for setup test
    except Exception as e:
        print(f"❌ Dump file test error: {e}")
        return False

def test_migration_scripts():
    """Test migration scripts"""
    print("🔍 Testing migration scripts...")
    
    migrations_dir = Path('migrations')
    if not migrations_dir.exists():
        print("❌ migrations directory not found")
        return False
    
    # Check for products transformation script
    products_script = migrations_dir / 'products_transformation.py'
    if not products_script.exists():
        print("❌ products_transformation.py not found")
        return False
    
    # Try to import the transformation function
    try:
        sys.path.append(str(migrations_dir.parent))
        from migrations.products_transformation import transform_products_data
        print("✅ Migration scripts importable")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_environment_variables():
    """Test environment variable setup"""
    print("🔍 Testing environment variables...")
    
    required_vars = [
        'STAGING_DB_USER',
        'STAGING_DB_PASSWORD', 
        'PRODUCT_DB_USER',
        'PRODUCT_DB_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
        print("   These will be set to defaults during migration")
    else:
        print("✅ All environment variables set")
    
    return True

def test_dependencies():
    """Test Python dependencies"""
    print("🔍 Testing dependencies...")
    
    required_packages = [
        'yaml',
        'polars', 
        'pymysql',
        'sqlalchemy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("   Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages available")
        return True

def main():
    """Run all tests"""
    print("MySQL Migration Setup Test")
    print("=" * 40)
    
    tests = [
        test_configuration,
        test_dump_file,
        test_migration_scripts,
        test_environment_variables,
        test_dependencies
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)
            print()
    
    # Summary
    print("Test Summary")
    print("=" * 20)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All {total} tests passed!")
        print("🚀 Ready to run migration!")
    else:
        print(f"⚠️ {passed}/{total} tests passed")
        print("🔧 Fix the issues above before running migration")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
