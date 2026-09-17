"""
Deep Thinking Trading System — entry point.
"""

#============================================================================
#                                Import Statements
#============================================================================

import argparse
import datetime

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

from trading_agents.llm import build_llms
from trading_agents.tools.toolkit import build_toolkit
from trading_agents.memory.financial_memory import build_memories
from trading_agents.state import make_initial_state
from trading_agents.graph.setup import build_graph, save_graph_visualization
from trading_agents.eval.single_processor import SignalProcessor
from trading_agents.eval.reflector import Reflector
from trading_agents.eval.ground_truth import evaluate_ground_truth
from trading_agents.eval.judge import run_judge
from trading_agents.eval.auditor import run_market_report_audit
from trading_agents.config import MAX_RECUR_LIMIT

console = Console()

#============================================================================
#                                Main logic Statements
#============================================================================

def parse_args():
    parser = argparse.ArgumentParser(description="Run the Deep Thinking Trading System.")
    parser.add_argument("--ticker", default="NVDA", help="Ticker symbol to analyze.")
    parser.add_argument(
        "--date",
        default=None,
        help="Trade date in YYYY-MM-DD. Defaults to 2 days ago.",
    )
    parser.add_argument(
        "--skip-eval",
        action="store_true",
        help="Skip the Part 8 evaluation suite (judge / ground truth / audit).",
    )
    parser.add_argument(
        "--skip-reflection",
        action="store_true",
        help="Skip the hypothetical-outcome reflection / memory-learning step.",
    )
    parser.add_argument(
        "--graph-image",
        default=None,
        help="If set, saves a PNG of the compiled graph to this path (requires pygraphviz).",
    )
    return parser.parse_args()


def main():
    load_dotenv()  # pull keys from a local .env file if present
    args = parse_args()

    ticker = args.ticker.upper()
    trade_date = args.date or (datetime.date.today() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")

    # --- 1. Setup ---
    deep_thinking_llm, quick_thinking_llm = build_llms()
    toolkit = build_toolkit()
    memories = build_memories()

    # --- 2. Build + compile the graph ---
    trading_graph, _ = build_graph(deep_thinking_llm, quick_thinking_llm, toolkit, memories)
    if args.graph_image:
        save_graph_visualization(trading_graph, args.graph_image)

    # --- 3. Run the full pipeline ---
    console.print(f"[bold]Running full analysis for {ticker} on {trade_date}[/bold]")
    graph_input = make_initial_state(ticker, trade_date)
    graph_config = {"recursion_limit": MAX_RECUR_LIMIT}

    final_state = None
    console.print("--- Invoking Graph Stream ---")
    for chunk in trading_graph.stream(graph_input, config=graph_config):
        node_name = list(chunk.keys())[0]
        console.print(f"Executing Node: {node_name}")
        final_state = chunk[node_name]
    console.print("--- Graph Stream Finished ---\n")

    if final_state is None or "final_trade_decision" not in final_state:
        console.print("[red]Graph did not produce a final decision. Check the trace above for errors.[/red]")
        return

    console.print("----- Final Portfolio Manager Decision -----")
    console.print(Markdown(final_state["final_trade_decision"]))

    # --- 4. Extract a clean BUY/SELL/HOLD signal ---
    signal_processor = SignalProcessor(quick_thinking_llm)
    final_signal = signal_processor.process_signal(final_state["final_trade_decision"])
    console.print(f"\n[bold]Extracted Signal:[/bold] {final_signal}")

    # --- 5. (Optional) Simulate the learning loop ---
    if not args.skip_reflection:
        console.print("\nSimulating reflection based on a hypothetical profit of $1000...")
        reflector = Reflector(quick_thinking_llm)
        hypothetical_returns = 1000
        reflector.reflect(final_state, hypothetical_returns, memories["bull_memory"], lambda s: s["investment_debate_state"]["bull_history"])
        reflector.reflect(final_state, hypothetical_returns, memories["bear_memory"], lambda s: s["investment_debate_state"]["bear_history"])
        reflector.reflect(final_state, hypothetical_returns, memories["trader_memory"], lambda s: s["trader_investment_plan"])
        reflector.reflect(final_state, hypothetical_returns, memories["risk_manager_memory"], lambda s: s["final_trade_decision"])
        console.print("Agent memories updated successfully.")

    # --- 6. (Optional) Run the evaluation suite ---
    if not args.skip_eval:
        console.print("\n----- LLM-as-a-Judge Evaluation -----")
        evaluation = run_judge(deep_thinking_llm, final_state)
        console.print(evaluation.model_dump())

        console.print("\n----- Ground Truth Evaluation -----")
        console.print(evaluate_ground_truth(ticker, trade_date, final_signal))

        console.print("\n----- Factual Consistency Audit (Market Report) -----")
        audit = run_market_report_audit(deep_thinking_llm, toolkit, ticker, trade_date, final_state["market_report"])
        console.print(audit.model_dump())


if __name__ == "__main__":
    main()
