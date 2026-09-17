"""
Factual-consistency audit: checks whether an analyst's report actually
matches the raw data it was supposed to be based on.
Originally notebook cell 8.3.1.
"""
from datetime import datetime, timedelta

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from trading_agents.tools import Toolkit


class Audit(BaseModel):
    is_consistent: bool = Field(description="Whether the report is factually consistent with the data.")
    discrepancies: list[str] = Field(description="A list of any identified discrepancies.")
    justification: str = Field(description="A brief justification for the audit result.")


_AUDITOR_PROMPT = ChatPromptTemplate.from_template(
    """You are an auditor. Compare the 'Agent Report' against the 'Raw Data' and check for factual consistency.
    Ignore differences in formatting or summarization, but flag any direct contradictions or claims in the report that are not supported by the data.

    Raw Data:
    {raw_data}

    Agent Report to Audit:
    {agent_report}
    """
)


def build_auditor_chain(deep_thinking_llm):
    return _AUDITOR_PROMPT | deep_thinking_llm.with_structured_output(Audit)


def run_market_report_audit(deep_thinking_llm, toolkit: Toolkit, ticker: str, trade_date: str, market_report: str) -> Audit:
    chain = build_auditor_chain(deep_thinking_llm)
    start_date_audit = (datetime.strptime(trade_date, "%Y-%m-%d") - timedelta(days=60)).strftime("%Y-%m-%d")
    raw_market_data = toolkit.get_technical_indicators.invoke(
        {"symbol": ticker, "start_date": start_date_audit, "end_date": trade_date}
    )
    return chain.invoke({"raw_data": raw_market_data, "agent_report": market_report})
