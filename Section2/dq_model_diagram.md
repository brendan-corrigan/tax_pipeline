# Data Quality Results Data Model

This file describes a conceptual schema for storing data quality results over time.

```text
+-------------------------+
|     data_source         |
+-------------------------+
| data_source_id (PK)     |
| name                    |
| description             |
+-------------------------+
            |
            | 1-to-many
            v
+-------------------------+
|  dq_run                 |
+-------------------------+
| dq_run_id (PK)          |
| data_source_id (FK)     |
| run_timestamp           |
| file_version            |
| row_count               |
+-------------------------+
            |
            | 1-to-many
            v
+-------------------------+
|   dq_dimension_score    |
+-------------------------+
| dimension_score_id (PK) |
| dq_run_id (FK)          |
| dimension_name          |
| score                   |
| passed_rows             |
| failed_rows             |
| total_rows              |
+-------------------------+
            |
            | 1-to-many
            v
+-------------------------+
|    dq_rule_result       |
+-------------------------+
| rule_result_id (PK)     |
| dimension_score_id (FK) |
| rule_name               |
| passed_count            |
| failed_count            |
| rule_description        |
| rule_expression         |
+-------------------------+
```
