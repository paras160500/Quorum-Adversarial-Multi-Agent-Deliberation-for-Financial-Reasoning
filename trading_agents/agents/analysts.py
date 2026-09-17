"""
    Analyst team : intelligence-gathering agents
"""
#============================================================================
#                                Import Statements
#============================================================================

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from trading_agents.tools.toolkit import Toolkit


#============================================================================
#                                agent Statements
#============================================================================

def create_analyst_node(llm , toolkit : Toolkit , system_message : str , tools : list , output_field : str):
    """
        Build a langgraph node function for one type of analyst
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system" , 
            "You are a helpful AI assistant, collaborating with other assistants."
            "Use the provided tools to progress towards answering the question"
            "If you are unable to fully answer, that's Ok; another assistant with different tools"
            " will help where you left off. Execute what you can to make progress."
            "You have access to the following tools: {tool_names}.\n{system_message}"
            " for your references, the current date is {current_date}. The company we want to look at is {ticker}"
            ),
            MessagesPlaceholder(variable_name="messages")
        ]
    )

    prompt = prompt.partial(system_message = system_message)
    prompt = prompt.partial(tool_names = ", ".join([t.name for t in tools]))
    bound_llm = llm.bind_tools(tools)

    def analyst_node(state):
        prompt_with_data = prompt.partial(
            current_date = state['trade_date'] , ticker=state['company_of_interest']
        )
        chain = prompt_with_data | bound_llm
        result = chain.invoke({"messages" : state['messages']})
        report = ""

        # If the llm didnot call a tool it means it has produced the final report
        if not result.tool_calls:
            report = result.content 
        return {"messages" : [result] , output_field : report}

    return analyst_node


def build_analyst_nodes(quick_thinking_llm, toolkit: Toolkit) -> dict:
    """Instantiate all four analyst nodes and return them keyed by name."""

    market_analyst_system_message = (
        "You are a trading assistant specialized in analyzing financial markets. Your role is to "
        "select the most relevant technical indicators to analyze a stock's price action, momentum, "
        "and volatility. You must use your tools to get historical data and then generate a report "
        "with your findings, including a summary table."
    )
    market_analyst_node = create_analyst_node(
        quick_thinking_llm, toolkit, market_analyst_system_message,
        [toolkit.get_yfinance_data, toolkit.get_technical_indicators],
        "market_report",
    )

    social_analyst_system_message = (
        "You are a social media analyst. Your job is to analyze social media posts and public "
        "sentiment for a specific company over the past week. Use your tools to find relevant "
        "discussions and write a comprehensive report detailing your analysis, insights, and "
        "implications for traders, including a summary table."
    )
    social_analyst_node = create_analyst_node(
        quick_thinking_llm, toolkit, social_analyst_system_message,
        [toolkit.get_social_media_sentiment],
        "sentiment_report",
    )

    news_analyst_system_message = (
        "You are a news researcher analyzing recent news and trends over the past week. Write a "
        "comprehensive report on the current state of the world relevant for trading and "
        "macroeconomics. Use your tools to be comprehensive and provide detailed analysis, "
        "including a summary table."
    )
    news_analyst_node = create_analyst_node(
        quick_thinking_llm, toolkit, news_analyst_system_message,
        [toolkit.get_finnhub_news, toolkit.get_macroeconomic_news],
        "news_report",
    )

    fundamentals_analyst_system_message = (
        "You are a researcher analyzing fundamental information about a company. Write a "
        "comprehensive report on the company's financials, insider sentiment, and transactions to "
        "gain a full view of its fundamental health, including a summary table."
    )
    fundamentals_analyst_node = create_analyst_node(
        quick_thinking_llm, toolkit, fundamentals_analyst_system_message,
        [toolkit.get_fundamental_analysis],
        "fundamentals_report",
    )

    return {
        "Market Analyst": market_analyst_node,
        "Social Analyst": social_analyst_node,
        "News Analyst": news_analyst_node,
        "Fundamentals Analyst": fundamentals_analyst_node,
    }


# Map each analyst node name to the tools it is allowed to call.
# Used by graph/setup.py to give each analyst its own dedicated ToolNode.
ANALYST_TOOLS = {
    "Market Analyst": lambda toolkit: [toolkit.get_yfinance_data, toolkit.get_technical_indicators],
    "Social Analyst": lambda toolkit: [toolkit.get_social_media_sentiment],
    "News Analyst": lambda toolkit: [toolkit.get_finnhub_news, toolkit.get_macroeconomic_news],
    "Fundamentals Analyst": lambda toolkit: [toolkit.get_fundamental_analysis],
}
