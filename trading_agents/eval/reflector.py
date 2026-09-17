"""
The learning loop: reflects on a trade's outcome and writes a lesson into
an agent's long-term memory. Originally notebook cell 7.1 (part 2).
"""

from trading_agents.memory.financial_memory import FinancialSituationMemory


class Reflector:
    def __init__(self, llm):
        self.llm = llm
        self.reflection_prompt = """You are an expert financial analyst. Review the trading decision/analysis, the market context, and the financial outcome.
        - First, determine if the decision was correct or incorrect based on the outcome.
        - Analyze the most critical factors that led to the success or failure.
        - Finally, formulate a concise, one-sentence lesson or heuristic that can be used to improve future decisions in similar situations.

        Market Context & Analysis: {situation}
        Outcome (Profit/Loss): {returns_losses}"""

    def reflect(self, current_state, returns_losses, memory: FinancialSituationMemory, component_key_func):
        """component_key_func: a callable extracting the text to reflect on from current_state."""
        situation = (
            f"Reports: {current_state['market_report']} {current_state['sentiment_report']} "
            f"{current_state['news_report']} {current_state['fundamentals_report']}\n"
            f"Decision/Analysis Text: {component_key_func(current_state)}"
        )
        prompt = self.reflection_prompt.format(situation=situation, returns_losses=returns_losses)
        result = self.llm.invoke(prompt).content
        memory.add_situations([(situation, result)])
