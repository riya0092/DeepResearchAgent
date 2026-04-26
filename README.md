# 🔬 AutoScholar: Self-Correcting Deep Research Agent

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/LangGraph-0.2+-purple.svg" alt="LangGraph">
  <img src="https://img.shields.io/badge/LLM-Llama%203.3-orange.svg" alt="Llama">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
</p>

> *"A research agent that thinks, verifies, and self-corrects."*

## 🎯 What is AutoScholar?

AutoScholar is an AI Research Agent that doesn't just generate answers—it verifies them. Unlike simple chatbots, AutoScholar plans research strategy, searches multiple sources, writes detailed reports, and self-corrects when it finds mistakes.

## 🏗️ Architecture

User Query → Planner (breaks into sub-queries) → Executor (searches via Tavily) → Writer (synthesizes report) → Critic (checks faithfulness) → VALID? → YES → END | NO → Replan (new search) → Executor (loop)

Key Innovation: The Critic uses NLI-based verification to check if every claim is supported by evidence.


**Key Innovation:** The Critic uses **NLI-based verification** to check if every claim is supported by evidence.

---

## 📊 Results

| Query Type | Result | Self-Correction |
|------------|--------|-----------------|
| Simple factual (NVIDIA, TSMC) | ✅ Faithful (95%) | Not needed |
| Complex multi-hop (CHIPS Act, GPU impact) | ⚠️ Gap detected | 2 iterations each |

**Key Metrics:**
- **Self-Correction Rate:** 50% (triggered on complex queries)
- **Average Iterations:** 1.0 per query
- **Simple Query Faithfulness:** 95%
- **Complex Query Resolution:** Resolved via self-correction

---

## 🔧 Installation

pip install langgraph langchain-groq tavily-python pandas pydantic python-dotenv

Required API Keys:

Groq: console.groq.com (100K tokens/day free)
Tavily: tavily.com (1000 searches/month free)

Set Environment Variables:
export GROQ_API_KEY="your_groq_key_here"
export TAVILY_API_KEY="your_tavily_key_here"

## 🚀 Usage

python research_agent.py

It will ask for your query. Type anything!

## 🛠️ Tech Stack
┌────────────────────┬─────────────────────────┐
│ Component          │ Technology              │
├────────────────────┼─────────────────────────┤
│ LLM                │ Llama 3.3 (Groq)        │
│ Orchestration      │ LangGraph               │
│ Search             │ Tavily AI               │
│ State Management   │ TypedDict               │
│ Verification       │ Custom NLI-based Critic │
└────────────────────┴─────────────────────────┘
## 📁 Project Structure

DeepResearchAgent/
├── research_agent.py (Main Agent Code)
├── requirements.txt (Python dependencies)
└── README.md (This file)


## 📄 Research Proposal

Symmetric Self-Reflective Architectures for Verifiable Deep Research

The Problem:
- LLMs hallucinate claims not supported by evidence
- Simple RAG systems cannot self-correct
- Multi-hop queries require iterative refinement

Proposed Solution:
- Bidirectional Loop: Writer → Critic → Replan → Executor
- NLI-based Verification: Mathematical claim-evidence entailment
- Self-Correction: Automatic re-research when gaps detected

Inspiration: Self-RAG (Asai et al., 2024), ReAct (Yao et al., 2023), CRAG

## 🔬 Technical Highlights

Agentic Pipeline:
Planner → Executor → Writer → Critic → Replan
                                    ↓
                            Loop back to Executor
                                    ↓
                                END


State Machine:
AgentState {
    query: str
    plan: List[str]
    research_data: Dict[str, str]
    final_answer: str
    critique: str
    is_valid: bool
    iteration_count: int
}


Conditional Routing:
If is_valid = True → END
If is_valid = False → Re-search
Max iterations: 2

⭐ Star this repo if you found it useful!

