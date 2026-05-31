"""Application configuration."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# CSV data directory (no database server required)
DATA_DIR = BASE_DIR / "data"

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Risk thresholds (days)
RISK_STALE_DAYS = int(os.getenv("RISK_STALE_DAYS", "14"))
RISK_STAGE_STUCK_DAYS = int(os.getenv("RISK_STAGE_STUCK_DAYS", "30"))

# Project stages (fixed workflow)
STAGES: dict[int, str] = {
    0: "未開始 / Planning",
    1: "Stage 1 - 需求商談",
    2: "Stage 2 - 資料收集",
    3: "Stage 3 - AI方法開發與驗證",
    4: "Stage 4 - CIM與廠商串接",
    5: "Stage 5 - 管理平台串接",
}

STAGE_SUBTASKS: dict[int, list[str]] = {
    1: [
        "確認需求文件",
        "確認機台規格",
        "確認相機規格",
        "確認資料取得方式",
        "確認 AI 輔助項目",
        "確認機台現況",
        "確認資訊流串接方式",
    ],
    2: [
        "收集缺陷樣本資料",
        "確認資料標註規範",
        "建立資料集目錄結構",
        "完成資料品質檢查",
        "確認資料儲存與存取權限",
    ],
    3: [
        "完成模型選型評估",
        "完成資料清理與前處理",
        "完成模型訓練與驗證",
        "完成離線指標評估報告",
        "完成現場 PoC 測試",
    ],
    4: [
        "確認 API 格式",
        "CIM 串接測試",
        "廠商測試驗證",
        "完成異常處理流程",
        "完成上線前檢查清單",
    ],
    5: [
        "確認管理平台 API 規格",
        "完成管理平台串接開發",
        "完成 UAT 測試",
        "確認正式上線計畫",
        "完成文件交付",
    ],
}
