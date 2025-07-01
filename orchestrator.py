#!/usr/bin/env python3
"""
MySQL Migration Orchestrator
Main orchestration script for managing the migration process from staging to microservices.
"""

import os
import sys
import yaml
import logging
import subprocess
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

# Database connectivity
import pymysql
import polars as pl
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Migration modules
from migrations.products_transformation import transform_products_data, validate_transformation_results

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class MigrationConfig:
    """Configuration data class for migration settings"""
    config_path: str
    data: Dict
    
    @classmethod
    def load(cls, config_path: str = "migration_config.yaml"):
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(config_path=config_path, data=data)
    
    def get_connection_string(self, service_name: str) -> str:
        """Generate connection string for a service"""
        if service_name == "staging":
            conn = self.data['connections']['staging']
            return f"mysql+pymysql://{conn['username']}:{conn['password']}@{conn['host']}:{conn['port']}/{conn['database']}"
        else:
            conn = self.data['connections']['microservices'][service_name]
            return f"mysql+pymysql://{conn['username']}:{conn['password']}@{conn['host']}:{conn['port']}/{conn['database']}"

class DatabaseManager:
    """Handles database operations and connections"""
    
    def __init__(self, config: MigrationConfig):
        self.config = config
        self.engines = {}
    
    def get_engine(self, service_name: str):
        """Get or create SQLAlchemy engine for a service"""
        if service_name not in self.engines:
            conn_str = self.config.get_connection_string(service_name)
            self.engines[service_name] = create_engine(conn_str)
        return self.engines[service_name]
    
    def test_connections(self) -> bool:
        """Test all database connections"""
        logger.info("Testing database connections...")
        
        # Test staging connection
        try:
            engine = self.get_engine("staging")
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("✅ Staging database connection successful")
        except Exception as e:
            logger.error(f"❌ Staging database connection failed: {e}")
            return False
        
        # Test microservice connections
        for service_name in self.config.data['connections']['microservices']:
            try:
                engine = self.get_engine(service_name)
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    logger.info(f"✅ {service_name} database connection successful")
            except Exception as e:
                logger.error(f"❌ {service_name} database connection failed: {e}")
                return False
        
        return True
    
    def restore_staging_dump(self, dump_file_path: str) -> bool:
        """Restore MySQL dump to staging database"""
        logger.info(f"Restoring dump file: {dump_file_path}")
        
        staging_config = self.config.data['connections']['staging']
        
        # Build mysql command
        cmd = [
            'mysql',
            f"--host={staging_config['host']}",
            f"--port={staging_config['port']}",
            f"--user={staging_config['username']}",
            f"--password={staging_config['password']}",
            staging_config['database']
        ]
        
        try:
            with open(dump_file_path, 'r') as dump_file:
                result = subprocess.run(
                    cmd,
                    stdin=dump_file,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )
            
            if result.returncode == 0:
                logger.info("✅ Staging dump restored successfully")
                return True
            else:
                logger.error(f"❌ Dump restore failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Dump restore timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Dump restore error: {e}")
            return False
    
    def load_source_data(self, table_name: str) -> pl.DataFrame:
        """Load data from staging database table"""
        logger.info(f"Loading data from staging table: {table_name}")
        
        engine = self.get_engine("staging")
        query = f"SELECT * FROM {table_name}"
        
        try:
            df = pl.read_database(query, engine)
            logger.info(f"✅ Loaded {len(df)} rows from {table_name}")
            return df
        except Exception as e:
            logger.error(f"❌ Failed to load data from {table_name}: {e}")
            raise
    
    def write_target_data(self, service_name: str, table_name: str, data: pl.DataFrame) -> bool:
        """Write transformed data to target microservice database"""
        logger.info(f"Writing {len(data)} rows to {service_name}.{table_name}")
        
        if len(data) == 0:
            logger.info(f"No data to write for {table_name}")
            return True
        
        engine = self.get_engine(service_name)
        
        try:
            # Convert Polars to Pandas for SQLAlchemy compatibility
            pandas_df = data.to_pandas()
            pandas_df.to_sql(
                table_name,
                engine,
                if_exists='append',
                index=False,
                method='multi'
            )
            logger.info(f"✅ Successfully wrote data to {service_name}.{table_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to write data to {service_name}.{table_name}: {e}")
            return False

