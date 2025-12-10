# Workflow Specification: Orchestrate Debates

**Epic Reference**: Epic 3 (Debate Orchestrator)
**Stories**: 3.1, 3.2

## Goal
To generate the master schedule of pairwise conversations (The Stations).

## Nodes & Logic

### 1. Trigger
- **Type**: `Manual Trigger` or `Schedule Trigger` (once per Event).

### 2. Fetch Agents
- **Node**: `Postgres Node`
- **Operation**: `SELECT * FROM agents;`
- **Output**: Array of 11 agent objects.

### 3. Generate Combinations (The Matchmaker)
- **Node**: `Code Node` (Javascript)
- **Logic**:
  - Implement a combination function `getCombinations(agents, 2)`.
  - Result: 55 pairs.
  - Enrich pairs with metadata:
    - `frequency`: Assign from a predefined list (87.5 to 108.0).
    - `topic`: "The Future of Humanity" (or varied topics).
    - `status`: 'scheduled'.

### 4. Batch Insert
- **Node**: `Postgres Node`
- **Operation**: `INSERT` into `conversations`.
- **Batching**: Use `Split In Batches` if 55 is too large for a single insert (unlikely).

## Output
- 55 rows in `conversations` with unique frequency assignments.

## N8N-MCP Specifics
- **Optimization**: Use `Function Item` logic within `Code Node` to keep it pure JS for the combination logic.
