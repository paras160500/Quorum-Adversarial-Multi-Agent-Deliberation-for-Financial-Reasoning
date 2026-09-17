"""
    Trader + Risk management team
"""

#============================================================================
#                                Import Statements
#============================================================================

from trading_agents.memory.financial_memory import FinancialSituationMemory
import functools

#============================================================================
#                                Agent Statements
#============================================================================

def create_traders(llm , memory : FinancialSituationMemory):
    def trader_node(state , name : str):
        prompt = f"""
        You are a trading agent, Based on the provided investment plam create a concise trading 
        proposal. Your response must be end with 'FINAL TRANSACTION PROPOSAL : **BUY/HOLD/SELL**'
        Proposed Investment Plan : {state['investment_plan']}
        """
        result = llm.invoke(prompt)
        return {"trader_investment_plan" : result.content , "sender" : name}
    return trader_node


def create_risk_debator(llm , role_prompt : str , agent_name : str):
    def risk_debator_node(state):
        risk_state = state['risk_debate_state']
        opponents_args = []
        if agent_name != "Risky Analyst" and risk_state['current_risky_response']:
            opponents_args.append(f"Risky : {risk_state['current_risky_response']}")
        if agent_name != "Safe Analyst" and risk_state['current_safe_response']:
            opponents_args.append(f"Risky : {risk_state['current_safe_response']}")
        if agent_name != "Neutral Analyst" and risk_state['current_neutral_response']:
            opponents_args.append(f"Risky : {risk_state['current_neutral_response']}")

        opponents_block = "\n".join(opponents_args)
        prompt = f"""
        {role_prompt}
        Here is the trader's Plan : {state['trader_investment_plan']}
        Debate history : {risk_state['history']}
        Your opponent's last argument : {opponents_block}
        Critique or support the plan from yout perspective.
        """

        response = llm.invoke(prompt).content

        new_risk_state = dict(risk_state)
        new_risk_state['history'] += f"\n{agent_name} : {response}"
        new_risk_state['latest_speaker'] = agent_name
        if agent_name == "Risky Analyst":
            new_risk_state['current_risky_response'] = response 
        elif agent_name == "Safe Analyst":
            new_risk_state['current_safe_response'] = response 
        else:
            new_risk_state['current_neutral_response'] = response 

        new_risk_state['count'] += 1
        return {"risk_debate_state" : new_risk_state}

    return risk_debator_node


def create_risk_manager(llm , memory : FinancialSituationMemory):
    def risk_manager_node(state):
        prompt = f"""
        As the portfolio manager you decision is final. Review the trader's plan and the risk debate
        Provide a final binding decision : Buy, Sell or Hold and a brief justification.

        Traders Plan : {state['trader_investment_plan']}
        Risk Debate : {state['risk_debate_state']['history']}
        """
        response = llm.invoke(prompt).content 
        return {"final_trade_decision" : response}

    return risk_manager_node


RISKY_PROMPT = "You are the Risky Risk Analyst. You advocate for high-reward opportunities and bold strategies."
SAFE_PROMPT = "You are the Safe/Conservative Risk Analyst. You prioritize capital preservation and minimizing volatility."
NEUTRAL_PROMPT = "You are the Neutral Risk Analyst. You provide a balanced perspective, weighing both benefits and risks."


def build_trader_and_risk_nodes(quick_thinking_llm, deep_thinking_llm, memories: dict) -> dict:
    trader_node_func = create_traders(quick_thinking_llm, memories["trader_memory"])
    trader_node = functools.partial(trader_node_func, name="Trader")

    risky_node = create_risk_debator(quick_thinking_llm, RISKY_PROMPT, "Risky Analyst")
    safe_node = create_risk_debator(quick_thinking_llm, SAFE_PROMPT, "Safe Analyst")
    neutral_node = create_risk_debator(quick_thinking_llm, NEUTRAL_PROMPT, "Neutral Analyst")
    risk_manager_node = create_risk_manager(deep_thinking_llm, memories["risk_manager_memory"])

    return {
        "Trader": trader_node,
        "Risky Analyst": risky_node,
        "Safe Analyst": safe_node,
        "Neutral Analyst": neutral_node,
        "Risk Judge": risk_manager_node,
    }
