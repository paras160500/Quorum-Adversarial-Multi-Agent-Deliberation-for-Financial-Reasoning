"""
    Researcher team: the bull vs bear investment debat + research manager verdict
"""

#============================================================================
#                                Import Statements
#============================================================================
from trading_agents.memory.financial_memory import FinancialSituationMemory

#============================================================================
#                                Agent Statements
#============================================================================

def create_researcher_node(llm , memory : FinancialSituationMemory , role_prompt : str , agent_name : str):
    def researcher_node(state):
        situation_summary = f"""
        Market Report : {state['market_report']}
        Sentiment Report : {state['sentiment_report']}
        News Report : {state['news_report']}
        Fundamentals Report : {state['fundamentals_report']}
        """
        past_memories = memory.get_memories(situation_summary)
        past_memory_str = "\n".join([mem['recommendation'] for mem in past_memories])

        prompt = f"""
        Here is the current state of the analysis
        {situation_summary}
        Conversation history : {state['investment_debate_state']['history']}
        You opponent's last argument: {state['investment_debate_state']['current_response']}
        Reflections from similar past situations: {past_memory_str or 'No pas memories found'}
        Based on all this information present your argument conversationally.
        """

        response = llm.invoke(prompt)
        argument = f"{agent_name} : {response.content}"

        debate_state = dict(state['investment_debate_state'])
        debate_state['history'] += "\n" + argument
        if agent_name == "Bull Analyst":
            debate_state['bull_history'] += "\n" + argument 
        else:
            debate_state['bear_history'] += "\n" + argument
        debate_state['current_response'] = argument
        debate_state['count'] += 1 
        return {"investment_debate_state" : debate_state}

    return researcher_node


def create_Research_manager(llm , memory : FinancialSituationMemory):
    def resarch_menager_node(state):
        prompt = f"""
        As the Research Manager, your role is to critically evaluate the debate between the bull and bear
        analysis and make a definitive decision. 
        Summarize the key points then provide a clear recommendation: Buy, Sell or Hold. Develop a 
        detailed investment plan for the trader,including your rationale and strategic actions.

        Debate History:
        {state['investment_debate_state']['history']}
        """
        reponse = llm.invoke(prompt)
        return {"investment_plan" : reponse.content}

    return resarch_menager_node


BULL_PROMPT = (
    "You are a Bull Analyst, Your goal is to argue for investing in the stock. Focus on growth "
    "potential, competitive advantages and positive indicators from the reports. Counter the"
    " bear's arguments effectively."
)

BEAR_PROMPT = (
    "you are a Bear Analyst. Your goal is to argue against investing in the stock.Focus on risks, challenges, "
    "and negative indicators, Counter the bulls argument effectively."
)


def build_researcher_nodes(quick_thinking_llm , deep_thinking_llm , memories : dict) -> dict:
    bull_researcher_node = create_researcher_node(
        quick_thinking_llm , memories['bull_memory'] , role_prompt=BULL_PROMPT , agent_name="Bull Analyst",
    )
    bear_researcher_node = create_researcher_node(
        quick_thinking_llm , memories['bear_memory'],role_prompt =  BEAR_PROMPT , agent_name = "Bear Analyst"
    )
    research_manager_node = create_Research_manager(deep_thinking_llm , memories['invest_judge_memory'])

    return {
        "Bull Researcher" : bull_researcher_node,
        "Bear Researcher" : bear_researcher_node,
        "Research Manager" : research_manager_node
    }