class MigrationOrchestrator:
    """Main orchestrator for managing migration process"""
    
    def __init__(self, config_path: str = "migration_config.yaml"):
        self.config = MigrationConfig.load(config_path)
        self.db_manager = DatabaseManager(self.config)
        self.migration_results = {}
    
    def setup_environment_variables(self):
        """Setup required environment variables"""
        logger.info("Setting up environment variables...")
        
        # Set default values if not already set
        env_vars = {
            'STAGING_DB_USER': 'root',
            'STAGING_DB_PASSWORD': 'password',
            'PRODUCT_DB_USER': 'root',
            'PRODUCT_DB_PASSWORD': 'password'
        }
        
        for var, default_value in env_vars.items():
            if not os.getenv(var):
                os.environ[var] = default_value
                logger.info(f"Set {var} to default value")
    
    def phase_1_environment_preparation(self) -> bool:
        """Phase 1: Prepare migration environment"""
        logger.info("🚀 Phase 1: Environment Preparation")
        
        # Setup environment variables
        self.setup_environment_variables()
        
        # Test database connections
        if not self.db_manager.test_connections():
            logger.error("❌ Database connection tests failed")
            return False
        
        # Restore staging dump
        dump_file = self.config.data['connections']['staging'].get('dump_file', 'phase_00/dump-myapp-202506302052.sql')
        if not os.path.exists(dump_file):
            logger.error(f"❌ Dump file not found: {dump_file}")
            return False
        
        if not self.db_manager.restore_staging_dump(dump_file):
            logger.error("❌ Failed to restore staging dump")
            return False
        
        logger.info("✅ Phase 1 completed successfully")
        return True
    
    def phase_2_execute_migrations(self) -> bool:
        """Phase 2: Execute configured migrations"""
        logger.info("🚀 Phase 2: Execute Migrations")
        
        migrations = self.config.data.get('migrations', [])
        
        for migration in migrations:
            migration_id = migration['migration_id']
            logger.info(f"Executing migration: {migration_id}")
            
            if not self.execute_single_migration(migration):
                logger.error(f"❌ Migration {migration_id} failed")
                return False
        
        logger.info("✅ Phase 2 completed successfully")
        return True
    
    def execute_single_migration(self, migration: Dict) -> bool:
        """Execute a single migration configuration"""
        migration_id = migration['migration_id']
        logger.info(f"Processing migration: {migration_id}")
        
        try:
            # Load source data
            source_tables = migration['source']['tables']
            source_data = None
            
            for table_config in source_tables:
                table_name = table_config['name']
                data = self.db_manager.load_source_data(table_name)
                
                if source_data is None:
                    source_data = data
                else:
                    # If multiple source tables, would need to join/combine here
                    source_data = source_data.vstack(data)
            
            # Execute transformation
            if migration['transformation']['type'] == 'custom':
                transformation_results = self.execute_custom_transformation(
                    migration, source_data
                )
            else:
                logger.error(f"❌ Unsupported transformation type: {migration['transformation']['type']}")
                return False
            
            # Validate transformation results
            if not validate_transformation_results(transformation_results, source_data):
                logger.error(f"❌ Transformation validation failed for {migration_id}")
                return False
            
            # Write to target databases
            targets = migration['targets']
            for target in targets:
                database_service = target['database']
                target_table = target['table']
                
                if target_table in transformation_results:
                    target_data = transformation_results[target_table]
                    if not self.db_manager.write_target_data(
                        database_service, target_table, target_data
                    ):
                        return False
                else:
                    logger.warning(f"⚠️ No data found for target table: {target_table}")
            
            # Store results
            self.migration_results[migration_id] = {
                'status': 'success',
                'source_rows': len(source_data),
                'target_tables': {
                    table_name: len(df) for table_name, df in transformation_results.items()
                }
            }
            
            logger.info(f"✅ Migration {migration_id} completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration {migration_id} failed with error: {e}")
            self.migration_results[migration_id] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    def execute_custom_transformation(self, migration: Dict, source_data: pl.DataFrame) -> Dict[str, pl.DataFrame]:
        """Execute custom transformation script"""
        transformation_config = migration['transformation']
        
        # For products transformation, we need to add configuration parameters
        parameters = {
            'variation_patterns': [
                {
                    'regex': r'(\d+x\d+)$',
                    'variation_type': 'dimension'
                },
                {
                    'regex': r'(\d+(?:kg|g|ml|l))$',
                    'variation_type': 'weight_volume'
                }
            ]
        }
        
        # Call the transformation function
        return transform_products_data(source_data, parameters)
    
    def phase_3_validation(self) -> bool:
        """Phase 3: Post-migration validation"""
        logger.info("🚀 Phase 3: Post-Migration Validation")
        
        # Print migration summary
        logger.info("Migration Summary:")
        for migration_id, result in self.migration_results.items():
            if result['status'] == 'success':
                logger.info(f"✅ {migration_id}: {result['source_rows']} source rows")
                for table_name, row_count in result['target_tables'].items():
                    logger.info(f"   -> {table_name}: {row_count} rows")
            else:
                logger.error(f"❌ {migration_id}: {result['error']}")
        
        # Additional validation could be added here
        logger.info("✅ Phase 3 completed successfully")
        return True
    
    def run_full_migration(self) -> bool:
        """Run the complete migration process"""
        logger.info("🎯 Starting Full Migration Process")
        start_time = time.time()
        
        try:
            # Phase 1: Environment Preparation
            if not self.phase_1_environment_preparation():
                return False
            
            # Phase 2: Execute Migrations
            if not self.phase_2_execute_migrations():
                return False
            
            # Phase 3: Validation
            if not self.phase_3_validation():
                return False
            
            elapsed_time = time.time() - start_time
            logger.info(f"🎉 Migration completed successfully in {elapsed_time:.2f} seconds")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed with error: {e}")
            return False
        finally:
            # Cleanup connections
            for engine in self.db_manager.engines.values():
                engine.dispose()

def main():
    """Main entry point"""
    print("MySQL Migration Orchestrator")
    print("=" * 50)
    
    # Create orchestrator
    orchestrator = MigrationOrchestrator()
    
    # Run migration
    success = orchestrator.run_full_migration()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Migration failed. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
