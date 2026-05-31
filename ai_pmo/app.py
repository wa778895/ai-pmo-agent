"""
AI PMO Agent — Standalone Streamlit App (Windows / CSV)

No uvicorn or SQLite required. Data stored in data/*.csv

Run:
    streamlit run app.py
Or double-click run.bat
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import date

import pandas as pd
import streamlit as st
from plotly.graph_objects import Figure

from config import DATA_DIR, STAGE_SUBTASKS, STAGES
from services.charts import build_all_charts
from services.progress_agent import apply_progress_updates
from services.report_agent import create_and_save_report, generate_weekly_report_md
from services.risk_detector import refresh_all_risks
from storage import csv_store

st.set_page_config(page_title="AI PMO Agent", page_icon="📊", layout="wide")


def _init():
    csv_store.seed_projects()
    refresh_all_risks()


def _project_dict(p) -> dict:
    d = asdict(p)
    d["due_date"] = p.due_date.isoformat() if p.due_date else None
    d["stage_entered_at"] = p.stage_entered_at.isoformat()
    d["last_updated"] = p.last_updated.isoformat()
    d["created_at"] = p.created_at.isoformat()
    return d


def stage_label(stage: int) -> str:
    return STAGES.get(stage, f"Stage {stage}")


def risk_badge(risk: str) -> str:
    icons = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}
    return f"{icons.get(risk, '⚪')} {risk}"


def page_dashboard():
    st.header("📋 Project Dashboard")
    projects = csv_store.get_projects()
    if not projects:
        st.warning("尚無專案，請執行 init_data.py")
        return

    rows = [_project_dict(p) for p in projects]
    df = pd.DataFrame(rows)
    df["Current Stage"] = df["current_stage"].apply(stage_label)
    df["Risk"] = df["risk"].apply(risk_badge)
    df["Progress %"] = df["progress"].apply(lambda x: f"{x:.0f}%")
    df["Due Date"] = pd.to_datetime(df["due_date"], errors="coerce").dt.date

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("專案總數", len(df))
    c2.metric("進行中", len(df[df["status"].isin(["In Progress", "Waiting", "Planning"])]))
    c3.metric("高風險", len(df[df["risk"].isin(["HIGH", "CRITICAL"])]))
    c4.metric("已完成", len(df[df["status"] == "Completed"]))

    display = df.rename(columns={
        "name": "Project Name", "customer": "Customer", "process": "Process",
        "next_action": "Next Action", "status": "Status", "remark": "Remark",
    })[[
        "Project Name", "Customer", "Process", "Current Stage", "Progress %",
        "Risk", "Next Action", "Due Date", "Status", "Remark",
    ]]
    st.dataframe(display, use_container_width=True, hide_index=True)
    st.caption(f"資料來源：`{DATA_DIR / 'projects.csv'}`")


def page_weekly_tasks():
    st.header("✅ Weekly Task Generator")
    week_start = st.date_input("週次起始（週一）", value=date.today())

    if st.button("🔄 產生本週待辦", type="primary"):
        tasks = csv_store.generate_weekly_tasks(week_start)
        st.session_state["weekly_tasks"] = tasks
        st.success(f"已產生 {len(tasks)} 項待辦 → 寫入 weekly_tasks.csv")

    tasks = st.session_state.get("weekly_tasks") or csv_store.get_weekly_tasks(week_start)
    if not tasks:
        st.info("尚無本週待辦，請點擊「產生本週待辦」")
        return

    tdf = pd.DataFrame([asdict(t) for t in tasks])
    st.dataframe(
        tdf[["project_name", "description", "completed"]].rename(
            columns={"project_name": "Project", "description": "Task", "completed": "Done"}
        ),
        use_container_width=True, hide_index=True,
    )


def page_progress_update():
    st.header("🤖 Progress Update Agent")
    st.caption("貼上週報文字，自動解析並更新 CSV")

    example = """DUC:
完成API串接

CoW Xray:
完成管理平台串接80%

Foundation Model:
完成資料清理"""

    text = st.text_area("週報輸入", value=example, height=220)
    if st.button("提交更新", type="primary"):
        with st.spinner("解析中…"):
            result = apply_progress_updates(text)
        for e in result.errors:
            st.warning(e)
        if result.parsed:
            st.subheader("解析結果")
            st.json(result.parsed)
        if result.applied:
            st.subheader("已更新專案")
            st.dataframe(pd.DataFrame(result.applied), use_container_width=True)
        elif not result.errors:
            st.info("沒有專案被更新")


def page_weekly_report():
    st.header("📝 Weekly Report Agent")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("預覽週報"):
            st.session_state["report_md"] = generate_weekly_report_md()
    with c2:
        if st.button("產生並儲存週報", type="primary"):
            st.session_state["report_md"] = create_and_save_report()
            st.success("已儲存至 weekly_reports.csv")

    md = st.session_state.get("report_md", "")
    if md:
        st.markdown(md)
        st.download_button("下載 Markdown", md, file_name="weekly_report.md", mime="text/markdown")
    else:
        st.info("點擊「預覽週報」或「產生並儲存週報」")


def page_executive():
    st.header("📈 Executive Dashboard")
    charts = build_all_charts()
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(Figure(charts["progress_bar"]), use_container_width=True)
    with c2:
        st.plotly_chart(Figure(charts["stage_distribution"]), use_container_width=True)
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(Figure(charts["risk_distribution"]), use_container_width=True)
    with c4:
        st.plotly_chart(Figure(charts["gantt"]), use_container_width=True)


def page_stages():
    st.header("📌 專案階段流程")
    for num, desc in STAGES.items():
        st.markdown(f"**{desc}**")
        for s in STAGE_SUBTASKS.get(num, []):
            st.markdown(f"- {s}")


def main():
    _init()
    st.sidebar.title("AI PMO Agent")
    st.sidebar.caption("Windows 本機版 · CSV 儲存")
    st.sidebar.markdown(f"📁 `{DATA_DIR}`")

    page = st.sidebar.radio("功能", [
        "Project Dashboard", "Weekly Tasks", "Progress Update",
        "Weekly Report", "Executive Dashboard", "Stage Reference",
    ])

    if page == "Project Dashboard":
        page_dashboard()
    elif page == "Weekly Tasks":
        page_weekly_tasks()
    elif page == "Progress Update":
        page_progress_update()
    elif page == "Weekly Report":
        page_weekly_report()
    elif page == "Executive Dashboard":
        page_executive()
    elif page == "Stage Reference":
        page_stages()


if __name__ == "__main__":
    main()
