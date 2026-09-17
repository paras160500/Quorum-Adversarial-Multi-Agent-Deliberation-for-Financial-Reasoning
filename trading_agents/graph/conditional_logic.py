"""
Routing logic for the StateGraph.
"""

#============================================================================
#                                Import Statements
#============================================================================

from langchain_core.messages import HumanMessage, RemoveMessage
from langgraph.prebuilt import tools_condition
from trading_agents.state import AgentState

#============================================================================
#                                Graph Statements
#============================================================================

class ConditionalLogic:
    def __init__(self, max_debate_rounds: int = 1, max_risk_discuss_rounds: int = 1):
        self.max_debate_rounds = max_debate_rounds
        self.max_risk_discuss_rounds = max_risk_discuss_rounds

    def should_continue_analyst(self, state: AgentState) -> str:
        """Route to 'tools' if the analyst's last message was a tool call, else continue."""
        return "tools" if tools_condition(state) == "tools" else "continue"

    def should_continue_debate(self, state: AgentState) -> str:
        """Alternate Bull/Bear until max_debate_rounds is reached, then hand off to the manager."""
        if state["investment_debate_state"]["count"] >= 2 * self.max_debate_rounds:
            return "Research Manager"
        return (
            "Bear Researcher"
            if state["investment_debate_state"]["current_response"].startswith("Bull")
            else "Bull Researcher"
        )

    def should_continue_risk_analysis(self, state: AgentState) -> str:
        """Cycle Risky -> Safe -> Neutral until max_risk_discuss_rounds is reached."""
        if state["risk_debate_state"]["count"] >= 3 * self.max_risk_discuss_rounds:
            return "Risk Judge"
        speaker = state["risk_debate_state"]["latest_speaker"]
        if speaker == "Risky Analyst":
            return "Safe Analyst"
        if speaker == "Safe Analyst":
            return "Neutral Analyst"
        return "Risky Analyst"


def create_msg_delete():
    """Clear accumulated tool-call messages between analysts so context doesn't leak."""

    def delete_messages(state):
        return {
            "messages": [RemoveMessage(id=m.id) for m in state["messages"]]
            + [HumanMessage(content="Continue")]
        }

    return delete_messages