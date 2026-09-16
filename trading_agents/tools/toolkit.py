"""
    Live data tools used by the analyst agents.
"""


#============================================================================
#                                Import Statements
#============================================================================

import os 
from typing_extensions import Annotated
import yfinance as yf
import finnhub
from langchain_core.tools import tool 
from langchain_tavily import TavilySearch
from stockstats import wrap as stockstats_wrap 
from config import FINNHUB_API_KEY, TAVILY_API_KEY

# Setting up the env key
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
os.environ['FINNHUB_API_KEY'] = FINNHUB_API_KEY

#============================================================================
#                                Tool Statements
#============================================================================

@tool 
def get_yfinance_data(
    symbol : Annotated[str , "ticker symbol of the company"],
    start_date : Annotated[str , "Start date in yyyy-mm-dd format"],
    end_date : Annotated[str , "End date in yyyy-mm-dd format"]
    ) -> str :
    """
        Retrieve the stock price data for a give ticker symbol from Yahoo Finance.
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        data = ticker.history(start = start_date , end=end_date)
        if data.empty:
            return f"No data found for symbol {symbol} between {start_date} and {end_date}"
        return data.to_csv()
    except Exception as e:
        return f"Error fetching Yahoo finance data : {e}"


@tool 
def get_technical_indicators(
    symbol : Annotated[str , "ticker symbol for the company"],
    start_date : Annotated[str , "start date in yyyy-mm-dd format"],
    end_date : Annotated[str , "end date in yyyy-mm-dd format"]
) -> str:
    """
        Retrieve key technical indicators for a stock using the stockstats library.
    """
    try:
        df = yf.download(symbol , start=start_date , end=end_date , progress=False)
        if df.empty:
            return "No data found for this symbol"
        stock_df = stockstats_wrap(df)
        indicators = stock_df[
            ["macd" , "rsi_14" , "boll" , "boll_ub" , "boll_lb" , "close_50_sma" , "close_200_sma"]
        ]
        return indicators.tail().to_csv()
    except Exception as e:
        return f"Error calculating stockstats indicators : {e}"


@tool 
def get_finnhub_news(ticker : str , start_date : str , end_date : str) -> str:
    """
        Get company news from Finnhub within a date range.
    """
    try:
        finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
        news_list = finnhub_client.company_news(ticker , _from = start_date , to = end_date)
        news_items = []
        for news in news_list[:5]:
            news_items.append(f"Headline : {news['headline']}\nSummary: {news['summary']}")
        return "\n\n".join(news_items) if news_items else "No Finnhub news found."
    except Exception as e:
        return f"Error fetching Finnhub news: {e}"

_tavily_tool = TavilySearch(max_results=3, tavily_api_key=TAVILY_API_KEY)

@tool 
def get_social_media_sentiment(ticker : str , trade_date : str) -> str:
    """
        Performs a live web search for social media sentiment regarding a stock.
    """
    query = f"Social media sentiment and discussion for {ticker} stock around {trade_date}"
    return str(_tavily_tool.invoke({"query" : query}))

@tool
def get_fundamental_analysiz(ticker : str , trade_date : str) -> str:
    """
        Perform a live web search for recent fundamental analysis of a stock
    """
    query = f"fundamental analysis and key financial metrics for {ticker} stock published around {trade_date}"
    return str(_tavily_tool.invoke({"query" : query}))

@tool 
def get_macroeconomic_news(trade_date : str) -> str:
    """
        Performs a live web search for macroeconomics news relevant to the stock market
    """
    query = f"macroeconomic news and market trends affecting the stock market on {trade_date}"
    return str(_tavily_tool.invoke({"query" : query}))


class Toolkit:
    """
        Groups all live-data tools behind a single, easy to pass around object
    """
    def __init__(self):
        self.get_yfinance_data = get_yfinance_data
        self.get_technical_indicators = get_technical_indicators
        self.get_finnhub_news = get_finnhub_news
        self.get_social_media_sentiment = get_social_media_sentiment
        self.get_fundamental_analysis = get_fundamental_analysiz()
        self.get_macroeconomic_news = get_macroeconomic_news

    def all_tools(self) -> list:
        """
            Return every tool in the toolkit as a flat list.
        """
        return [
            self.get_yfinance_data,
            self.get_technical_indicators,
            self.get_finnhub_news,
            self.get_social_media_sentiment,
            self.get_fundamental_analysis,
            self.get_macroeconomic_news
        ]

def build_toolkit() -> Toolkit:
    return Toolkit()