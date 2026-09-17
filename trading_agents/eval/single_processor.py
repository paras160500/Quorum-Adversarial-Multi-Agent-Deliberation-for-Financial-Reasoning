"""
Parses the Portfolio Manager's free-text decision into a clean BUY/SELL/HOLD
"""

class SignalProcessor:
    def __init__(self, llm):
        self.llm = llm

    def process_signal(self, full_signal: str) -> str:
        messages = [
            (
                "system",
                "You are an assistant designed to extract the final investment decision: SELL, "
                "BUY, or HOLD from a financial report. Respond with only the single-word decision.",
            ),
            ("human", full_signal),
        ]
        result = self.llm.invoke(messages).content.strip().upper()
        if result in ["BUY", "SELL", "HOLD"]:
            return result
        return "ERROR_UNPARSABLE_SIGNAL"