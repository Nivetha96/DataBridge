# DataBridge: A Data Integration Toolkit

## Overview

Databridge is a command-line toolkit called for managing data connections and transferring files
between them.

## Language

**Python 3.11+**

## DataBridge Usage Example

### Phase 1: Connection Management + Local Filesystem Connector

Established the adapter pattern and built a stateful connection management.

**Requirements Satisfied:**

1. Defined a **connector interface** with at minimum these operations:
   - `list` -- list available files in the connection
   - `read` -- read a file's contents from the connection
   - `write` -- write contents to a file in the connection

2. Implemented a **local filesystem connector** that operates on a directory path.

3. Built a **connection store** that persists connection configuration (name, type, and type-specific settings). The config details are encrypted using Fernet library.

4. Examples

```bash
# Create a local filesystem connection
databridge create-connection --name local_data --type local --path ./data
# Output
Connection 'local_data' created
# DB Store
NAME                 TYPE       CONFIG
-------------------- ---------- ----------------------------------------
local_data           local      gAAAAABqHQMxRUjAcjzPK9s1sc9Ax8**

# List files available through a connection
databridge list --connection local_data
#Output 
customers.csv
products.json
# Preview file content and infer schema (for CSV/JSON files)
databridge head --connection local_data --file customers.csv
# Output
Displaying schema ->
  COLUMN       TYPE     NULLABLE
  -----------  -------  --------
  id           integer  no
  first_name   string   no
  last_name    string   no
  email        string   no
  age          integer  no
  signup_date  date     no
  is_active    boolean  no
  balance      float    no
Displaying data ->
id  first_name  last_name  email                     age  signup_date  is_active  balance
--  ----------  ---------  ------------------------  ---  -----------  ---------  -------
1   Alice       Chen       alice.chen@example.com    34   2023-06-15   true       1250.00
2   Bob         Martinez   bob.martinez@example.com  28   2024-01-20   true       340.50 
3   Carol       Johnson    carol.j@example.com       45   2022-11-03   false      0.00   
4   David       Kim        david.kim@example.com     31   2023-09-08   true       890.75 
5   Eve         Okafor     eve.okafor@example.com    27   2024-03-12   true       2100.00
```

### Phase 2: SSH/SFTP Connector + Data Transfer

**Goal:** Proved the adapter pattern works across connection types and built the transfer pipeline.

**Requirements Satisfied:**

1. Implemented an **SFTP connector** that connects to an SSH/SFTP server using stored credentials (host, port, username, password). It uses the same connector interface defined in Phase 1.

2. Built a **transfer** operation that reads a file from a source connection and writes it to a destination connection. The transfer should be **data-agnostic** -- it moves the file without inspecting or transforming the content.

3. Track **transfer status** including: started/completed timestamps, bytes or rows transferred (logging is fine).

4. Support the following operations:

```bash
# Create an SFTP connection
databridge create-connection --name remote_server --type sftp \
  --host localhost --port 2222 --user testuser --password testpass
# Output
Connection 'remote_server' created
# List files on the remote server
databridge list --connection remote_server
#Output
customers.csv
products.json
# Transfer a file from local to SFTP
databridge transfer \
  --source local_data --source-file customers.csv \
  --destination remote_server --destination-file customers_from_local.csv
#Output
Transfer completed successfully
Bytes transferred: 1006
Started: 2026-06-01 00:34:13.438106
Completed: 2026-06-01 00:34:13.441120
# Transfer a file from SFTP back to local
databridge transfer \
  --source remote_server --source-file customers.csv \
  --destination local_data --destination-file customers_from_remote.csv
 #Output
Transfer completed successfully
Bytes transferred: 1006
Started: 2026-06-01 00:34:36.414137
Completed: 2026-06-01 00:34:36.420974 
```

### Phase 3: Head Utility + Polish

**Goal:** Build a useful schema preview tool and polish error handling.

**Requirements Satisfied:**

1. Enhanced the **head utility** to infer schema from structured file formats:
   - For **CSV**: display column names and inferred types (string, integer, float, boolean, date)
   - For **JSON** (array-of-objects): display field names and inferred types
   - The head utility should work through **any connector** -- local or SFTP

2. Polished **error handling** across the application:
   - Connection creation with invalid parameters gives clear feedback
   - SFTP connection failures produce actionable error messages
   - Transferring to/from a non-existent file is handled gracefully

```bash
# Preview schema of a file on the SFTP server
databridge head --connection remote_server --file customers.csv
# Output
Displaying schema ->
  COLUMN       TYPE     NULLABLE
  -----------  -------  --------
  id           integer  no
  first_name   string   no
  last_name    string   no
  email        string   no
  age          integer  no
  signup_date  date     no
  is_active    boolean  no
  balance      float    no
Displaying data ->
id  first_name  last_name  email                     age  signup_date  is_active  balance
--  ----------  ---------  ------------------------  ---  -----------  ---------  -------
1   Alice       Chen       alice.chen@example.com    34   2023-06-15   true       1250.00
2   Bob         Martinez   bob.martinez@example.com  28   2024-01-20   true       340.50 
3   Carol       Johnson    carol.j@example.com       45   2022-11-03   false      0.00   
4   David       Kim        david.kim@example.com     31   2023-09-08   true       890.75 
5   Eve         Okafor     eve.okafor@example.com    27   2024-03-12   true       2100.00
```

### Bonus Completed

- Connection healthcheck command (verify credentials are valid without transferring data)
```bash
# Healthcheck
 databridge check-health --connection local_data
 # Output
Local connection successful
```
- Encryption of stored credentials at rest
```bash
 uv run tests/storage/test_connection_db.py
 NAME                 TYPE       CONFIG
-------------------- ---------- ----------------------------------------
local_data           local      gAAAAAB***
remote_server        sftp       gAAAAAB***
```
- Unit tests for the connector interface contract
```bash
uv run pytest
========================test session starts ===========================
platform darwin -- Python 3.11.5, pytest-9.0.3, pluggy-1.6.0
rootdir: /Users/nivethab/Documents/GitHub/databridge
configfile: pyproject.toml
collected 26 items                                                                                                                                       

tests/connectors/test_connector_factory.py .... [ 15%]
tests/connectors/test_local_connector.py ............[ 61%]
tests/connectors/test_sftp_connector.py ..........[100%]

============================= 26 passed in 0.31s ===========================

```
- A proper CLI framework (argparse/Click, OptionParser, Mix tasks)

## Submission

- Submit as a Git repository (public or private -- if private, grant access to the reviewer)
- Include a **README** in your project with:
  - How to set up and run your solution
  - Any design decisions worth calling out
  - What you would improve with more time
- Commit history matters -- we'd like to see how you built it incrementally, not as a single commit

## Tool Used 

- Claude Code
- Used to analyse on errors, look for better options available for encryption/decryption, implement test cases
