# 📻 Radio Pacis Populi

**Tagline:** The Infinite Town Hall.

## 🎯 The Mission

To generate a **multi-voiced consensus report** based on interviews with **11 unique AI Personas**. We use a multi-model approach where different LLMs drive different personalities (e.g., concerned mother, student, retired person, libertarian, conservative, etc.) to answer questions on a specific topic.

The user interacts via a simple audio player that plays the final synthesized report, which features snippets of the different personas speaking in their own voices, woven together by a "Reporter" narrator.

## 🏗️ Architecture & Tracks

### 1. Character Creation (The 11 Personas)
We define **11 Agents**.
*   **Provider Independent:** Cloud providers (Grok, Claude, Gemini, OpenAI) and Models are assigned **randomly** to agents to ensure even usage and prevent bias.
*   **Attributes:** Each agent has a Name, Bio (Persona), and an 11Labs Voice ID.
*   **Storage:** Stored in Supabase `agents` table.

### 2. Interview Module
The core logic for gathering content.
*   **Input:** A specific "Topic" or "Question".
*   **Process:** Each of the 11 Agents is prompted individually to give their "take" or answer.
*   **Output:** Text responses stored in Supabase `interviews` table.

### 3. Report Generation (The Synthesis)
The Orchestrator.
*   **Input:** The set of 11 interview answers.
*   **Process:** A "Reporter" LLM synthesizes these distinct viewpoints into a cohesive script. The script looks like a radio report, alternating between the Reporter's narration and direct quotes (soundbites) from the Personas.
*   **Output:** A multi-speaker script.

### 4. Audio Production
*   **Input:** The multi-speaker script.
*   **Process:**
    *   Iterate through script segments.
    *   Use 11Labs API to generate audio for each segment using the correct Speaker's Voice ID.
    *   Concatenate/Stitch the audio files into one single track.
*   **Output:** Final MP3 URL stored in `reports`.

### 5. Backend & Data Layer
*   **Database:** **Supabase (Postgres)**.
*   **Function:** Stores agents, interviews, and final reports.
*   **Integration:** N8N handles all logic (Agent Gen -> Interview -> Report -> Audio).

---

## 🌟 The Experience (UI/UX)

1.  **Simple Player:** The main interface is a clean, minimal audio player.
2.  **The Content:** It plays the "Report" for the current topic.
3.  **Controls:** Play/Pause. Potentially Next/Prev to switch between different Reports (topics).

---

## 🛠️ Engineering & Development Standards

To strictly enforce quality and scalability, we adopt a **"Workflow as API"** development paradigm.

### 1. Workflow Architecture ("The API Contract")
*   **Single Responsibility:** Each workflow must perform exactly **one** discrete operation.
*   **Structure:**
    1.  **Trigger:** Webhook.
    2.  **Process:** Business logic, DB operations, AI calls.
    3.  **Output:** JSON response.

### 2. Naming Convention & Execution Order
*   `1.0_generate_personas.json` (Run once to seed DB with 11 agents)
*   `2.0_conduct_interviews.json` (Run per topic; interviews all agents)
*   `3.0_generate_report.json` (Run per topic; synthesizes interviews into script)
*   `4.0_synthesize_audio.json` (Run per topic; turns script into audio)

---

## 🛠️ Tech Stack

*   **Orchestrator:** **n8n**
*   **Database:** **Supabase**
*   **AI Models:** Mix of Grok, Claude, Gemini, OpenAI (Randomly assigned)
*   **Audio:** **ElevenLabs API**

---

# Data Model

## 1. Core Tables

### `agents`
*Stores the 11 AI Personas.*

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `UUID` | Primary Key. |
| `name` | `TEXT` | Display name (e.g., "The Skeptic"). |
| `bio` | `TEXT` | Persona description/System prompt. |
| `voice_id` | `TEXT` | 11Labs Voice ID. |
| `provider` | `TEXT` | 'grok', 'claude', 'gemini', 'openai'. |
| `model` | `TEXT` | Specific model used (e.g. 'grok-beta'). |

### `interviews`
*Stores the raw answers from agents on a topic.*

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `UUID` | Primary Key. |
| `agent_id` | `UUID` | FK to `agents.id`. |
| `topic` | `TEXT` | The general topic (e.g. "Universal Basic Income"). |
| `question` | `TEXT` | The specific prompt asked. |
| `answer` | `TEXT` | The agent's raw response. |
| `created_at` | `TIMESTAMPTZ` | Default `now()`. |

### `reports`
*The final synthesized output.*

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `UUID` | Primary Key. |
| `topic` | `TEXT` | The topic covered. |
| `script` | `JSONB` | Structured script (Speaker + Text segments). |
| `audio_url` | `TEXT` | URL to the final stitched audio. |
| `created_at` | `TIMESTAMPTZ` | Default `now()`. |
