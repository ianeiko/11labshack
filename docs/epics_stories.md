# Epics & User Stories: N8N Architecture

Based on the `docs/prd.md` and `docs/data_model.md` requirements.

## 📖 Epic 1: Character Creation Engine
**Goal:** Robustly generate and configure the 11 unique AI personas in the `agents` table.

### Story 1.1: Persona Schema Definition
- **Description:** Define the strict JSON schema for an Agent Persona to populate the `agents` table.
- **Tasks:**
  - Define fields matching the DB: `id` (UUID), `name`, `bio`, `voice_id`, `provider` (enum), `initial_stance` (JSONB).
  - Create a JSON Schema validator for this structure to be used in N8N.
- **N8N Implementation Notes:**
  - **Global Constants:** Store the schema definition here for easy access across workflows.
  - **Schema Preview:**
    ```json
    {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "bio": { "type": "string" },
        "voice_id": { "type": "string" },
        "initial_stance": {
          "type": "object",
          "properties": {
            "outlook": { "enum": ["optimistic", "pessimistic", "neutral", "chaotic"] },
            "key_beliefs": { "type": "array", "items": { "type": "string" } },
            "topic_leanings": { "type": "object", "description": "Map of topic->sentiment" }
          },
          "required": ["outlook", "key_beliefs"]
        },
        "provider": { "enum": ["grok", "claude", "gemini", "openai"] }
      },
      "required": ["name", "bio", "voice_id", "initial_stance", "provider"]
    }
    ```
  - **Nodes:** Use `Code Node` (JS) with manual validation logic (since `ajv` is unavailable) or a simple internal validator helper.
- **Acceptance Criteria:** A valid JSON schema exists; example JSON passes validation and matches `agents` table columns.

### Story 1.2: Random Provider Distribution Logic
- **Description:** Ensure that the 11 agents are assigned `provider` values (Grok, Claude, Gemini, OpenAI) randomly to prevent "personality bias".
- **Tasks:**
  - Create a utility/node in N8N that assigns a `provider` string to each agent payload.
  - Implement a check to ensure roughly even distribution (e.g., ~3 agents per provider) before insertion.
- **N8N Implementation Notes:**
  - **Nodes:** `Code Node` (JS) to shuffle array of providers and assign to agents.
  - **Logic:** "Deck of Cards" approach. Create an exact array `['grok'*3, 'claude'*3, 'gemini'*3, 'openai'*2]` (total 11). Shuffle this array using Fisher-Yates, then pop one provider for each agent to guarantee exact distribution.
- **Acceptance Criteria:** `agents` table populated with a mix of providers.

### Story 1.3: Agent Profile Generation (The 11)
- **Description:** Write the creative prompts and biographies for the 11 specific characters.
- **Tasks:**
  - Generate content for `bio`, `name`, and `voice_id` fields.
  - Insert the 11 records into the `agents` table.
- **N8N Implementation Notes:**
  - **Nodes:** `OpenAI Node` (or preferred LLM) to generate profiles. **Recommendation:** Generate all 11 profiles in a SINGLE batch prompt to ensure character diversity and avoid "same-voice" syndrome.
  - **Nodes:** `Postgres Node` (Supabase) to `INSERT` into `agents`.
- **Acceptance Criteria:** 11 distinct rows in the `agents` table.

### Story 1.4: "Station Break" Gap Fillers
- **Description:** Generate content for "Station Breaks" to be used during static moments or gaps.
- **Tasks:**
  - Create a library of sound effects/break scripts using 11Labs Sound Effects Studio where applicable (manual or API if available).
  - Store metadata to be accessed during "Static" tuning.
- **N8N Implementation Notes:**
  - **Process:** Use 11Labs Sound Effects to generate audio assets.
  - **Storage:** Metadata in a dedicated table or static config (e.g. `station_breaks` table or simple JSON config).
- **Acceptance Criteria:** Metadata/scripts available for the frontend to play/synthesize.

---

## 🗣️ Epic 2: Conversation Module (The Core Loop)
**Goal:** A reliable, turn-based dialogue engine that simulates a debate and logs to `turns`.

### Story 2.1: Dual-Agent Turn Management
- **Description:** Power the debate loop between `agent_a_id` and `agent_b_id`.
- **Tasks:**
  - Retrieve `agents` data for the context (Bio, Stance).
  - Loop through turns, adhering to max turn limits.
- **N8N Implementation Notes:**
  - **Nodes:** `Postgres Node` (Get Agents).
  - **Memory:** Maintain `chat_history` JSON array in the workflow memory (passed from node to node) to avoid DB read latency on every turn. Write to DB asynchronously (Story 2.2).
  - **Structure:** `Split In Batches` or internal loop trigger.
  - **Logic:** `Switch Node` to check `turn_count < max_turns`.
- **Acceptance Criteria:** A debate runs from start to finish without errors.

