"""
S&P 500 Rebalance & Reconstitution Arbitrage Intelligence Platform
Web-based application providing rebalance timeline tracking, candidate addition/deletion
predictions, and point-in-time historical backtest auditing with dataset integrity checks.
"""

import html
import textwrap
from typing import Dict, Any

import pandas as pd
import streamlit as st

from timeline_manager import RebalanceTimelineManager
from sp500_engine import SP500RebalanceEngine
from data_loader import get_current_universe
from historic_evaluator import HistoricArbitrageEvaluator


def _esc(val: Any) -> str:
    """HTML-escapes dynamic text and replaces '$' with '&#36;' so KaTeX never hijacks HTML cards."""
    return html.escape(str(val)).replace("$", "&#36;")


@st.cache_data(ttl=300)
def load_current_universe_cached() -> Dict[str, Any]:
    return get_current_universe()


@st.cache_data(ttl=300)
def load_historical_audit_cached() -> Dict[str, Any]:
    return HistoricArbitrageEvaluator.run_full_historical_audit()


@st.cache_data(ttl=300)
def load_walk_forward_cached() -> Dict[str, Any]:
    return HistoricArbitrageEvaluator.optimize_and_tune_loop(target_rating=9.0)


# --- Page Configuration ---
st.set_page_config(
    page_title="S&P 500 Arbitrage & Reconstitution Engine",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS (Glassmorphism & Institutional Dark Theme) ---
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background-color: #070d18;
        color: #f1f5f9;
    }

    .glass-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 16px;
    }

    .badge-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }

    .metric-title {
        color: #94a3b8;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 900;
        color: #f8fafc;
        line-height: 1.2;
    }
    .metric-sub {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 4px;
    }
</style>
""",
    unsafe_allow_html=True,
)


# --- Rebalance Timeline Header ---
timeline = RebalanceTimelineManager.get_timeline_status()

st.markdown(
    textwrap.dedent(
        f"""
<div style="background: linear-gradient(135deg, #09152b 0%, #11254a 100%); border: 1px solid #1e3a8a; border-radius: 14px; padding: 22px 26px 18px 26px; margin-bottom: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.45);">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 15px;">
        <div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.6rem;">🏛️</span>
                <h1 style="color: #facc15; font-size: 1.55rem; font-weight: 900; margin: 0; letter-spacing: -0.02em;">
                    S&amp;P 500 指数成份股纳调与事件驱动套利雷达
                </h1>
                <span style="background: rgba(250, 204, 21, 0.15); color: #facc15; border: 1px solid #facc15; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 800;">
                    PRO ARB ENGINE
                </span>
            </div>
            <div style="color: #94a3b8; font-size: 0.88rem; margin-top: 6px;">
                S&amp;P Dow Jones Indices 官方规则模型（&#36;22.7B 门槛 / FMC / IWF / 成交量 / 4Q累计+Q0 GAAP）— 点测隔离回测与套利分析
            </div>
        </div>
        <div style="text-align: right; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 8px 16px;">
            <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 600;">下一换仓目标季度 (NYSE ET)</div>
            <div style="font-size: 1.25rem; font-weight: 900; color: #38bdf8;">{_esc(timeline['next_quarter_label'])}</div>
            <div style="font-size: 0.75rem; color: #10b981; font-weight: 700;">生效日: {timeline['effective_date'].strftime('%Y-%m-%d')}</div>
        </div>
    </div>
