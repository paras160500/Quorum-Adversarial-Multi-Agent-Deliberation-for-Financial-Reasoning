"""
LLM-as-a-Judge evaluation of the final trading decision.
Originally notebook cell 8.1.1.
"""
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate


class Evaluation(BaseModel):
    reasoning_quality: int = Field(description="Score 1-10 on the coherence and logic.")
    evidence_based_score: int = Field(description="Score 1-10 on citation of evidence from reports.")
    actionability_score: int = Field(description="Score 1-10 on how clear and actionable the decision is.")
    justification: str = Field(description="A brief justification for the scores.")


_EVALUATOR_PROMPT = ChatPromptTemplate.from_template(
    """You are an expert financial auditor. Evaluate the 'Final Trading Decision' based on the provided 'Analyst Reports'.
    Analyst Reports:
    {reports}
    Final Trading Decision to Evaluate:
    {final_decision}
    """
)


def build_judge_chain(deep_thinking_llm):
    return _EVALUATOR_PROMPT | deep_thinking_llm.with_structured_output(Evaluation)


def run_judge(deep_thinking_llm, final_state: dict) -> Evaluation:
    chain = build_judge_chain(deep_thinking_llm)
    reports_summary = (
        f"Market: {final_state['market_report']}\n"
        f"Sentiment: {final_state['sentiment_report']}\n"
        f"News: {final_state['news_report']}\n"
        f"Fundamentals: {final_state['fundamentals_report']}"
    )
    return chain.invoke({"reports": reports_summary, "final_decision": final_state["final_trade_decision"]})
