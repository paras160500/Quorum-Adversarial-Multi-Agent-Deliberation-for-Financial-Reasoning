"""
    Assembles the complete LangGraph `StateGraph` wiring every agent together.
"""

#============================================================================
#                                Import Statements
#============================================================================

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from trading_agents.state import AgentState
from trading_agents.tools.toolkit import Toolkit
from trading_agents.agents.analysts import build_analyst_nodes, ANALYST_TOOLS
from trading_agents.agents.researchers import build_researcher_nodes
from trading_agents.agents.trader_risk import build_trader_and_risk_nodes
from trading_agents.graph.conditional_logic import ConditionalLogic, create_msg_delete

# Analyst Sequence
ANALYST_SEQUENCE = [
    ("Market Analyst", "tools_market"),
    ("Social Analyst", "tools_social"),
    ("News Analyst", "tools_news"),
    ("Fundamentals Analyst", "tools_fundamentals"),
]


#============================================================================
#                                Graph Working Statements
#============================================================================

def build_graph(config: dict, deep_thinking_llm, quick_thinking_llm, toolkit: Toolkit, memories: dict):
    """Build and compile the full multi-agent trading graph.

    Returns the compiled graph plus the ConditionalLogic instance (handy for
    tests / introspection).
    """
    analyst_nodes = build_analyst_nodes(quick_thinking_llm, toolkit)
    researcher_nodes = build_researcher_nodes(quick_thinking_llm, deep_thinking_llm, memories)
    trader_risk_nodes = build_trader_and_risk_nodes(quick_thinking_llm, deep_thinking_llm, memories)

    conditional_logic = ConditionalLogic(
        max_debate_rounds=config["max_debate_rounds"],
        max_risk_discuss_rounds=config["max_risk_discuss_rounds"],
    )
    msg_clear_node = create_msg_delete()

    workflow = StateGraph(AgentState)

    # --- Analyst nodes + their own dedicated tool nodes ---
    for analyst_name, tool_node_name in ANALYST_SEQUENCE:
        workflow.add_node(analyst_name, analyst_nodes[analyst_name])
        workflow.add_node(tool_node_name, ToolNode(ANALYST_TOOLS[analyst_name](toolkit)))

    workflow.add_node("Msg Clear", msg_clear_node)

    # --- Researcher nodes ---
    for name in ("Bull Researcher", "Bear Researcher", "Research Manager"):
        workflow.add_node(name, researcher_nodes[name])

    # --- Trader + Risk nodes ---
    for name in ("Trader", "Risky Analyst", "Safe Analyst", "Neutral Analyst", "Risk Judge"):
        workflow.add_node(name, trader_risk_nodes[name])

    # --- Entry point ---
    workflow.set_entry_point("Market Analyst")

    # --- Analyst sequence, each with its own ReAct (tool-call) loop ---
    next_after = {
        "Market Analyst": "Social Analyst",
        "Social Analyst": "News Analyst",
        "News Analyst": "Fundamentals Analyst",
        "Fundamentals Analyst": "Bull Researcher",
    }
    for analyst_name, tool_node_name in ANALYST_SEQUENCE:
        # After the first analyst we insert "Msg Clear" to wipe the previous
        # analyst's tool-call messages so they don't leak into the next one.
        continue_target = "Msg Clear" if analyst_name == "Market Analyst" else next_after[analyst_name]
        workflow.add_conditional_edges(
            analyst_name,
            conditional_logic.should_continue_analyst,
            {"tools": tool_node_name, "continue": continue_target},
        )
        workflow.add_edge(tool_node_name, analyst_name)  # loop back after the tool runs

    workflow.add_edge("Msg Clear", "Social Analyst")

    # --- Research debate loop (Bull <-> Bear -> Research Manager) ---
    workflow.add_conditional_edges(
        "Bull Researcher",
        conditional_logic.should_continue_debate,
        {"Bull Researcher": "Bull Researcher", "Bear Researcher": "Bear Researcher", "Research Manager": "Research Manager"},
    )
    workflow.add_conditional_edges(
        "Bear Researcher",
        conditional_logic.should_continue_debate,
        {"Bull Researcher": "Bull Researcher", "Bear Researcher": "Bear Researcher", "Research Manager": "Research Manager"},
    )
    workflow.add_edge("Research Manager", "Trader")

    # --- Risk debate loop (Risky -> Safe -> Neutral -> ... -> Risk Judge) ---
    workflow.add_edge("Trader", "Risky Analyst")
    risk_targets = {
        "Risky Analyst": "Risky Analyst",
        "Safe Analyst": "Safe Analyst",
        "Neutral Analyst": "Neutral Analyst",
        "Risk Judge": "Risk Judge",
    }
    for name in ("Risky Analyst", "Safe Analyst", "Neutral Analyst"):
        workflow.add_conditional_edges(name, conditional_logic.should_continue_risk_analysis, risk_targets)

    workflow.add_edge("Risk Judge", END)

    trading_graph = workflow.compile()
    return trading_graph, conditional_logic


def save_graph_visualization(trading_graph, output_path: str = "graph.png") -> bool:
    """Best-effort PNG render of the compiled graph (requires pygraphviz)."""
    try:
        png_bytes = trading_graph.get_graph().draw_png()
        with open(output_path, "wb") as f:
            f.write(png_bytes)
        return True
    except Exception as e:
        print(f"Graph visualization failed: {e}. Please ensure pygraphviz is installed.")
        return False
