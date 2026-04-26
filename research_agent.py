
# DEEP RESEARCH AGENT
import os
from typing import List, Dict, TypedDict
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from typing import List as TList
from tavily import TavilyClient
from langgraph.graph import StateGraph, START, END

# Check API keys
if "GROQ_API_KEY" not in os.environ:
    os.environ["GROQ_API_KEY"] = input("Enter Groq API Key: ")
if "TAVILY_API_KEY" not in os.environ:
    os.environ["TAVILY_API_KEY"] = input("Enter Tavily API Key: ")


# STATE
class AgentState(TypedDict):
    query: str
    plan: List[str]
    reasoning: str
    research_data: Dict[str, str]
    final_answer: str
    critique: str
    is_valid: bool
    iteration_count: int

# LLM
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# PLANNER
class ResearchPlan(BaseModel):
    steps: TList[str] = Field(description="Search queries")
    reasoning: str = Field(description="Logic behind plan")

planner_llm = llm.with_structured_output(ResearchPlan)

def research_planner(state: AgentState):
    response = planner_llm.invoke([
        SystemMessage(content="Break down queries into 3-5 sub-queries."),
        HumanMessage(content=f"Query: {state['query']}")
    ])
    print(f"Plan: {len(response.steps)} steps")
    return {"plan": response.steps, "reasoning": response.reasoning}


# EXECUTOR
def research_executor(state: AgentState):
    tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    results = {}

    for i, step in enumerate(state['plan'], 1):
        print(f"  Search [{i}/{len(state['plan'])}]")
        try:
            search_result = tavily.search(query=step, search_depth="advanced", max_results=3)
            content = "\n".join([r['content'] for r in search_result['results']])
            results[step] = content
        except Exception as e:
            print(f"  Error: {e}")
            results[step] = "Search failed"
    return {"research_data": results}

# WRITER
def research_writer(state: AgentState):
    data_context = "\n\n".join([f"=== {k} ===\n{v}" for k, v in state['research_data'].items()])

    prompt = f"""Write a comprehensive research report for:
QUERY: {state['query']}

DATA:
{data_context}

Rules:
- Use ONLY the provided data
- Cite sources inline like [1], [2]
- Be detailed with headers"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {"final_answer": response.content}

# CRITIC
def faithfulness_critic(state: AgentState):
    data_context = "\n\n".join([f"=== {k} ===\n{v}" for k, v in state['research_data'].items()])

    prompt = f"""Fact-checker. Answer with ONE WORD only:
- If answer is 100% faithful to data: Write "VALID"
- If any gaps: Write "INVALID"

QUERY: {state['query']}
DATA: {data_context}
ANSWER: {state['final_answer']}

OUTPUT (ONE WORD ONLY):"""

    response = llm.invoke([HumanMessage(content=prompt)])
    response_text = response.content.strip().upper()

    is_valid = (response_text == "VALID")

    if is_valid:
        print("VALID")
    else:
        print("INVALID")

    return {"critique": response.content, "is_valid": is_valid}

# REPLAN (FIXED - Returns dict, not "END")
def replan_node(state: AgentState):
    if state['is_valid']:
        print(" Valid. Done.")
        return {}  # FIXED: Return empty dict, not "END"

    print(" Gaps found. Creating correction plan...")

    prompt = f"""Fill gaps: {state['critique']}
Generate EXACTLY 2 search queries (one per line)."""

    response = llm.invoke([HumanMessage(content=prompt)])

    lines = [line.strip() for line in response.content.split('\n') if line.strip()]
    new_queries = [line for line in lines if line and not line.startswith('#')]

    print(f"New plan: {len(new_queries[:2])} queries")

    return {
        "plan": new_queries[:2],
        "iteration_count": state['iteration_count'] + 1
    }


# BUILD GRAPH 
def create_agent():
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("planner", research_planner)
    graph.add_node("executor", research_executor)
    graph.add_node("writer", research_writer)
    graph.add_node("critic", faithfulness_critic)
    graph.add_node("replan", replan_node)

    # Edges
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "executor")
    graph.add_edge("executor", "writer")
    graph.add_edge("writer", "critic")
    graph.add_edge("critic", "replan")

    # FIXED: Conditional edge that ROUTES to END or executor
    def should_continue(state):
        if state['iteration_count'] >= 2:
            print("Max iterations. Ending.")
            return "END"
        if state['is_valid']:
            print("Valid. Ending.")
            return "END"
        print("Self-correcting...")
        return "executor"

    graph.add_conditional_edges("replan", should_continue, {
        "END": END,
        "executor": "executor"
    })

    return graph.compile()

research_agent = create_agent()
print("Agent compiled!")

def run_research(query: str):
    initial_state = {
        "query": query,
        "plan": [],
        "reasoning": "",
        "research_data": {},
        "final_answer": "",
        "critique": "",
        "is_valid": False,
        "iteration_count": 0
    }
    return research_agent.invoke(initial_state)

# MAIN FUNCTION:
if __name__ == "__main__":
    query = input("Enter research query: ")
    result = run_research(query)
    print("\n" + "="*50)
    print("FINAL REPORT:")
    print("="*50)
    print(result['final_answer'])


