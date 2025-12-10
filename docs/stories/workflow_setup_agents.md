# Workflow Specification: Setup Agents

**Epic Reference**: Epic 1 (Character Creation Engine)
**Stories**: 1.1, 1.2, 1.3, 1.4

## Goal
To initialize the `agents` table with 11 unique, randomly assigned, and validated persona records. This is likely a "Run Once" workflow.

## Nodes & Logic

### 1. Trigger
- **Type**: `Manual Trigger`
- **Why**: This is an administrative setup task.

### 2. Generate Provider Distribution
- **Node**: `Code Node` (Javascript)
- **Logic**:
  - Create an array of 11 provider strings: `['grok', 'grok', 'grok', 'claude', 'claude', 'claude', 'gemini', 'gemini', 'gemini', 'openai', 'openai']`.
  - Shuffle the array using Fisher-Yates or simple sort.
  - Output: A list of objects `[{ provider: 'grok' }, { provider: 'claude' }, ...]`.

### 3. Generate Agent Profiles (Loop)
- **Node**: `Loop Over Items` (Batch Size: 1)
- **Input**: The list of providers.

### 4. Agentic Generation & Validation
- **Node**: `AI Agent` (LangChain Agent)
- **Tools**: `validate_json_schema` (Code Tool)
- **Logic**:
  - The Agent is prompted to create a unique persona.
  - **Prompt**:
    > You are a creative writer. Create a unique persona for a radio debate participant.
    > Provider assigned: `{{ $json.provider }}`.
    > Output JSON schema: { name, bio, voice_id, initial_stance, provider }.
    > The 'initial_stance' should be a complex object describing their view on "The Future of Humanity".
    > ALWAYS use the `validate_json_schema` tool to check your work before responding.
  - **Tool Logic (`validate_json_schema`)**:
    - Takes the JSON string from the agent.
    - Validates against the strict schema: `required: [name, bio, voice_id, initial_stance, provider]`.
    - Returns success or specific error messages (e.g., "Missing keys: voice_id") to the Agent so it can self-correct.

### 5. Gap Fillers (Optional - Not in POC)
- **Node**: `11Labs Node` (if available via MCP or HTTP Request)
- **Logic**: Generate sound effect metadata (Story 1.4). *Defer this to a separate sub-flow if complex.*

### 6. Database Write
- **Node**: `Postgres Node` (Supabase)
- **Operation**: `INSERT` into `agents` table.
- **Mapping**: Map JSON fields to DB columns.

### 7. Summary
- **Node**: `Code Node`
- **Logic**: Returns a summary of the operation (e.g., "All agents processed").
- **Notes**: This node is also used as a bypass target for the "Test Mode".

## Test Mode
- **Parameter**: `test_run` (boolean) passed via Webhook body.
- **Logic**: If `test_run` is true, the workflow skips the LLM generation/DB write steps and jumps directly to the **Summary** node to verify connectivity and basic workflow integrity.

## Output
- 11 verified rows in the `agents` table (in normal run).
- JSON success message (in test run).

## N8N-MCP Specifics
- Use standard `n8n-nodes-base.postgres` for DB.
- Use `n8n-nodes-base.openAi` or compatible for LLM.
- Use `n8n-nodes-base.code` for shuffling and validation.
