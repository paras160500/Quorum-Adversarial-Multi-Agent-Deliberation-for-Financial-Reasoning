"""Premium Quorum command center.

Run with: streamlit run streamlit_app.py
"""
from __future__ import annotations

import datetime as dt
import html
import time
from dataclasses import dataclass
from typing import Any

import streamlit as st

st.set_page_config(page_title="Quorum · Intelligence Command Center", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")

st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root{--ink:#071523;--muted:#7890a2;--faint:#aebfca;--line:#d9e7ed;--blue:#1d73f8;--cyan:#11c8cc;--green:#16c596;--bg:#f6fafc}
.stApp{background:radial-gradient(ellipse at 80% -10%,#c9f8f4 0,transparent 34%),radial-gradient(ellipse at 0% 60%,#dfeaff 0,transparent 28%),linear-gradient(135deg,#fbfdfe 0%,#f0f7fa 100%);color:var(--ink);font-family:'Manrope',sans-serif}
[data-testid=stHeader]{background:transparent}.block-container{max-width:1520px;padding:1.05rem 3.8rem 2.5rem}footer{display:none}.stApp{overflow-x:hidden}
.topbar{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #d7e5eb;padding:.35rem 0 .8rem;margin-bottom:1.25rem}.brand{display:flex;align-items:center;gap:.72rem}.mark{width:34px;height:34px;display:grid;place-items:center;border-radius:11px;color:white;font-size:18px;font-weight:800;background:linear-gradient(135deg,#156df4,#0fc8bb);box-shadow:0 10px 28px #1d73f845}.brand-name{font-family:'Space Grotesk';font-size:1.12rem;font-weight:700;letter-spacing:-.06em}.brand-sub{font:500 .54rem 'DM Mono';color:var(--muted);letter-spacing:.13em;text-transform:uppercase}.network{font:500 .6rem 'DM Mono';color:#168d78;display:flex;align-items:center;gap:.5rem}.network i,.live-dot{display:inline-block;width:7px;height:7px;background:#14c398;border-radius:50%;box-shadow:0 0 0 5px #14c3981c;animation:heartbeat 1.6s ease-in-out infinite}.hero{position:relative;overflow:hidden;display:flex;justify-content:space-between;min-height:190px;padding:1.8rem 2.4rem;border-radius:26px;border:1px solid #d4e9ef;background:linear-gradient(115deg,#fff 0%,#f2fcff 58%,#e6faf8 100%);box-shadow:0 20px 55px #3d718b18}.hero:before{content:'';position:absolute;right:4%;top:-65%;width:360px;height:360px;border:1px solid #12c8cc42;border-radius:50%;box-shadow:0 0 0 22px #12c8cc0f,0 0 0 44px #12c8cc08}.hero:after{content:'◈';position:absolute;right:10%;top:12%;font-size:7rem;color:#0fc8bb13;font-weight:800}.eyebrow{position:relative;z-index:1;color:#1474e9;font:500 .62rem 'DM Mono';letter-spacing:.16em;text-transform:uppercase}.hero h1{position:relative;z-index:1;font-family:'Space Grotesk';font-size:clamp(2rem,4vw,3.7rem);line-height:.94;letter-spacing:-.09em;margin:.5rem 0 .7rem;max-width:780px}.hero h1 span{color:#1975f6}.hero p{position:relative;z-index:1;max-width:610px;color:#668091;font-size:.82rem;line-height:1.55;margin:0}.run-chip{position:relative;z-index:1;align-self:flex-end;display:flex;align-items:center;gap:.65rem;border:1px solid #b9e8e2;background:#effcf9;padding:.6rem .8rem;border-radius:999px;color:#147967;font:500 .62rem 'DM Mono'}
.section{margin-top:1.35rem}.section-head{display:flex;justify-content:space-between;align-items:end;margin-bottom:.55rem}.section-kicker{color:#247ef1;font:500 .6rem 'DM Mono';letter-spacing:.16em;text-transform:uppercase}.section-title{font-family:'Space Grotesk';font-size:1.3rem;letter-spacing:-.06em;font-weight:700;margin:.12rem 0 0}.hint{color:var(--muted);font-size:.7rem}
.ticker-card{border:1px solid var(--line);border-radius:22px;background:#ffffffb8;padding:1.1rem;box-shadow:0 13px 35px #517b8d0c}.ticker-card label{display:block;color:var(--muted);font:500 .61rem 'DM Mono';letter-spacing:.12em;text-transform:uppercase;margin-bottom:.5rem}.ticker-card button{height:38px!important;border:1px solid #d7e5eb!important;background:linear-gradient(180deg,#fff,#f5f9fb)!important;color:#294052!important;border-radius:11px!important;font-family:'Space Grotesk'!important;font-size:.66rem!important;font-weight:700!important;line-height:1.15!important;box-shadow:0 3px 0 #d7e5eb!important;transition:all .18s ease!important}.ticker-card button:hover{border-color:#4b9bff!important;color:#176ee5!important;transform:translateY(-2px)!important;box-shadow:0 6px 12px #1d73f81c!important}.ticker-selected{height:38px;display:flex;flex-direction:column;justify-content:center;align-items:center;border-radius:11px;position:relative;background:linear-gradient(135deg,#f0f8ff,#e9fff9);color:#0869db;font-family:'Space Grotesk';font-size:.66rem;font-weight:700;line-height:1.15;box-shadow:0 0 0 1px #fff inset,0 5px 0 #a8d8ee,0 0 18px #43a8f844;isolation:isolate}.ticker-selected:before{content:'';position:absolute;inset:-2px;border-radius:13px;padding:2px;background:linear-gradient(115deg,#55a8ff,#a18cff,#43dfc0,#55a8ff);background-size:260% 260%;animation:borderFlow 3.2s linear infinite;z-index:-1}.ticker-selected:after{content:'';position:absolute;inset:0;border-radius:11px;background:linear-gradient(105deg,transparent 25%,#ffffffaa 50%,transparent 75%);background-size:220% 100%;animation:selectedShine 3.6s ease-in-out infinite;pointer-events:none}.ticker-selected span{position:relative;z-index:1}.custom-input{display:flex;gap:.7rem;align-items:end;margin-top:.7rem}.custom-input [data-testid=stTextInput]{flex:1}.stTextInput input{height:40px;border-radius:12px!important;border:1px solid #cfe0e8!important;background:#fff!important;font-family:'Space Grotesk'!important;font-size:.92rem!important;font-weight:600!important;letter-spacing:.03em!important;box-shadow:inset 0 1px 2px #0c32400b!important}.stTextInput input:focus{border-color:#3e91ff!important;box-shadow:0 0 0 4px #3e91ff1d!important}.stTextInput label{display:none}
.ticker-card button[aria-label^="◆"],button[aria-label^="◆"]{background:linear-gradient(135deg,#e3f1ff 0%,#d9fbf3 100%)!important;color:#0869db!important;border:1px solid #4da1fa!important;box-shadow:0 0 0 3px #4da1fa26,0 5px 0 #8ac6ef!important}
.option-row{display:flex;gap:.6rem;align-items:center;margin-top:.75rem;padding:.55rem .8rem;border:1px solid #dbeaf0;border-radius:14px;background:linear-gradient(105deg,#ffffffcc,#f0fbfbcc);box-shadow:0 6px 18px #5382960c}.switch-label{color:var(--muted);font:500 .65rem 'DM Mono';text-transform:uppercase;letter-spacing:.08em}.stCheckbox label,.stToggle label{font-size:.7rem!important;color:#527083!important;font-weight:600!important}.stCheckbox,.stToggle{padding:0!important}.stToggle [role="switch"][aria-checked="true"]{background:#2cbfae!important;box-shadow:0 0 0 3px #2cbfae22!important}.launch button,button[aria-label*="Launch"],[data-testid="stBaseButton-primary"] button,button[kind="primary"]{height:56px!important;border:1px solid #73c9e8!important;border-radius:17px!important;color:#075b9d!important;font-family:'Space Grotesk'!important;font-size:1rem!important;font-weight:800!important;letter-spacing:-.02em!important;background:linear-gradient(110deg,#c7efff 0%,#dce8ff 28%,#d5fff2 58%,#bdefff 100%)!important;background-size:260% 100%!important;box-shadow:0 10px 22px #3aaed64a,0 0 0 4px #b8f1ff66,0 3px 0 #82cfe5!important;animation:ctaFlow 4.2s ease-in-out infinite!important;transition:all .2s ease!important;position:relative;overflow:hidden}.launch button:after,button[aria-label*="Launch"]:after,[data-testid="stBaseButton-primary"] button:after,button[kind="primary"]:after{content:'';position:absolute;inset:0;background:linear-gradient(105deg,transparent 25%,#ffffffc9 48%,transparent 72%);background-size:220% 100%;animation:ctaShine 3.4s ease-in-out infinite;pointer-events:none}.launch button:hover,button[aria-label*="Launch"]:hover,[data-testid="stBaseButton-primary"] button:hover,button[kind="primary"]:hover{color:#034b83!important;transform:translateY(-3px)!important;box-shadow:0 16px 30px #36a9da5c,0 0 0 5px #bdeeff88,0 4px 0 #76c5df!important}
.trace-shell{border:1px solid #cfe2ea;border-radius:26px;background:#081a2b;box-shadow:0 22px 55px #132d3d2b;overflow:hidden}.trace-top{display:flex;justify-content:space-between;align-items:center;padding:1rem 1.25rem;border-bottom:1px solid #ffffff14}.trace-title{color:#edfaff;font-family:'Space Grotesk';font-size:.95rem;font-weight:600}.trace-sub{color:#7092a8;font:500 .6rem 'DM Mono';letter-spacing:.1em;text-transform:uppercase}.trace-live{display:flex;align-items:center;gap:.5rem;color:#6ef0c5;font:500 .62rem 'DM Mono';letter-spacing:.08em}.trace-body{padding:1.15rem 1.25rem 1.3rem;max-height:430px;overflow:auto}.trace-body::-webkit-scrollbar{width:4px}.trace-body::-webkit-scrollbar-thumb{background:#31526b;border-radius:4px}.event{position:relative;display:grid;grid-template-columns:23px 1fr auto;gap:.8rem;min-height:59px;padding-bottom:.8rem}.event:not(:last-child):before{content:'';position:absolute;left:10px;top:22px;bottom:0;width:1px;background:#234258}.event-node{position:relative;z-index:1;width:21px;height:21px;display:grid;place-items:center;border-radius:50%;color:#081a2b;background:#5fe7ce;font:700 .59rem 'DM Mono';box-shadow:0 0 0 4px #5fe7ce1c}.event-tool .event-node{background:#8cb8ff}.event-name{color:#e8f6fb;font-size:.78rem;font-weight:700;padding-top:.1rem}.event-desc{color:#7795a7;font-size:.67rem;margin-top:.22rem;line-height:1.35}.event-time{color:#718e9f;font:500 .61rem 'DM Mono';white-space:nowrap}.empty-trace{padding:3rem 1rem;text-align:center;color:#7693a3;font:500 .72rem 'DM Mono';letter-spacing:.05em}.metricbar{display:grid;grid-template-columns:repeat(3,1fr);gap:.7rem;margin-top:.8rem}.dark-metric{border:1px solid #d8e7ed;border-radius:16px;padding:.85rem 1rem;background:#ffffffb8}.dark-metric .label{color:var(--muted);font:500 .59rem 'DM Mono';letter-spacing:.09em}.dark-metric .value{font-family:'Space Grotesk';font-size:1.3rem;font-weight:700;margin-top:.25rem}
.result-card{border:1px solid var(--line);border-radius:23px;background:#ffffffc7;padding:1.25rem;box-shadow:0 14px 40px #52798a10}.decision{border-radius:19px;color:white;padding:1.4rem;background:linear-gradient(135deg,#091b2d,#173e59);box-shadow:0 15px 35px #0c24373b}.decision-label{color:#a7c8d9;font:500 .6rem 'DM Mono';letter-spacing:.12em}.decision-value{font-family:'Space Grotesk';font-size:2.6rem;letter-spacing:-.08em;font-weight:700;margin-top:.35rem}.stat-value{font-family:'Space Grotesk';font-size:1.45rem;font-weight:700;margin-top:.4rem}.stat-label{color:var(--muted);font:500 .59rem 'DM Mono';letter-spacing:.1em}.report{border:1px solid var(--line);border-radius:17px;background:#fff;padding:1.3rem;line-height:1.7;color:#294052}.stTabs [data-baseweb=tab-list]{gap:.4rem;border-bottom:1px solid var(--line)}.stTabs [data-baseweb=tab]{font-size:.72rem;font-weight:700;color:#7890a2}.stTabs [aria-selected=true]{color:#176ff0!important}.stExpander{border:1px solid var(--line)!important;border-radius:15px!important;background:#ffffffb8!important}
@keyframes heartbeat{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.42;transform:scale(.78)}}@keyframes borderFlow{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}@keyframes selectedShine{0%,35%{background-position:220% 0}65%,100%{background-position:-20% 0}}@keyframes ctaFlow{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}@keyframes ctaShine{0%,25%{background-position:220% 0}55%,100%{background-position:-20% 0}}
@media(max-width:850px){.block-container{padding:1.2rem 1rem 3rem}.hero{padding:2rem 1.5rem;min-height:230px}.run-chip{display:none}.hero h1{font-size:2.7rem}.topbar{margin-bottom:1.2rem}.metricbar{grid-template-columns:1fr}.event-time{display:none}}
</style>
""", unsafe_allow_html=True)

TICKERS = [("AAPL","Apple"),("MSFT","Microsoft"),("NVDA","NVIDIA"),("GOOGL","Alphabet"),("AMZN","Amazon"),("META","Meta"),("TSLA","Tesla"),("BRK.B","Berkshire"),("JPM","JPMorgan"),("V","Visa"),("AVGO","Broadcom"),("LLY","Eli Lilly"),("WMT","Walmart"),("XOM","Exxon"),("NFLX","Netflix"),("AMD","AMD"),("COST","Costco"),("CRM","Salesforce"),("ORCL","Oracle"),("INTC","Intel")]
NODE_INFO={"Market Analyst":("MKT","Price action, momentum and volatility"),"Social Analyst":("SOC","Public discussion and crowd signal"),"News Analyst":("NEWS","Company and macroeconomic context"),"Fundamentals Analyst":("FND","Financial health and insider signal"),"Bull Researcher":("BULL","Constructing the upside case"),"Bear Researcher":("BEAR","Stress-testing the downside case"),"Research Manager":("SYN","Turning debate into an investment plan"),"Trader":("TRD","Converting conviction into a trade proposal"),"Risky Analyst":("RISK","High-reward opportunity lens"),"Safe Analyst":("SAFE","Capital-preservation lens"),"Neutral Analyst":("NEU","Balanced risk/reward lens"),"Risk Judge":("FINAL","Binding portfolio decision"),"tools_market":("DATA","Yahoo Finance market data"),"tools_social":("DATA","Web sentiment search"),"tools_news":("DATA","Company and macro news"),"tools_fundamentals":("DATA","Fundamental research search"),"Msg Clear":("SYNC","Preparing next specialist")}
REPORT_FIELDS=[("market_report","Market intelligence"),("sentiment_report","Social sentiment"),("news_report","News intelligence"),("fundamentals_report","Fundamentals")]
@dataclass
class TraceEvent: node:str; started:float; ended:float; detail:str

def esc(x:Any)->str:return html.escape(str(x or ""))
def state_preview(state:dict,node:str)->str:
    keys={"Market Analyst":"market_report","Social Analyst":"sentiment_report","News Analyst":"news_report","Fundamentals Analyst":"fundamentals_report","Research Manager":"investment_plan","Trader":"trader_investment_plan","Risk Judge":"final_trade_decision"}
    value=state.get(keys.get(node,""),"")
    if value:
        text=str(value).replace("\n"," ");return text[:118]+("…" if len(text)>118 else "")
    if node in ("Bull Researcher","Bear Researcher"):return f"Debate round {state.get('investment_debate_state',{}).get('count',0)}"
    if "Analyst" in node:return f"Risk round {state.get('risk_debate_state',{}).get('count',0)}"
    return "State updated"

def event_html(event:TraceEvent)->str:
    code,desc=NODE_INFO.get(event.node,("NODE","State transition")); kind=" event-tool" if event.node.startswith("tools_") else ""
    return f'<div class="event{kind}"><div class="event-node">{esc(code[:4])}</div><div><div class="event-name">{esc(event.node)}</div><div class="event-desc">{esc(desc)} · {esc(event.detail)}</div></div><div class="event-time">{event.ended-event.started:.1f}s</div></div>'

def render_header():
    st.markdown('<div class="topbar"><div class="brand"><div class="mark">◈</div><div><div class="brand-name">QUORUM</div><div class="brand-sub">adversarial financial intelligence</div></div></div><div class="network"><i></i> SYSTEMS NOMINAL · LIVE DATA READY</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="hero"><div><div class="eyebrow">The intelligence command center</div><h1>Decisions built in<br><span>public view.</span></h1><p>Deploy a council of market analysts, adversarial researchers, traders, and risk judges. Watch every state transition as Quorum turns evidence into conviction.</p></div><div class="run-chip"><span class="live-dot"></span> GRAPH OBSERVABILITY ONLINE</div></div>',unsafe_allow_html=True)

def run_analysis(ticker,trade_date,skip_eval,skip_reflection,trace_slot,metric_slot):
    from dotenv import load_dotenv;load_dotenv()
    from trading_agents.config import MAX_RECUR_LIMIT
    from trading_agents.llm import build_llms
    from trading_agents.memory.financial_memory import build_memories
    from trading_agents.state import make_initial_state
    from trading_agents.tools.toolkit import build_toolkit
    from trading_agents.graph.setup import build_graph
    deep_llm,quick_llm=build_llms();toolkit=build_toolkit();memories=build_memories();graph,_=build_graph(deep_llm,quick_llm,toolkit,memories)
    final_state=None;events=[];started_all=time.perf_counter()
    for chunk in graph.stream(make_initial_state(ticker,trade_date),config={"recursion_limit":MAX_RECUR_LIMIT}):
        started=time.perf_counter();node=next(iter(chunk));final_state=chunk[node];ended=time.perf_counter();events.append(TraceEvent(node,started,ended,state_preview(final_state,node)))
        trace_slot.markdown(f'<div class="trace-shell"><div class="trace-top"><div><div class="trace-title">Live graph trace</div><div class="trace-sub">langgraph · state emissions · chronological</div></div><div class="trace-live"><span class="live-dot"></span> EXECUTING · {esc(node.upper())}</div></div><div class="trace-body">{"".join(event_html(e) for e in events)}</div></div>',unsafe_allow_html=True)
        metric_slot.markdown(f'<div class="metricbar"><div class="dark-metric"><div class="label">NODES COMPLETE</div><div class="value">{len(events)} <span style="color:#9fb1bb;font-size:.75rem">/ live</span></div></div><div class="dark-metric"><div class="label">ELAPSED</div><div class="value">{time.perf_counter()-started_all:.0f}<span style="font-size:.75rem">s</span></div></div><div class="dark-metric"><div class="label">ACTIVE PHASE</div><div class="value" style="font-size:.78rem;margin-top:.65rem">{esc(NODE_INFO.get(node,("RUNNING",))[0])}</div></div></div>',unsafe_allow_html=True)
    if not final_state or "final_trade_decision" not in final_state:raise RuntimeError("The graph finished without producing a final portfolio decision.")
    from trading_agents.eval.single_processor import SignalProcessor
    signal=SignalProcessor(quick_llm).process_signal(final_state["final_trade_decision"]);evaluation=None
    if not skip_reflection:
        from trading_agents.eval.reflector import Reflector
        ref=Reflector(quick_llm)
        for key,field in [("bull_memory",lambda s:s["investment_debate_state"]["bull_history"]),("bear_memory",lambda s:s["investment_debate_state"]["bear_history"]),("trader_memory",lambda s:s["trader_investment_plan"]),("risk_manager_memory",lambda s:s["final_trade_decision"])]:ref.reflect(final_state,1000,memories[key],field)
    if not skip_eval:
        from trading_agents.eval.judge import run_judge
        from trading_agents.eval.ground_truth import evaluate_ground_truth
        from trading_agents.eval.auditor import run_market_report_audit
        evaluation={"judge":run_judge(deep_llm,final_state),"ground_truth":evaluate_ground_truth(ticker,trade_date,signal),"audit":run_market_report_audit(deep_llm,toolkit,ticker,trade_date,final_state["market_report"])}
    return {"state":final_state,"signal":signal,"events":events,"evaluation":evaluation,"duration":time.perf_counter()-started_all}

def render_results(result):
    state=result["state"];signal=str(result["signal"]).upper();tone="#16c596" if "BUY" in signal else "#ff806d" if "SELL" in signal else "#f2bd50"
    st.markdown('<div class="section"><div class="section-head"><div><div class="section-kicker">Run output</div><div class="section-title">Conviction snapshot</div></div><div class="hint">Decision synthesized from all live agent states</div></div></div>',unsafe_allow_html=True)
    cols=st.columns([1.35,1,1,1])
    with cols[0]:st.markdown(f'<div class="decision"><div class="decision-label">EXTRACTED SIGNAL</div><div class="decision-value" style="color:{tone}">{esc(signal)}</div><div style="color:#9cb9c9;font-size:.72rem;margin-top:.3rem">Signal processor output</div></div>',unsafe_allow_html=True)
    for col,label,value,sub in [(cols[1],"COVERAGE",len(result["events"]),"real graph emissions"),(cols[2],"RUNTIME",f'{result["duration"]:.0f}s',"end-to-end execution"),(cols[3],"ASSET",state.get("company_of_interest"),state.get("trade_date"))]:
        with col:st.markdown(f'<div class="result-card"><div class="stat-label">{label}</div><div class="stat-value">{esc(value)}</div><div style="color:#7890a2;font-size:.7rem;margin-top:.25rem">{esc(sub)}</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="section"><div class="section-head"><div><div class="section-kicker">Evidence room</div><div class="section-title">Intelligence dossier</div></div><div class="hint">Open a channel to inspect the reasoning</div></div></div>',unsafe_allow_html=True)
    tabs=st.tabs([x[1] for x in REPORT_FIELDS]+["Debate room","Final authority","Evaluation"])
    for tab,(key,title) in zip(tabs[:4],REPORT_FIELDS):
        with tab:
            st.markdown('<div class="report">',unsafe_allow_html=True)
            st.markdown(state.get(key) or "_No report returned._")
            st.markdown('</div>',unsafe_allow_html=True)
    with tabs[4]:
        debate=state.get("investment_debate_state",{});risk=state.get("risk_debate_state",{})
        st.markdown("### Bull case")
        st.markdown(debate.get("bull_history") or "_No bull case returned._")
        st.markdown("### Bear case")
        st.markdown(debate.get("bear_history") or "_No bear case returned._")
        st.markdown("### Risk council")
        st.markdown(f"**Risky lens**\n\n{risk.get('current_risky_response') or '_No response._'}")
        st.markdown(f"**Safe lens**\n\n{risk.get('current_safe_response') or '_No response._'}")
        st.markdown(f"**Neutral lens**\n\n{risk.get('current_neutral_response') or '_No response._'}")
    with tabs[5]:st.markdown(state.get("final_trade_decision","_No final decision returned._"))
    with tabs[6]:
        if result["evaluation"]:
            for name,value in result["evaluation"].items():
                with st.expander(name.replace("_"," ").title()):st.write(value.model_dump() if hasattr(value,"model_dump") else value)
        else:st.info("Evaluation was skipped for this run.")

def main():
    render_header()
    st.markdown('<div class="section"><div class="section-head"><div><div class="section-kicker">Select an asset</div><div class="section-title">Choose your market</div></div><div class="hint">20 curated liquid symbols · analysis date is automatic</div></div></div>',unsafe_allow_html=True)
    if "ticker" not in st.session_state:st.session_state.ticker="AAPL"
    # Render two rows of premium ticker cards.
    for row in [TICKERS[:10],TICKERS[10:]]:
        cols=st.columns(10)
        for col,(symbol,name) in zip(cols,row):
            with col:
                selected = st.session_state.ticker == symbol
                if selected:
                    st.markdown(f'<div class="ticker-selected"><span>◆ {esc(symbol)}</span><span style="font-size:.57rem;color:#4d7895">{esc(name)}</span></div>',unsafe_allow_html=True)
                elif st.button(f"{symbol}\n{name}",key=f"ticker_{symbol}",use_container_width=True):
                    st.session_state.ticker=symbol;st.rerun()
    st.markdown('<div class="custom-input">',unsafe_allow_html=True)
    custom=st.text_input("Custom ticker",value="",placeholder="Or type a symbol · e.g. SHOP, PLTR, COIN",max_chars=8)
    st.markdown('</div>',unsafe_allow_html=True)
    if custom.strip():st.session_state.ticker=custom.strip().upper()
    ticker=st.session_state.ticker
    st.markdown(f'<div style="margin-top:.6rem;margin-bottom:.6rem;color:#547083;font:500 .68rem DM Mono;letter-spacing:.08em">SELECTED ASSET <span style="color:#1674ed;font-size:.85rem">{esc(ticker)}</span> · TRADE DATE <span style="color:#1674ed;font-size:.85rem">{(dt.date.today()-dt.timedelta(days=2)).isoformat()}</span> (AUTO)</div>',unsafe_allow_html=True)
    # st.markdown('<div class="option-row">',unsafe_allow_html=True)
    skip_eval=st.toggle("Skip evaluation suite",value=True);skip_reflection=st.toggle("Skip reflection memory",value=True)
    st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('<div class="launch">',unsafe_allow_html=True)
    run=st.button(f"◈  Launch {ticker} intelligence council",use_container_width=True,type="primary")
    st.markdown('</div>',unsafe_allow_html=True)
    if run:
        trace_slot=st.empty();metric_slot=st.empty();trace_slot.markdown('<div class="trace-shell"><div class="trace-body"><div class="empty-trace"><span class="live-dot"></span><br><br>BOOTING QUORUM COUNCIL · LOADING AGENTS · CONNECTING TO LIVE DATA</div></div></div>',unsafe_allow_html=True)
        try:
            st.session_state.result=run_analysis(ticker,(dt.date.today()-dt.timedelta(days=2)).isoformat(),skip_eval,skip_reflection,trace_slot,metric_slot)
            st.success("Council complete · the dossier is ready below")
        except Exception as exc:st.error(f"Analysis failed: {exc}")
    if "result" in st.session_state:render_results(st.session_state.result)

if __name__=="__main__":main()