### Story 2.2: Live Turn Logging (The Stream)
- **Description:** The N8N agents must write every message to the `turns` table in real-time.
- **Tasks:**
  - Create an N8N tool/node: `write_turn`.
  - Input Payload: `conversation_id`, `turn_number`, `speaker_id`, `content_text`.
  - **Constraint:** `audio_url` is NOT generated here; frontend handles TTS.
- **N8N Implementation Notes:**
  - **Nodes:** `Postgres Node` (`INSERT` into `turns`).
  - **Tables:** Ensure `turns` table matches `data_model.md`: `id` (BigInt), `conversation_id`(UUID), `turn_number`(Int), `speaker_id`(UUID), `content_text`(Text).
- **Acceptance Criteria:** Rows appear in `turns` table sequentially during execution with text content.

### Story 2.3: Data Model Verification
- **Description:** Prevent malformed data from polluting the DB.
- **Tasks:**
  - Integration point: Verify payload against the schema for `turns` and `reports` before the `postgres_insert` node.
- **N8N Implementation Notes:**
  - **Global Constants:** Retrieve schemas from here.
  - **Nodes:** `Code Node` with JS validation logic.
  - **Error Handling:** `Error Trigger` node or `Continue On Fail`.
- **Acceptance Criteria:** Invalid payloads trigger an error/retry.

---

## 🎬 Epic 3: Debate Orchestrator (The Spawner)
**Goal:** Manage the `conversations` lifecycle (Scheduled -> Broadcasting -> Completed).

### Story 3.1: The Matchmaker (Spawner Workflow)
- **Description:** A master workflow that populates the `conversations` table.
- **Tasks:**
  - Generate the 55 unique pairs from the 11 agents ($n=11, k=2$).
  - Insert rows into `conversations` with `status = 'scheduled'` and assigned `frequency`.
  - **Frequency Mapping:** Map each conversation to a specific frequency. Range 87.5 - 108.0 MHz (20.5 MHz span). 55 Stations. Spacing: ~0.4 MHz.
    - Algo: `87.5 + (index * 0.4)` (approx). Track used frequencies to avoid collision.
- **N8N Implementation Notes:**
  - **Nodes:** `Postgres Node` (Fetch all Agents).
  - **Nodes:** `Code Node` (JS) to generate pairwise combinations (nCr).
  - **Nodes:** `Postgres Node` (Batch Insert into `conversations`).
- **Acceptance Criteria:** `conversations` table populated with 55 rows, ready to be picked up.

### Story 3.2: Dynamic "On Air" Status
- **Description:** The system must update `conversations.status` to drive the UI and Next/Previous buttons.
- **Tasks:**
  - **Start:** Update `status` to `'broadcasting'` and `started_at` to `NOW()`.
  - **End:** Update `status` to `'completed'` and `ended_at` to `NOW()`.
- **N8N Implementation Notes:**
  - **Nodes:** `Postgres Node` (`UPDATE` `conversations` SET status...).
  - **Trigger:** Start of Conversation Workflow -> Update "Broadcasting"; End -> Update "Completed".
- **Realtime:** This drives the Supervisor Realtime events for the frontend.
- **Acceptance Criteria:** Frontend queries `WHERE status = 'broadcasting'` reflect the running N8N workflows.

---

## 📊 Epic 4: Reporting & Analytics
**Goal:** Synthesize results into `reports` and `consensus_reports`.

### Story 4.1: The 1-on-1 Wrap-Up
- **Description:** Summarize a single completed conversation into the `reports` table.
- **Tasks:**
  - Trigger: When `conversations.status` moves to `'completed'`.
  - Process: Send full `turns` transcript to a Reporter Agent.
  - Output: Insert into `reports` (`summary`, `verdict`, `key_insights`).
- **N8N Implementation Notes:**
  - **Nodes:** `Postgres Node` (Fetch turns for `conversation_id`).
  - **Nodes:** `LLM Chain / Agent` (Summarize transcript).
  - **Nodes:** `Postgres Node` (Insert `reports`).
- **Acceptance Criteria:** A single row in `reports` linked to the `conversation_id`.

### Story 4.2: The Town Hall Consensus
- **Description:** The final meta-analysis stored in `consensus_reports`.
- **Tasks:**
  - Aggregate: `agents.initial_stance` vs `agents.current_stance` (if updated) or overall shift analysis.
  - Insert: `global_drift` (JSONB), `narrative_text` into `consensus_reports`.
- **N8N Implementation Notes:**
  - **Nodes:** `Postgres Node` (Fetch all reports/agents).
  - **Nodes:** `LLM Chain` (Global Analysis Prompt).
- **Acceptance Criteria:** The final artifact row exists in `consensus_reports`.

### Story 4.3: Reporter Script Generation
- **Description:** Generate the `narrative_text` for the reporter.
- **Tasks:**
  - Ensure `narrative_text` is written to `consensus_reports`.
  - **Note:** Audio generation via 11Labs is removed from this workflow. Frontend will synthesize the `narrative_text`.
- **N8N Implementation Notes:**
  - **Use Case:** This script is read by the "Host" persona.
  - **Nodes:** `Postgres Node` (Update record with text).
- **Acceptance Criteria:** Final report contains the script text.
