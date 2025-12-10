# Workflow Specification: Run Debate Loop

**Epic Reference**: Epic 2 & 3
**Stories**: 2.1, 2.2, 2.3, 3.2

## Goal
The core engine. Picks up a scheduled conversation and executes it turn-by-turn.

## Nodes & Logic

### 1. Trigger
- **Type**: `Webhook` (triggered by Orchestrator or Frontend) OR `Schedule` (polling `status='scheduled'`).
- **Best Practice**: A **Supervisor Workflow** that calls this sub-workflow for each active station.

### 2. Update Status: Broadcasting
- **Node**: `Postgres Node`
- **Operation**: `UPDATE conversations SET status = 'broadcasting', started_at = NOW() WHERE id = {{conversation_id}}`.

### 3. Fetch Context
- **Node**: `Postgres Node`
- **Operation**: `SELECT * FROM agents WHERE id IN (agent_a, agent_b)`.

### 4. Debate Loop (Split In Batches / Loop)
- **Constraint**: Max Turns (e.g., 6 turns total).
- **State**: Keep track of `history` in the loop buffer.
- **Node**: `Switch` (Check Turn Count).

### 5. Agent Turn (LLM)
- **Node**: `AI Agent` (Dynamic Provider)
- **Logic**:
  - Determine active speaker (A or B).
  - Select Provider Model based on `agent.provider` field (e.g., Switch node routing to specific Model Nodes or a Dynamic Model Tool).
  - **Prompt**: Include `bio`, `history`, `opponent context`.
  - **Output**: Argument text.

### 6. Log Turn (Realtime)
- **Node**: `Postgres Node` (Story 2.2)
- **Operation**: `INSERT` into `turns`.
- **Validation**: Ensure text is clean.

### 7. Loop Back
- Append response to `history`.
- Increment Turn Count.
- Repeat.

### 8. Update Status: Completed
- **Node**: `Postgres Node`
- **Operation**: `UPDATE conversations SET status = 'completed', ended_at = NOW()`.

### 9. Trigger Reports
- **Node**: `Execute Workflow`
- **Target**: `generate_reports` (Pass `conversation_id`).

## N8N-MCP Specifics
- **Dynamic Models**: Since provider varies, use a `Switch` node after identifying the speaker to route to `OpenAI Node`, `Anthropic Node`, etc.
- **State Management**: Use `Code Node` to aggregate the conversation string efficiently between loops.
