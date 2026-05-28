# DataBridge: A Data Integration Toolkit

## Overview

Build a command-line toolkit called **DataBridge** for managing data connections and transferring files
between them. The requirements are outlined belowed and broken into three phases already.
Phase's 1 & 2 are required and expected to be completed, Phase 3 is optional.

**Expectation:** We value quality over completeness -- it is better to finish Phases 1 and 2 well than
to rush through all three phases. Use of AI tooling is acceptable, see [AI Tooling Section](#ai-tooling).

## Language

**Python 3.10+**, **Ruby 3.0+**, and **Elixir 1.14+** are recommended, but choose whichever language you feel most comfortable with.

External libraries are allowed for SSH/SFTP connectivity, YAML/JSON parsing, and CLI frameworks. The core logic (connection management, adapter design, transfer orchestration) should be your own.

## What We Provide

- **`data/customers.csv`** -- a sample CSV file with 15 rows of customer data
- **`data/products.json`** -- a sample JSON file with 6 product records
- **`docker-compose.yml`** -- spins up a local SFTP server for testing

### Setting Up the SFTP Server

```bash
docker compose up -d
```

This starts an SFTP server on **port 2222** with the following credentials:

| Field    | Value      |
|----------|------------|
| Host     | localhost  |
| Port     | 2222       |
| Username | testuser   |
| Password | testpass   |

Files written to the SFTP server will appear in the `sftp_data/` directory on your local machine.

You can verify the server is running:

```bash
sftp -P 2222 testuser@localhost
```

## What You Build

### Phase 1: Connection Management + Local Filesystem Connector

**Goal:** Establish the adapter pattern and build stateful connection management.

**Requirements:**

1. Define a **connector interface** with at minimum these operations:
   - `list` -- list available files in the connection
   - `read` -- read a file's contents from the connection
   - `write` -- write contents to a file in the connection

2. Implement a **local filesystem connector** that operates on a directory path.

3. Build a **connection store** that persists connection configuration (name, type, and type-specific settings). Connections must survive across separate invocations of your program. You may use SQLite, a JSON file, or any persistent mechanism you choose.

4. Support the following operations (CLI commands shown as examples -- you may design the interface however you like):

```bash
# Create a local filesystem connection
databridge create-connection --name local_data --type local --path ./data

# List files available through a connection
databridge list --connection local_data

# Preview file content and infer schema (for CSV/JSON files)
databridge head --connection local_data --file customers.csv
```

**Acceptance criteria:**

- A clear connector interface exists
- Local filesystem connector implements the interface
- Connections persist across program invocations
- `list` shows files in the connected directory
- `head` displays the first several rows of a file

### Phase 2: SSH/SFTP Connector + Data Transfer

**Goal:** Prove the adapter pattern works across connection types and build the transfer pipeline.

**Requirements:**

1. Implement an **SFTP connector** that connects to an SSH/SFTP server using stored credentials (host, port, username, password). It should conform to the same connector interface you defined in Phase 1, so the rest of the system can use it without knowing whether the underlying connection is local or remote.

2. Build a **transfer** operation that reads a file from a source connection and writes it to a destination connection. The transfer should be **data-agnostic** -- it moves the file without inspecting or transforming the content.

3. Track **transfer status** including: started/completed timestamps, bytes or rows transferred (logging is fine).

4. Support the following operations:

```bash
# Create an SFTP connection
databridge create-connection --name remote_server --type sftp \
  --host localhost --port 2222 --user testuser --password testpass

# List files on the remote server
databridge list --connection remote_server

# Transfer a file from local to SFTP
databridge transfer \
  --source local_data --source-file customers.csv \
  --destination remote_server --destination-file customers.csv

# Transfer a file from SFTP back to local
databridge transfer \
  --source remote_server --source-file customers.csv \
  --destination local_data --destination-file customers_from_remote.csv
```

**Acceptance criteria:**

- SFTP connector implements the same interface as the local connector
- Transfers work bidirectionally (local to SFTP, SFTP to local)
- Transfer status is reported (timestamps, size)
- The transfer operation does not contain connector-specific logic (no `if type == "sftp"` branching)
- Adding a new connector type would not require changes to the transfer logic
- Connection failures (wrong credentials, server down) produce clear error messages

### Phase 3: Head Utility + Polish (Optional)

**Goal:** Build a useful schema preview tool and polish error handling.

**Requirements:**

1. Enhance the **head utility** to infer schema from structured file formats:
   - For **CSV**: display column names and inferred types (string, integer, float, boolean, date)
   - For **JSON** (array-of-objects): display field names and inferred types
   - The head utility should work through **any connector** -- local or SFTP

2. Polish **error handling** across the application:
   - Connection creation with invalid parameters gives clear feedback
   - SFTP connection failures produce actionable error messages
   - Transferring to/from a non-existent file is handled gracefully

```bash
# Preview schema of a file on the SFTP server
databridge head --connection remote_server --file customers.csv
```

**Acceptance criteria:**

- Schema inference produces reasonable types for the provided sample data
- Head utility works through both local and SFTP connections
- Error messages help the user understand what went wrong and how to fix it

### Bonus (Optional)

These are genuinely optional. Completing any of them signals depth but is not expected:

- Connection healthcheck command (verify credentials are valid without transferring data)
- Streaming/lazy I/O so large files don't need to be fully loaded into memory
- Encryption of stored credentials at rest
- Additional connector types (e.g., S3)
- Unit tests for the connector interface contract
- A proper CLI framework (argparse/Click, OptionParser, Mix tasks)

## Submission

- Submit as a Git repository (public or private -- if private, grant access to the reviewer)
- Include a **README** in your project with:
  - How to set up and run your solution
  - Any design decisions worth calling out
  - What you would improve with more time
- Commit history matters -- we'd like to see how you built it incrementally, not as a single commit

## What We Value

In priority order:

1. **Clean abstractions** -- a well-designed connector interface matters more than feature count
2. **Working code** -- we will run your solution against the provided SFTP server
3. **Stateful connections** -- connections should persist and be reusable
4. **Thoughtful error handling** -- clear messages over silent failures
5. **Code organization** -- sensible file/module structure for a growing project

## Rules

- Open book: use documentation, Stack Overflow, language references
- AI tooling is allowed and expected. Please document your process and how you leverage AI tooling (see the AI Tooling section below).
- External libraries are fine for SSH/SFTP, YAML parsing, and CLI frameworks

## AI Tooling

With the advent of agentic coding, we expect our engineers to leverage AI tooling and workflows, so using these for this take-home is allowed.
However, we also expect that the code you submit is code you can explain in-depth and provide the reasoning for architectural decisions.

In your project README, please include a section documenting:

- **What tooling you used** (e.g., Claude Code, Cursor, Copilot, Gemini, ChatGPT, etc.)
- **Your general process** for how you used it -- skills, agents, custom commands, workflows, etc.
- **One or two example prompts** that illustrate how you collaborated with the tooling
- **A short paragraph or two** explaining your overall approach

We are not grading on whether or how much AI you used; we are grading on the quality of the code and your ability to reason about it.