</div>
"""
    ).strip(),
    unsafe_allow_html=True,
)


# --- Executive Milestone Countdown Bar ---
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    st.markdown(
        textwrap.dedent(
            f"""
    <div class="glass-card" style="border-left: 4px solid {_esc(timeline['stage_color'])};">
        <div class="metric-title">当前换仓周期状态 ({timeline['progress']:.1f}%)</div>
        <div style="font-size: 1.05rem; font-weight: 800; color: {_esc(timeline['stage_color'])}; margin-top: 4px;">
            {_esc(timeline['stage_zh'])}
        </div>
        <div class="metric-sub">{_esc(timeline['stage_desc'])}</div>
    </div>
    """
        ).strip(),
        unsafe_allow_html=True,
    )

with col_m2:
    days_cut = timeline["days_to_cutoff"]
    st.markdown(
        textwrap.dedent(
            f"""
    <div class="glass-card" style="border-left: 4px solid #38bdf8;">
        <div class="metric-title">距数据冻结截止日 (Cutoff)</div>
        <div class="metric-value" style="color: #38bdf8;">{max(0, days_cut)} <span style="font-size: 0.9rem; font-weight: 600; color: #64748b;">天</span></div>
        <div class="metric-sub">截止日: {timeline['cutoff_date'].strftime('%Y年%m月%d日')} (NYSE 月末交易日)</div>
    </div>
    """
        ).strip(),
        unsafe_allow_html=True,
    )

with col_m3:
    days_ann = timeline["days_to_announcement"]
    st.markdown(
        textwrap.dedent(
            f"""
    <div class="glass-card" style="border-left: 4px solid #f59e0b;">
        <div class="metric-title">距官方公告公布日 (1st Friday)</div>
        <div class="metric-value" style="color: #f59e0b;">{max(0, days_ann)} <span style="font-size: 0.9rem; font-weight: 600; color: #64748b;">天</span></div>
        <div class="metric-sub">公告日: {timeline['announcement_date'].strftime('%Y年%m月%d日')} 17:15 ET</div>
    </div>
    """
        ).strip(),
        unsafe_allow_html=True,
    )

with col_m4:
    days_eff = timeline["days_to_effective"]
    st.markdown(
        textwrap.dedent(
            f"""
    <div class="glass-card" style="border-left: 4px solid #10b981;">
        <div class="metric-title">距指数基金生效换仓 (3rd Friday)</div>
        <div class="metric-value" style="color: #10b981;">{max(0, days_eff)} <span style="font-size: 0.9rem; font-weight: 600; color: #64748b;">天</span></div>
        <div class="metric-sub">生效日: {timeline['effective_date'].strftime('%Y年%m月%d日')} ({timeline['trading_days_announcement_to_effective']} 交易日窗口)</div>
    </div>
    """
        ).strip(),
        unsafe_allow_html=True,
    )


# --- Interactive Cycle Progress Indicator ---
st.progress(min(1.0, max(0.0, float(timeline["progress"]) / 100.0)))
st.markdown(
    textwrap.dedent(
        f"""
<div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px 16px; margin-bottom: 24px; display: flex; align-items: center; gap: 16px; font-size: 0.83rem;">
    <div style="white-space: nowrap; color: #94a3b8; font-weight: 700;">💡 套利实战策略指引:</div>
    <div style="color: #e2e8f0;">{_esc(timeline['action_hint'])}</div>
