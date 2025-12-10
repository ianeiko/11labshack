# 📻 Radio Pacis Populi

**Tagline:** The Infinite Town Hall.

## 🎯 The Mission

To simulate a debate between **11 unique AI Personas**, generating a complex web of conversations. We use a multi-model approach where different LLMs drive different personalities (think: concerned mother, a student, a retired person, a libertarian, a conservative, etc). The personas debate a complex topic and rotate partners, keeping track of how their opinions are changing.

The user interacts via a tactile **Rotary Dial** (and Next/Previous buttons), tuning into these conversations like finding stations on a standard FM radio band. The stations come online dynamically as conversations start. At the end of the debate, we show a **Consensus Report** - explaining the insights on how the entire town shifted their stance.

## 🏗️ Architecture & Tracks

### 1. Character Creation Data
We define **11 Agents**.
*   **Provider Independent:** Cloud providers (Grok, Claude, Gemini, OpenAI) are assigned **randomly** to agents to ensure even usage and prevent provider bias from attaching to specific personality types.
*   **Gap Filler:** Since we have 11 agents (an 11Labs Hackathon constraint), we utilize the **11Labs Sound Effects Studio** to generate humorous audio content or "station breaks" filling the gaps between conversations.

### 2. Conversation Module
The core logic for a single pairwise interaction.
*   Handles the back-and-forth dialogue.
*   Manages turn-taking and context.
*   Outputs the raw text stream.

### 3. Debate Creation
The Orchestrator.
*   **Input:** Takes the **Character Creation Data**.
*   **Process:** Spawns the pairwise conversations.
*   **Logic:** Manages the schedule of who talks to whom.

### 4. Reporting Phase
Two tiers of reporting:
1.  **Single Conversation Report:** A summary and analysis of a specific 1-on-1 debate.
2.  **Aggregate Debate Report:** A holistic "Town Report" summarizing the entire event, sentiment shifts, and key winners/losers of the argument.

### 5. Backend & Data Layer
*   **Database:** **Supabase (Postgres)**.
*   **Function:** Stores debate information, active channels, and streaming status.
*   **Integration:** N8N agents verify data against the model and write directly to Supabase.

---

## 🌟 The Experience (UI/UX)

1.  **The Atmosphere:** The app opens in darkness with ambient crowd noise.
2.  **The Interface:**
    *   **Rotary Dial:** Ideally for browsing, but stations appear dynamically.
    *   **Next / Previous Buttons:** **CRUCIAL ADDITION**. Since stations (conversations) come online asynchronously after rounds end, the dial alone is insufficient. Buttons allow users to jump to the next active frequency immediately.
3.  **The Lock-In:** Tuning into a station cross-fades into the live audio of two agents calculating/debating.
4.  **The Insight:** The final Consensus Report breaks down the "Town Hall" result.

---

## 🧠 The Engine: N8N + MCP

*   **Logic:** N8N workflows orchestrate the 4 tracks (Character, Conversation, Debate, Reporting).
*   **Tools:** Agents have tools within N8N to write to the Supabase database directly.
*   **Verification:** A verification tool (living in a shared folder between `n8n/` and `app/`) ensures data integrity against the schema before writing.

## 🛠️ Tech Stack

### Frontend
*   **Framework:** **Next.js**.
*   **Styling:** Tailwind CSS (or custom CSS for premium feel).
*   **State:** Reads active debate info from Supabase.

### Backend / Orchestration
*   **Orchestrator:** **n8n** (likely n8n 2.0 if compatible with MCP).
*   **Database:** **Supabase**.
*   **AI Models:** Mix of Grok, Claude, Gemini, OpenAI (Randomly assigned).
*   **Audio:** **ElevenLabs API** (Voice + Sound Effects).

---

## 📊 The "Meta-Analysis"

Every agent fills out a structured questionnaire regarding their stance on the topic *before* and *after* the debate. The Global Summary aggregates this to show the "Drift" of public opinion.
