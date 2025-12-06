# Project Name: Pax Populi (Peace of the People)
**Tagline:** The Infinite Town Hall.

## 🎯 The Mission
To simulate a massive electorate debate by spinning up **100 unique AI Agents (50 concurrent pairs)**. We use a multile models approach where different LLMs drive different personalities. The user interacts via a tactile **Rotary Dial**, tuning into these conversations like finding stations on a radio.

## 🌟 The "Winning" Demo (The 2-Minute Video)
* **The Hook:** "We didn't just ask one AI. We asked 100."
* **The Visual:** A minimalist, dark-mode UI centered around a large, glowing **Rotary Dial**.
* **The Action:** The user spins the dial. Initially, we hear crowd noise (ElevenLabs SFX), then it locks onto "Frequency 1-50": A debate between a "Grok-powered" Libertarian and a "Claude-powered" Academic.
* **The Climax:** The "Consensus Report." The simulation ends after each pair rotates twice around, and we see a high-level summary of how the *entire* town's opinion shifted.

## 🛠️ Core Features

### 1. The Interface: The Rotary Dial
* **Start with the Dial** .
* **Haptic Visuals:** As you turn the dial, the UI creates "interference" visuals.
* **Locking In:** When the dial stops on a "frequency" (a specific pair), the interference clears.
* **Active View:**
    * **Live Waveform:** Using ElevenLabs UI Blocks.
    * **Live Transcript:** Scrolling text of the current dialogue.
    * **Profile Overlay:** A simple popup triggered by the user to see who is speaking (e.g., "The Skeptic" vs "The Optimist").

### 2. The Engine: Multi-Model Orchestrator (n8n)
We assign specific LLMs to specific personality archetypes to ensure genuine diversity of thought:
* **Grok:** Powers the "Contrarian/Edgy" agents.
* **Claude:** Powers the "Nuanced/Academic" agents.
* **Gemini:** Powers the "Data-Driven/Analytic" agents.
* **OpenAI:** Powers the "General Populace/Normie" agents.
* *Note:* These models generate the **Text**. ElevenLabs is used exclusively for the **Voice** generation when the user tunes in.

### 3. The "Meta-Analysis" (The Closer)
* **The Global Summary:** Once the simulation concludes (or the user clicks "End Town Hall"), the system aggregates the results of all 50 debates.
* **The Shift:** It produces a report answering:
    * *Who won?* (Which arguments were most persuasive?)
    * *The Drift:* "At the start, 60% opposed. Now, only 40% oppose."
    * *Key Insight:* "The 'Grok' agents successfully persuaded the 'Claude' agents on economic points."

## 🏗️ Tech Stack & Workflow

1.  **Frontend:** **Bolt** (Elevenlabs UI lib)
2.  **Orchestration:** **n8n**.
    * *Workflow:* User Topic -> Spawn 100 Personas -> Assign LLMs -> Run Chat Loops in background.
3.  **Voice:** **ElevenLabs API**.
    * *Trigger:* We only generate audio for the *active* frequency to save latency/credits.
    * *Voices:* Diverse VoiceIDs assigned to the agents.
4.  **Auth:** **Clerk**.
5.  **Code Quality:** **CodeRabbit**.

## 🎬 The Demo Script (Video Flow)

1.  **0:00 - 0:20: The Setup.** "We want to know what EU thinks about age verification policy in the context of developing AI technologies. Let's spin up 100 agents."
2.  **0:20 - 0:50: The Dial.** The dial spins. Static noise.
    * *Stop 1:* Hear a Gemini Agent debating a Grok Agent. The conversation is intense. The text scrolls.
    * *Stop 2:* Spin the dial. Hear a Claude Agent vs OpenAI Agent. Totally different tone.
3.  **0:50 - 1:10: The Profile.** Click on the Grok Agent. Popup: "Personality: Radical | Initial Stance: Against."
4.  **1:10 - 1:40: The Summary.** "Let's see the result." Screen transitions to the **Consensus Dashboard**.
    * *Audio Summary:* A generated news-anchor voice (ElevenLabs) reads: "In today's session, the town shifted 15% toward favorability..."
    * *Visual:* A graph showing the opinion delta.
5.  **1:40 - 2:00: Outro.** "Pax Populi. The future of polling is simulation."