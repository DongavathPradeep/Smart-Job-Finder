CUSTOM_CSS = """
<style>
header[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stStatusWidget"], div[class*="viewerBadge"] { display: none !important; }

.stApp {
    background-color: #0b1120 !important;
    color: #f1f5f9 !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

button[data-baseweb="tab"] {
    background-color: rgba(30, 41, 59, 0.7) !important;
    border: 1px solid #334155 !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 8px 16px !important;
    margin-right: 6px !important;
}
button[data-baseweb="tab"] div p {
    color: #94a3b8 !important;
    font-weight: 700 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background-color: #1e293b !important;
    border-bottom: 3px solid #38bdf8 !important;
}
button[data-baseweb="tab"][aria-selected="true"] div p {
    color: #38bdf8 !important;
    font-weight: 800 !important;
}

.stTextInput input, .stSelectbox > div > div {
    background-color: #1e293b !important;
    color: #ffffff !important;
    border: 1px solid #38bdf8 !important;
    border-radius: 6px !important;
}

label {
    color: #38bdf8 !important;
    font-weight: 700 !important;
}

.job-card {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
}

.tag-match {
    background-color: #064e3b;
    color: #34d399;
    border: 1px solid #059669;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.82rem;
    margin-right: 6px;
    display: inline-block;
    font-weight: 600;
}
.tag-gap {
    background-color: #7f1d1d;
    color: #f87171;
    border: 1px solid #dc2626;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.82rem;
    margin-right: 6px;
    display: inline-block;
    font-weight: 600;
}
</style>
"""
