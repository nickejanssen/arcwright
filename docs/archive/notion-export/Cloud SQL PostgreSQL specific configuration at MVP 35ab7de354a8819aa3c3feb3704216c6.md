# Cloud SQL PostgreSQL specific configuration at MVP (instance class, storage, backup retention)

Category: Product
Date Opened: May 7, 2026
Priority: Medium
Resolution Notes: Decided on Cloud SQL PostgreSQL but not the specific tier. db-f1-micro is the smallest; db-g1-small or shared-core may be needed for prod traffic. Storage starts at 10GB. Free GCP credits ($300) cover ~20 months of minimum config. Specific config TBD when actual session volume materializes.
Status: Open
Where Resolved: Implementation kickoff in Claude Code; revisit at first month of real traffic.