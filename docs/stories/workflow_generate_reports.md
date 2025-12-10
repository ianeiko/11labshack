# Workflow Specification: Generate Reports

**Epic Reference**: Epic 4 (Reporting & Analytics)
**Stories**: 4.1, 4.2, 4.3

## Goal
To analyze completed debates and eventually the entire event.

## Nodes & Logic

### 1. Trigger
- **Type**: `Execute Workflow Trigger`.
- **Input**: `conversation_id`.

### 2. Fetch Transcript
- **Node**: `Postgres Node`
- **Operation**: `SELECT * FROM turns WHERE conversation_id = {{id}} ORDER BY turn_number ASC`.

### 3. Conversation Analysis (1-on-1)
- **Node**: `AI Agent` (Reporter Persona).
- **Prompt**:
  > Read the transcript.
  > summarized: Short recap.
  > verdict: Who won?
  > insights: Key points.
  > Output JSON.
- **Validation**: Use schema validation pattern.

### 4. Save Report
- **Node**: `Postgres Node`
- **Operation**: `INSERT` into `reports`.

### 5. Check for Global Consensus (Optional)
- **Node**: `Postgres Node`
- **Logic**: Check if all 55 conversations are done.
- **If True**: Trigger "Town Hall Summary".

### 6. Town Hall Summary (Sub-branch)
- **Node**: `Postgres Node` (Fetch All Reports).
- **Node**: `AI Agent` (Global Analyst).
- **Prompt**: Analyze drift and generate `narrative_text`.
- **Output**: `Postgres Insert` into `consensus_reports`.

## N8N-MCP Specifics
- **Long Context**: The Global Summary might require a large context window model (e.g., Gemini 1.5 Pro or Claude 3 Opus) if feeding all 55 summaries.
