# Data Model Proposal

**Context**: This data model supports the Radio Pacis Populi architecture defined in `docs/epics_stories.md`. It addresses the need for Character tracking, Conversation streaming, and Reporting.

## 1. Core Tables

### `agents`
*Stores the static and stateful data for the 11 AI Personas.*

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `UUID` | Primary Key. |
| `name` | `TEXT` | Display name (e.g., "The Skeptic"). |
| `bio` | `TEXT` | Prompt/Behavioral description. |
| `voice_id` | `TEXT` | 11Labs Voice ID. |
| `provider` | `TEXT` | 'grok', 'claude', 'gemini', 'openai' (Randomly assigned). |
| `initial_stance` | `JSONB` | Structured object representing pre-debate views. |
| `current_stance` | `JSONB` | Updated after debates (optional tracking). |

### `conversations` (The Stations)
*Represents a pairwise debate event. Corresponds to a frequency on the dial.*

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `UUID` | Primary Key. |
| `agent_a_id` | `UUID` | FK to `agents.id`. |
| `agent_b_id` | `UUID` | FK to `agents.id`. |
| `status` | `TEXT` | 'scheduled', 'broadcasting', 'completed'. |
| `frequency` | `FLOAT` | Assigned radio frequency (e.g., 92.3). |
| `topic` | `TEXT` | The debate topic. |
| `started_at` | `TIMESTAMPTZ` | When status changed to broadcasting. |
| `ended_at` | `TIMESTAMPTZ` | When status changed to completed. |

### `turns` (The Stream)
*Granular log of every message exchanged. Used for the "Live Feed".*

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `BIGINT` | Primary Key. |
| `conversation_id` | `UUID` | FK to `conversations.id`. |
| `turn_number` | `INT` | 1, 2, 3... |
| `speaker_id` | `UUID` | FK to `agents.id`. |
| `content_text` | `TEXT` | The raw argument text. |
| `audio_url` | `TEXT` | URL to the generated 11Labs audio file. |
| `created_at` | `TIMESTAMPTZ` | Default `now()`. |

### `reports`
*The "1-on-1 Wrap-Up" for each conversation.*

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `UUID` | Primary Key. |
| `conversation_id` | `UUID` | FK to `conversations.id`. |
| `summary` | `TEXT` | Short recap. |
| `verdict` | `TEXT` | Who made better points? |
| `key_insights` | `JSONB` | List of main clashes/points. |
| `created_at` | `TIMESTAMPTZ` | Default `now()`. |

### `consensus_reports`
*The Global Town Hall Summary.*

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `UUID` | Primary Key. |
| `total_conversations` | `INT` | Should match target (e.g., 55). |
| `global_drift` | `JSONB` | Aggregated stance shift metrics. |
| `narrative_text` | `TEXT` | The "State of the Union" script. |
| `audio_url` | `TEXT` | Voiceover of the final report. |

## 2. Relationships

*   **Agents** have many **Conversations** (as A or B).
*   **Conversations** have many **Turns**.
*   **Conversations** have one **Report**.

## 3. Realtime Requirements

Supabase Realtime must be enabled for:
1.  `conversations` (Filter: `status=eq.broadcasting`) - To light up the "On Air" stations on the frontend map.
2.  `turns` (Filter: `conversation_id=eq.YOUR_ID`) - To stream text/audio to the active listener.

## 4. Updates from Previous SQL (`supabase_setup.sql`)

*   *Rename* `stream_buffer` -> `turns` (more semantic, permanent storage).
*   *Rename* `debate_reports` -> `reports`.
*   *Add* `conversations` table to link turns together (previously missing context).
*   *Add* `agents` table to centralize character configs.
