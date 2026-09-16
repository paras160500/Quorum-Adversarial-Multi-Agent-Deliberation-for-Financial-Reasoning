#============================================================================
#                                Import Statements
#============================================================================

from typing_extensions import TypedDict
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage

#============================================================================
#                                 Class Statements
#============================================================================

class InvestDebateState(TypedDict):
    """
        State for the Bull vs. Bear researcher debate.
    """
    bull_history : str 
    bear_history : str 
    history : str 
    current_response : str 
    judge_decision : str 
    count : int 


class RiskDebateState(TypedDict):
    """
        State for the Risky / Safe / Neutral risk-management debate.
    """
    risky_histroy : str 
    safe_history : str 
    neutral_history : str 
    history : str 
    latest_speaker : str 
    current_risky_response : str 
    current_safe_response : str 
    current_neutral_response : str 
    judge_decision : str 
    count : int 


class AgentState(MessagesState):
    """
        The main state object passed through the entire graph
    """
    company_of_interest : str 
    trade_date : str 
    sender : str 
    market_report : str 
    sentiment_report : str 
    news_report : str 
    fundamentals_report : str 
    investment_debate_state : InvestDebateState
    investment_plan : str 
    trader_investment_plan : str 
    risk_debate_state : RiskDebateState
    final_trade_decision : str 

def make_initial_state(ticker : str , trade_date : str) -> AgentState:
    """
        Build a fresh, Agentstate for a new run
    """
    return AgentState(
        messages=[HumanMessage(content = f"Analyze {ticker} for trading on {trade_date}")],
        company_of_interest=ticker,
        trade_date=trade_date,
        investment_debate_state=InvestDebateState(
            history="",
            current_response="",
            count=0,
            bull_history="",
            bear_history="",
            judge_decision=""
        ),
        risk_debate_state=RiskDebateState(
            history="",
            latest_speaker="",
            current_risky_response="",
            current_safe_response="",
            current_neutral_response="",
            count=0,
            risky_histroy="",
            safe_history="",
            neutral_history="",
            judge_decision=""
        )
    )