</div>
"""
    ).strip(),
    unsafe_allow_html=True,
)


# --- Tabs Navigation ---
tab_add, tab_del, tab_eval, tab_playbook = st.tabs(
    [
        "🚀 潜在纳入预测名单 (Addition Candidates)",
        "⚠️ 高危剔除预警名单 (Deletion Candidates)",
        "🔬 历史点测回测与独立评估器 (Historic Evaluator Lab)",
        "📈 指数效应与事件驱动套利手册 (Arbitrage Playbook)",
    ]
)


# ==============================================================================
# TAB 1: ADDITION CANDIDATES
# ==============================================================================
with tab_add:
    st.subheader("🎯 标普 500 潜在纳入候选标的筛选与概率评分")
    st.caption(
        "依据 S&P Dow Jones Indices 官方准则（市值门槛 \\$22.7B、FMC >= 50% 门槛、IWF >= 0.10、"
        "过去4季度累计 GAAP 净利润之和 > 0 且最近季度 Q0 > 0、流动性比率 >= 0.75、6个月最低月成交量 >= 25万股、"
        "IPO >= 12个月、S&P MidCap 400 优先池；权重 35/35/15/15）全景测算"
    )

    curr_universe = load_current_universe_cached()
    add_pool = curr_universe["addition_candidates"]

    # Filter Controls (deterministic sorted sector options)
    f_c1, f_c2, f_c3 = st.columns([1.5, 1.5, 2.0])
    with f_c1:
        min_cap = st.slider(
            "最低未调整市值门槛 ($B)",
            min_value=14.0,
            max_value=35.0,
            value=float(SP500RebalanceEngine.DEFAULT_MKT_CAP_THRESHOLD_B),
            step=0.1,
        )
    with f_c2:
        feeder_choice = st.selectbox(
            "成份股来源池筛选",
            [
                "全部来源 (All Pools)",
                "仅限 S&P MidCap 400 (最高概率)",
                "大型非指数股 (Large Non-Index)",
            ],
        )
    with f_c3:
        sector_options = sorted({c["sector"] for c in add_pool})
        sector_filter = st.multiselect("板块过滤 (GICS Sectors)", sector_options, default=[])

    filtered_add = list(add_pool)
    if feeder_choice == "仅限 S&P MidCap 400 (最高概率)":
        filtered_add = [c for c in filtered_add if "MidCap 400" in c.get("feeder", "")]
    elif feeder_choice == "大型非指数股 (Large Non-Index)":
        filtered_add = [c for c in filtered_add if "MidCap 400" not in c.get("feeder", "")]

    if sector_filter:
        filtered_add = [c for c in filtered_add if c["sector"] in sector_filter]

    ranked_add = SP500RebalanceEngine.rank_addition_candidates(
        filtered_add, mkt_cap_threshold_b=min_cap
    )

    # Top 3 Candidate Spotlight (dynamically rendered badges & escaped dollar signs)
    st.markdown("#### 🌟 第一顺位重点候选人 (Top Probability Spotlight)")
    top_3 = [c for c in ranked_add if c["is_eligible"]][:3]

    if not top_3:
        st.info("当前筛选条件下暂无满足全部 S&P 500 准入硬指标的候选标的，请放宽筛选条件。")
    else:
        spot_cols = st.columns(len(top_3))
        for i, cand in enumerate(top_3):
            is_midcap = "MidCap 400" in cand["feeder"]
            feeder_badge = "✅ S&amp;P 400 核心梯队" if is_midcap else "🌐 非指数大型股池"
            liq_val = cand.get("liq_ratio")
            liq_badge = f"✅ 换手 {liq_val:.2f}x" if liq_val is not None else "⚠️ 换手未知"
            gaap_badge = "✅ 4Q累计+Q0 GAAP 盈利" if cand["passed_gaap"] else "❌ GAAP 未达标"
            with spot_cols[i]:
                st.markdown(
                    textwrap.dedent(
                        f"""
                <div style="background: linear-gradient(145deg, #0b1c3d 0%, #0d2757 100%); border: 1px solid #2563eb; border-radius: 12px; padding: 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.3);">
                    <div style="display: flex; justify-content: space-between; align-items: baseline;">
                        <span style="font-size: 1.4rem; font-weight: 900; color: #facc15;">#{cand['rank']} {_esc(cand['ticker'])}</span>
                        <span style="background: rgba(16, 185, 129, 0.2); color: {_esc(cand['prob_color'])}; font-weight: 800; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;">
                            得分: {cand['score']:.1f}
                        </span>
                    </div>
                    <div style="color: #cbd5e1; font-weight: 700; font-size: 0.92rem; margin-top: 2px;">{_esc(cand['name'])}</div>
                    <div style="font-size: 0.78rem; color: #94a3b8; margin-top: 6px;">
                        板块: <b>{_esc(cand['sector'])}</b> | 市值: <b style="color: #38bdf8;">&#36;{cand['mkt_cap_b']:.1f}B</b>
                    </div>
                    <div style="margin-top: 8px; font-size: 0.75rem; color: #e2e8f0; background: rgba(0,0,0,0.25); border-radius: 6px; padding: 6px 10px;">
                        {gaap_badge} | {feeder_badge} | {liq_badge}
                    </div>
                </div>
                """
                    ).strip(),
                    unsafe_allow_html=True,
                )

    st.markdown("<br>", unsafe_allow_html=True)

    # Full Table
    if not ranked_add:
        st.warning("当前筛选条件无匹配标的。")
    else:
        table_data = []
        for c in ranked_add:
            status_str = (
                "✅ 合格 (Eligible)"
                if c["is_eligible"]
                else f"❌ 不合格 ({', '.join(c['fail_reasons'])})"
            )
            table_data.append(
                {
                    "顺位": f"#{c['rank']}",
                    "代码": c["ticker"],
                    "企业名称": c["name"],
                    "所属板块": c["sector"],
                    "市值 ($B)": round(c["mkt_cap_b"], 1),
                    "来源池": c["feeder"],
                    "准入审查状态": status_str,
                    "多因子得分": c["score"],
                    "纳入概率评级": c["prob_label"],
                }
            )

        df_add = pd.DataFrame(table_data)
        st.dataframe(df_add, width="stretch", hide_index=True)


# ==============================================================================
# TAB 2: DELETION CANDIDATES
# ==============================================================================
with tab_del:
    st.subheader("⚠️ 标普 500 成份股高危剔除与并购移除预警")
    st.caption("针对当前标普 500 尾部成份股的市值比例（相对 \\$22.7B 门槛）、标普尾部排名、连续亏损季数及待决并购交易的风险审计")

    del_pool = curr_universe["deletion_candidates"]
    ranked_del = SP500RebalanceEngine.rank_deletion_candidates(del_pool)

    if not ranked_del:
        st.info("当前无剔除风险监控标的。")
    else:
        d_col1, d_col2 = st.columns([1.2, 1.8])

        with d_col1:
            st.markdown("#### 🚨 剔除风险分级洞察")
            for d in ranked_del[:4]:
                st.markdown(
                    textwrap.dedent(
                        f"""
                <div style="background: rgba(30, 41, 59, 0.7); border-left: 4px solid {_esc(d['risk_color'])}; border-radius: 8px; padding: 12px 16px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: baseline;">
                        <b style="color: #f8fafc; font-size: 1.1rem;">#{d['rank']} {_esc(d['ticker'])}</b>
                        <span style="color: {_esc(d['risk_color'])}; font-weight: 800; font-size: 0.8rem;">{_esc(d['risk_label'])} ({d['risk_score']:.1f})</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 2px;">{_esc(d['name'])} · {_esc(d['sector'])} · 市值: &#36;{d['mkt_cap_b']:.1f}B (倒数 #{d['rank_bottom']})</div>
                    <div style="font-size: 0.78rem; color: #cbd5e1; margin-top: 6px;"><b>预警成因:</b> {_esc(d['reason'])}</div>
                </div>
                """
                    ).strip(),
                    unsafe_allow_html=True,
                )

        with d_col2:
            st.markdown("#### 📋 标普 500 剔除风险全量监控列表")
            del_table_data = []
            for d in ranked_del:
                del_table_data.append(
                    {
                        "排名": f"#{d['rank']}",
                        "代码": d["ticker"],
                        "公司名称": d["name"],
                        "板块": d["sector"],
                        "市值 ($B)": round(d["mkt_cap_b"], 1),
                        "尾部排名": f"#{d['rank_bottom']}",
                        "连续亏损季数": f"{d['neg_earnings_streak']} 季" if d["neg_earnings_streak"] > 0 else "无",
                        "并购状态": f"⚠️ 待决 ({d['acquirer']})" if d["ma_pending"] else "无",
                        "剔除风险分": d["risk_score"],
                        "风险评级": d["risk_label"],
                    }
                )
            st.dataframe(pd.DataFrame(del_table_data), width="stretch", hide_index=True)


# ==============================================================================
# TAB 3: HISTORIC EVALUATOR & BACKTEST LAB
# ==============================================================================
with tab_eval:
    st.subheader("🔬 历史点测回测与独立评估器实验室 (Evaluator Lab)")
    st.caption(
        "使用按时代还原的 S&P DJI 市值门槛（\\$14.5B / \\$15.8B / \\$18.0B / \\$20.5B / \\$22.7B）、"
        "数据集成员一致性校验、Precision@K / MRR 与扩展窗口 Walk-Forward 样本外验证"
    )

    audit_report = load_historical_audit_cached()
    wf_report = load_walk_forward_cached()
    integrity = audit_report["dataset_integrity"]

    # Dynamic accuracy styling
    if audit_report["is_high_accuracy"]:
        acc_color = "#10b981"
        acc_bg = "rgba(16, 185, 129, 0.08)"
        acc_badge = "✅ HIGH ACCURACY PASSED"
    else:
        acc_color = "#f59e0b"
        acc_bg = "rgba(245, 158, 11, 0.08)"
        acc_badge = "⚠️ BELOW 8.5 BENCHMARK OR INTEGRITY ALERT"

    # Evaluator Executive Grade Cards
    eval_c1, eval_c2, eval_c3, eval_c4 = st.columns(4)
    with eval_c1:
        st.markdown(
            textwrap.dedent(
                f"""
        <div class="glass-card" style="border: 2px solid {acc_color}; background: {acc_bg};">
            <div class="metric-title" style="color: {acc_color};">独立评估器综合评级</div>
            <div class="metric-value" style="color: {acc_color};">{_esc(audit_report['evaluation_rating'])}</div>
            <div class="metric-sub" style="color: {acc_color}; font-weight: 700;">{acc_badge}</div>
        </div>
        """
            ).strip(),
            unsafe_allow_html=True,
        )

    with eval_c2:
        st.markdown(
            textwrap.dedent(
                f"""
        <div class="glass-card" style="border-left: 4px solid #38bdf8;">
            <div class="metric-title">纳入预测 Recall@5 / Prec@5</div>
            <div class="metric-value" style="color: #38bdf8;">{_esc(audit_report['composite_add_recall_top_5'])} <span style="font-size: 0.95rem; color: #94a3b8;">/ {_esc(audit_report['composite_add_precision_top_5'])}</span></div>
            <div class="metric-sub">Add MRR: {audit_report['mean_add_mrr']:.3f} | Recall@3: {_esc(audit_report['composite_add_recall_top_3'])}</div>
        </div>
        """
            ).strip(),
            unsafe_allow_html=True,
        )

    with eval_c3:
        st.markdown(
            textwrap.dedent(
                f"""
        <div class="glass-card" style="border-left: 4px solid #facc15;">
            <div class="metric-title">样本外 Walk-Forward (OOS)</div>
            <div class="metric-value" style="color: #facc15;">{wf_report['oos_avg_score']:.1f}/10</div>
            <div class="metric-sub">{wf_report['folds_evaluated']} 折扩展窗口 | OOS Recall@5: {_esc(wf_report['oos_add_recall_top_5'])} | MRR: {wf_report['oos_mean_add_mrr']:.3f}</div>
        </div>
        """
            ).strip(),
            unsafe_allow_html=True,
        )

    with eval_c4:
        st.markdown(
            textwrap.dedent(
                f"""
        <div class="glass-card" style="border-left: 4px solid #ef4444;">
            <div class="metric-title">剔除预测 Recall@5 / Prec@5</div>
            <div class="metric-value" style="color: #ef4444;">{_esc(audit_report['composite_del_recall_top_5'])} <span style="font-size: 0.95rem; color: #94a3b8;">/ {_esc(audit_report['composite_del_precision_top_5'])}</span></div>
            <div class="metric-sub">Del MRR: {audit_report['mean_del_mrr']:.3f} | Recall@3: {_esc(audit_report['composite_del_recall_top_3'])}</div>
        </div>
        """
            ).strip(),
            unsafe_allow_html=True,
        )

    # Transparent small-pool caveat notice
    st.info(f"📊 样本池透明度提示 (Small-Pool Caveat): {audit_report['small_pool_caveat']}")

    if not integrity["is_valid"]:
        st.error(f"❌ 数据集一致性校验失败 ({integrity['error_count']} 处错误): {'; '.join(integrity['errors'][:3])}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Historical Quarter Selector (safe lookup)
    quarters_list = audit_report.get("quarters_evaluated", [])
    if quarters_list:
        selected_quarter = st.selectbox(
            "📅 选择历史测试季度 (Drilldown Historical Quarter):",
            quarters_list,
            index=0,
        )

        q_data = next(
            (r for r in audit_report["quarterly_results"] if r["quarter"] == selected_quarter),
            None,
        )
        q_leak = next(
            (c for c in audit_report["leakage_audit"] if c["quarter"] == selected_quarter),
            None,
        )

        if q_data is None:
            st.warning("未找到所选季度的回测记录。")
        else:
            q_clean = bool(q_leak and q_leak["verified_zero_leakage"])
            if q_clean:
                leak_badge_html = (
                    '<div style="font-size: 0.8rem; background: #10b98120; color: #10b981; '
                    'border: 1px solid #10b981; padding: 2px 8px; border-radius: 4px; font-weight: bold;">'
                    "🛡️ 日期顺序与成员状态校验通过 (PIT &amp; Integrity Verified)</div>"
                )
            else:
                leak_badge_html = (
                    '<div style="font-size: 0.8rem; background: #ef444420; color: #ef4444; '
                    'border: 1px solid #ef4444; padding: 2px 8px; border-radius: 4px; font-weight: bold;">'
                    "⚠️ 数据完整性或日期顺序告警 (Integrity Alert)</div>"
                )

            st.markdown(
                textwrap.dedent(
                    f"""
            <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 14px 20px; margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                    <div>
                        <b>季度标识:</b> <span style="color:#facc15;">{_esc(q_data['quarter'])}</span> |
                        <b>时代市值门槛:</b> <code>&#36;{q_data['era_cap_threshold_b']:.1f}B</code> |
                        <b>数据冻结日:</b> <code>{_esc(q_data['cutoff_date'])}</code> |
                        <b>公告日:</b> <code>{_esc(q_data['announcement_date'])}</code> |
                        <b>生效日:</b> <code>{_esc(q_data['effective_date'])}</code>
                    </div>
                    {leak_badge_html}
                </div>
            </div>
            """
                ).strip(),
                unsafe_allow_html=True,
            )

            q_col1, q_col2 = st.columns(2)

            with q_col1:
                st.markdown(f"#### 🚀 {selected_quarter} 纳入结果真实比对 (候选池: {q_data['add_pool_size']} 支)")
                actual_adds_str = ", ".join([f"<b>{_esc(t)}</b>" for t in q_data["actual_additions"]])
                pred_top5_str = ", ".join([_esc(t) for t in q_data["top_5_predicted_additions"]])
                hits_str = (
                    ", ".join([f"<b style='color:#10b981;'>{_esc(t)}</b>" for t in q_data["addition_hits_top_5"]])
                    or "无"
                )

                st.markdown(
                    textwrap.dedent(
                        f"""
                <div class="glass-card">
                    <div style="margin-bottom: 8px;"><b>官方实际纳入名单:</b> {actual_adds_str}</div>
                    <div style="margin-bottom: 8px;"><b>算法预测前 5 顺位:</b> {pred_top5_str}</div>
                    <div style="margin-bottom: 8px;"><b>前 5 命中重合标的:</b> {hits_str} (Recall@5: {q_data['add_recall_top_5']*100:.1f}%, Prec@5: {q_data['add_precision_top_5']*100:.1f}%)</div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">Add MRR: {q_data['add_mrr']:.3f} | Recall@3: {q_data['add_recall_top_3']*100:.1f}% | Top-10 命中: {_esc(', '.join(q_data['addition_hits_top_10']))}</div>
                </div>
                """
                    ).strip(),
                    unsafe_allow_html=True,
                )

            with q_col2:
                st.markdown(f"#### ⚠️ {selected_quarter} 剔除结果真实比对 (监控池: {q_data['del_pool_size']} 支)")
                actual_dels_str = ", ".join([f"<b>{_esc(t)}</b>" for t in q_data["actual_deletions"]])
                pred_top5_del_str = ", ".join([_esc(t) for t in q_data["top_5_predicted_deletions"]])
                del_hits_str = (
                    ", ".join([f"<b style='color:#ef4444;'>{_esc(t)}</b>" for t in q_data["deletion_hits_top_5"]])
                    or "无"
                )

                st.markdown(
                    textwrap.dedent(
                        f"""
                <div class="glass-card">
                    <div style="margin-bottom: 8px;"><b>官方实际剔除名单:</b> {actual_dels_str}</div>
                    <div style="margin-bottom: 8px;"><b>算法高危前 5 顺位:</b> {pred_top5_del_str}</div>
                    <div style="margin-bottom: 8px;"><b>高危前 5 命中标的:</b> {del_hits_str} (Recall@5: {q_data['del_recall_top_5']*100:.1f}%, Prec@5: {q_data['del_precision_top_5']*100:.1f}%)</div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">Del MRR: {q_data['del_mrr']:.3f} | Recall@3: {q_data['del_recall_top_3']*100:.1f}%</div>
                </div>
                """
                    ).strip(),
                    unsafe_allow_html=True,
                )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📜 过去三年全量 13 个季度点测回测得分榜 (Full 3-Year Walkback Scorecard)")
    leak_by_q = {c["quarter"]: c for c in audit_report["leakage_audit"]}
    summary_table = []
    for r in audit_report["quarterly_results"]:
        q_chk = leak_by_q.get(r["quarter"], {})
        integrity_label = "🛡️ 通过" if q_chk.get("verified_zero_leakage") else "❌ 异常"
        summary_table.append(
            {
                "季度": r["quarter"],
                "时代门槛 ($B)": r["era_cap_threshold_b"],
                "样本池 (纳/剔)": f"{r['add_pool_size']} / {r['del_pool_size']}",
                "数据冻结日": str(r["cutoff_date"]),
                "官方纳入": ", ".join(r["actual_additions"]),
                "纳入 R@5 / P@5": f"{r['add_recall_top_5']*100:.0f}% / {r['add_precision_top_5']*100:.0f}%",
                "Add MRR": r["add_mrr"],
                "官方剔除": ", ".join(r["actual_deletions"]),
                "剔除 R@5 / MRR": f"{r['del_recall_top_5']*100:.0f}% / {r['del_mrr']:.2f}",
                "季度评分": f"{r['quarter_score']}/10",
                "完整性校验": integrity_label,
            }
        )
    st.dataframe(pd.DataFrame(summary_table), width="stretch", hide_index=True)


# ==============================================================================
# TAB 4: ARBITRAGE PLAYBOOK
# ==============================================================================
with tab_playbook:
    st.subheader("📈 S&P 500 指数效应与事件驱动套利实战手册 (Arbitrage Playbook)")
    st.caption("万亿美元被动资本调仓机制深度解构：掌握公告日至生效日之间的被动资金脉冲与价格超额收益规律")

    p_col1, p_col2 = st.columns(2)

    with p_col1:
        st.markdown(
            textwrap.dedent(
                """
        <div class="glass-card">
            <h4 style="color: #38bdf8; margin-top: 0;">1. 指数效应的三阶段动力学</h4>
            <p style="font-size: 0.88rem; line-height: 1.6; color: #cbd5e1;">
                <b>阶段一：预伏期（Cutoff 前 30~60 天）</b><br>
                对冲基金依据 S&amp;P 规则锁定第一顺位候选标的，建立多头底仓；同时融券做空市值垫底的高危成份股，博弈配对套利（Long Candidates / Short Vulnerable）。
                <br><br>
                <b>阶段二：公告爆发期（Announcement 日盘后至次日）</b><br>
                周五盘后 17:15 公告发布瞬间，入选标的在盘后交易中通常跳涨 <b>+3% ~ +8%</b>。活跃资金涌入推升流动性。
                <br><br>
                <b>阶段三：生效冲刺与平仓期（Effective Date 盘后撮合）</b><br>
                周五盘后为换仓生效时点（遇美股假日则提前至前一个交易日）。SPY/IVV/VOO 等被动指数基金在 MOC（Market on Close）集合竞价中买入新纳入成份股，当日成交量往往放大 <b>5~15 倍</b>。
            </p>
        </div>
        """
            ).strip(),
            unsafe_allow_html=True,
        )

    with p_col2:
        st.markdown(
            textwrap.dedent(
                """
        <div class="glass-card">
            <h4 style="color: #facc15; margin-top: 0;">2. 机构套利核心风控守则</h4>
            <p style="font-size: 0.88rem; line-height: 1.6; color: #cbd5e1;">
                <b>规则一：防范委员会主观裁量权</b><br>
                S&amp;P 指数委员会并非纯机械规则，拥有最终否决权（Discretionary Power）。即使满足市值（&#36;22.7B）、FMC/IWF 与过去 4 季度累计+Q0 GAAP 盈利条件，若行业权重过载也可能被延后。单标的仓位不宜超过组合的 10%。
                <br><br>
                <b>规则二：警惕生效后的“流动性悬崖”（Liquidity Hangover）</b><br>
                在生效日收盘被动买盘出尽后的 5 天冷静期内，往往会出现均值回归。机构交易员通常在生效日收盘前平仓获利，避免承受回撤。
                <br><br>
                <b>规则三：被动资金需求量精算（Days-to-Cover）</b><br>
                根据新入选股票的流通市值除以指数总流通市值，计算指数基金必须买入的绝对美元规模与相当于日常成交天数的比例，优先选择 Days-to-Cover &gt; 3 天的高弹性标的。
            </p>
        </div>
        """
            ).strip(),
            unsafe_allow_html=True,
        )
