# AI PMO Agent — Windows 本機版（CSV）

半導體 **AOI / Xray / SAT** AI 專案管理 Agent。

**不需 uvicorn、不需 SQLite**，所有資料存成 CSV，雙擊 `run.bat` 即可啟動。

## 快速開始（Windows）

### 方法一：一鍵啟動

```bat
雙擊 run.bat
```

### 方法二：手動

```powershell
cd ai_pmo
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python init_data.py
streamlit run app.py
```

瀏覽器：http://localhost:8501

## CSV 資料檔

| 檔案 | 內容 |
|------|------|
| `data/projects.csv` | 專案主檔 |
| `data/project_updates.csv` | 進度更新紀錄 |
| `data/weekly_tasks.csv` | 本週待辦 |
| `data/weekly_reports.csv` | 週報 |

可用 Excel 直接開啟編輯 `projects.csv`。

## 功能

1. **Project Dashboard** — 專案一覽 + 風險標記
2. **Weekly Task Generator** — 依 Stage 產生待辦
3. **Progress Update Agent** — 貼週報文字自動更新 CSV
4. **Weekly Report Agent** — 產生 Markdown 週報
5. **Executive Dashboard** — Plotly 四種圖表
6. **Risk Detection** — 14 天未更新 HIGH / 同 Stage 30 天 CRITICAL

## 環境設定

`.env`（選填，有 OpenAI Key 時 LLM 解析更準確）：

```env
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4o-mini
```

未設定 API Key 時，Progress Update 使用規則式解析，週報使用模板。

## 專案結構

```
ai_pmo/
├── app.py              ← 主程式（Streamlit，直接執行）
├── run.bat             ← Windows 一鍵啟動
├── init_data.py        ← 初始化 CSV
├── config.py
├── storage/
│   ├── csv_store.py    ← CSV 讀寫
│   └── seed_data.py
├── services/           ← Agent 邏輯
└── data/*.csv          ← 資料檔
```

## 舊版 API 模式（可選）

`api/` 目錄保留 FastAPI + SQLite 舊版，若日後需要可另行安裝：

```powershell
pip install fastapi uvicorn sqlalchemy httpx
python -m uvicorn api.main:app --port 8000
```

**日常使用請直接用 `streamlit run app.py`，無需後端。**

## 重新初始化資料

```powershell
python init_data.py --force
```
