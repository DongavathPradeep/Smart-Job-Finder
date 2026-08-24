CUSTOM_CSS = """
<style>
header[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stStatusWidget"], div[class*="viewerBadge"] { display: none !important; }

.stApp {
    background: linear-gradient(rgba(10, 15, 30, 0.88), rgba(15, 23, 42, 0.93)), 
                url('https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070&auto=format&fit=crop') no-repeat center center fixed !important;
    background-size: cover !important;
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
button[data-baseweb="tab"] div p, button[data-baseweb="tab"] div span {
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
    font-weight: 600 !important;
}

label, .stTextInput label, .stSelectbox label, .stSlider label {
    color: #38bdf8 !important;
    font-weight: 700 !important;
}

.stButton > button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: #ffffff !important;
    border: 1px solid #3b82f6 !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
}

section[data-testid="stSidebar"] {
    background-color: rgba(11, 17, 32, 0.98) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
}

[data-testid="stMetric"] {
    background: rgba(30, 41, 59, 0.85) !important;
    border: 1px solid rgba(56, 189, 248, 0.3) !important;
    border-radius: 8px !important;
    padding: 12px !important;
}

.job-card {
    background-color: rgba(30, 41, 59, 0.88);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    padding: 18px;
    margin-bottom: 12px;
}

.tag-match {
    background-color: #064e3b;
    color: #34d399;
    border: 1px solid #059669;
    padding: 3px 8px;
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
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.82rem;
    margin-right: 6px;
    display: inline-block;
    font-weight: 600;
}
.tag-salary {
    background-color: rgba(245, 158, 11, 0.2);
    color: #fbbf24;
    border: 1px solid #d97706;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.82rem;
    margin-right: 6px;
    display: inline-block;
    font-weight: 700;
}
</style>
"""