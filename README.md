# 📻 Pax Populi: The Infinite Town Hall
**Tagline:** The Infinite Town Hall.

## 🎯 The Mission

To simulate a debate between **100 unique AI Personas (50 concurrent pairs)**. We use a multile models approach where different LLMs drive different personalities (think: concerned mother, a student, a retired person, a libertarian, a conservative, etc). The personas debate a complex topic and rotate partners keeping track of how their opinions are changinge. The user interacts via a tactile **Rotary Dial**, tuning into these conversations like finding stations on a radio. At the end of the debate, we show a **Consensus Report** - explaining the insights on how the entire town shifted their stance.

## 🌟 The Experience (Demo Flow)

1.  **The Atmosphere:** The app opens in darkness. You hear the ambient hum of a massive crowd (ElevenLabs SFX). A glowing **Rotary Dial** sits in the center.
2.  **The Spin:** The user rotates the dial. Heavy radio static and interference plays *only* while the dial is in motion.
3.  **The Lock-In:** The dial stops on "Frequency 12." The static cuts out.
4. We hear current debate, an elevenlabs voice transcribing the model's output, then the voice tunes out and we play a summary
4.  **The Smart Tune-In:**
      * The system generates a quick **Narrated Summary** of the argument *so far* (e.g., *"The Skeptic is currently pressing the Academic on inflation data..."*).
      * The audio then cross-fades back into the **Live Feed**, dropping you mid-sentence into the raw audio of the two agents debating.
5.  **The Insight:** After all the debators have rotated, the debate concludes and we show a **Consensus Report**— explaining how the 100 agents shifted their stance from their pre-debate questionnaire to their post-debate conclusion, high level insights, maybe even breaking third wall and analyzing which of the models leans which way.

-----

## 🧠 The Engine: Multi-Model Orchestrator (n8n)

We do not rely on a single LLM to generate our "crowd." We assign specific LLMs to specific personality archetypes to ensure genuine diversity of thought and speech patterns:

  * **Grok:** Powers the **"Contrarian/Edgy"** agents.
  * **Claude:** Powers the **"Nuanced/Academic"** agents.
  * **Gemini:** Powers the **"Data-Driven/Analytic"** agents.
  * **OpenAI:** Powers the **"General Populace/Normie"** agents.

> *Note:* These models generate the **Text** and personality logic. **ElevenLabs** is used exclusively for the high-fidelity **Voice** generation and SFX when the user tunes in.

-----

## 📊 The "Meta-Analysis" (The Closer)

The simulation isn't just noise; it's data. Every agent fills out a structured questionnaire regarding their stance on the topic *before* and *after* the debate.

  * **The Global Summary:** Once the simulation concludes, the system aggregates the results of all 50 debates.
  * **The Shift:** It produces a report answering:
      * *TLDR:* (Which arguments were most persuasive?)
      * *The Drift:* "At the start, 60% opposed. Now, only 40% oppose."
      * *Key Insight:* "The 'Grok' agents successfully persuaded the 'Claude' agents on economic points."

-----

## 🏗️ Tech Stack & Workflow

### 1\. Frontend (The Radio)

  * **Tech:** **Bolt** (React/Vite/Tailwind) + ElevenLabs UI Library mono theme.
  * **Component:** Custom SVG **Rotary Dial** with haptic visual feedback.
  * **Visuals:** Live waveform amplitude bars and scrolling teleprompter text.

### 2\. Orchestration (The Brain)

  * **Tech:** **n8n-mcp**, json files for workflows, claude/gemini driven development, github/code rabbit - traditional engineering to keep sanity.
  * **Workflow:**
    1.  User Selects Topic (e.g., "The EU AI Act").
    2.  We prepare extensive material on the subject, a result of deep research showing different positions on the topic.
    3.  Then we spawn 100 Personas (JSON profiles).
    4.  Assigns Provider (Grok/Claude/Gemini/OpenAI) based on archetype.
    5.  Initiates 50 concurrent chat loops in the background.

### 3\. Audio Engine (The Voice)

  * **Tech:** **ElevenLabs API**.
  * **Efficiency:** We only generate audio for the *active* frequency to save latency and credits.
  * **Voices:** 50 distinct Voice pairs mapped to the agent profiles.
  * **SFX:** Procedural static generated during dial rotation.

### 4\. Infrastructure

  * **Backend:** **FastAPI** (Python) for state management.
  * **AI:** n8n-mcp, claude/gemini driven development, github/code rabbit - traditional engineering to keep sanity.
  * **Auth:** **Clerk** (User history).
  * **Code Quality:** **CodeRabbit**.