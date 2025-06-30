# MySQL Migration Strategy - Context Prompt

## Project Overview
**Role**: Senior Data Engineer  
**Task**: Plan and execute data migration from MySQL on-premise to MySQL hosted in microservices  
**Approach**: Individual Python scripts for each table migration

## Constraints & Requirements
- **Source**: Single DUMP file from MySQL with complete tables
- **Destination**: Multiple MySQL databases for microservices
- **Schema Definition**: Single .sql file with CREATE statements (no INSERTs)
- **Schema Mismatch**: Source and target schemas differ; data transformation required
- **One-time Migration**: Source MySQL will be decommissioned post-migration
- **Staging Approach**: Restore dump to clean MySQL, then migrate from staging database
- **Orchestration**: Simple bash-based progress display (no Apache Airflow)
- **Scope**: High-level phases, not detailed implementation

## Technical Stack
- **Database Libraries**: PyMySQL/mysql-connector-python, SQLAlchemy
- **Data Processing**: Polar for transformations
- **Configuration**: PyYAML for mappings
- **Monitoring**: Python logging, bash progress display
- **Infrastructure**: Staging MySQL + Target microservice MySQL databases

## Phase 0: Create dummy dump and schemas.
- Set up a MySQL on docker
- Create some dummy tables and data
- Create a dump file
- Set up other MySQL on docker
- **Status**: [ ] Not Started | [ ] In Progress | [ ] Complete
- 
## Migration Phases

### Phase 1: Environment Preparation ⏳
- Restore source DUMP file to staging MySQL database
- Validate target microservice databases accessibility
- Confirm destination schemas are deployed
- **Status**: [ ] Not Started | [ ] In Progress | [ ] Complete

### Phase 2: Configuration Setup ⏳
- Create table-to-microservice mapping configurations
- Define field mappings for schema differences
- Document transformation rules and business logic
- **Status**: [ ] Not Started | [ ] In Progress | [ ] Complete

### Phase 3: Migration Script Development ⏳
- Develop individual Python scripts per table
- Implement extraction, transformation, and loading logic
- Handle schema transformation requirements
- **Status**: [ ] Not Started | [ ] In Progress | [ ] Complete

### Phase 4: Orchestration Framework ⏳
- Create bash-based orchestrator
- Implement dependency order execution
- Add progress display and error handling
- **Status**: [ ] Not Started | [ ] In Progress | [ ] Complete

### Phase 5: Validation & Testing ⏳
- Execute dry-run migrations
- Perform data validation and integrity checks
- Test transformation logic accuracy
- **Status**: [ ] Not Started | [ ] In Progress | [ ] Complete

### Phase 6: Production Migration Execution ⏳
- Run full migration with monitoring
- Track progress and handle errors
- Implement rollback procedures if needed
- **Status**: [ ] Not Started | [ ] In Progress | [ ] Complete

### Phase 7: Post-Migration Cleanup ⏳
- Validate migration completion
- Perform final integrity checks
- Document results and prepare for source decommission
- **Status**: [ ] Not Started | [ ] In Progress | [ ] Complete

## Current Status Tracker
**Last Updated**: [DATE]  
**Current Phase**: [PHASE NUMBER] - [PHASE NAME]  
**Overall Progress**: [X]% Complete  
**Active Tasks**:
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## Next Steps Needed
[Update this section with immediate next actions needed]

## Key Decisions Made
[Document important decisions and rationale as migration progresses]

## Issues & Blockers
[Track any impediments or challenges encountered]

## Usage Instructions
When returning to continue this migration:
1. Update the "Current Status Tracker" section
2. Mark completed phases with ✅
3. Update "Next Steps Needed" with current requirements
4. Reference this prompt to maintain context and approach consistency