import streamlit as st
import anthropic

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="나만의 AI ✨",
    page_icon="🤖",
    layout="wide",
)

# ── 모델 정의 ─────────────────────────────────────────────────
MODELS = {
    "claude-opus-4-5": {
        "label": "Opus 4.5",
        "full": "Claude Opus 4.5",
        "desc": "가장 강력해요 💪",
        "emoji": "🧠",
        "bg": "#fdf4ff",
        "border": "#d946ef",
        "text": "#86198f",
        "badge_bg": "#fae8ff",
    },
    "claude-sonnet-4-5": {
        "label": "Sonnet 4.5",
        "full": "Claude Sonnet 4.5",
        "desc": "균형 잡힌 추천 ⭐",
        "emoji": "✨",
        "bg": "#eff6ff",
        "border": "#3b82f6",
        "text": "#1d4ed8",
        "badge_bg": "#dbeafe",
    },
    "claude-haiku-4-5": {
        "label": "Haiku 4.5",
        "full": "Claude Haiku 4.5",
        "desc": "초고속 번개 ⚡",
        "emoji": "⚡",
        "bg": "#f0fdf4",
        "border": "#22c55e",
        "text": "#15803d",
        "badge_bg": "#dcfce7",
    },
}

PRESETS = {
    "🤖 기본 어시스턴트": "당신은 친절하고 유능한 AI 어시스턴트입니다. 항상 한국어로 답변해주세요.",
    "👨‍💻 코딩 전문가": "당신은 시니어 소프트웨어 엔지니어입니다. 코드와 기술 질문에 명확하고 실용적으로 답변하세요. 한국어로 답변해주세요.",
    "✍️ 글쓰기 코치": "당신은 전문 작가이자 편집자입니다. 글쓰기, 문장 교정, 창작을 도와주세요. 한국어로 답변해주세요.",
    "📊 비즈니스 분석가": "당신은 경험 많은 비즈니스 컨설턴트입니다. 전략적이고 논리적으로 답변하세요. 한국어로 답변해주세요.",
    "🎨 창의적 파트너": "당신은 창의력이 넘치는 AI입니다. 아이디어, 브레인스토밍, 창작을 신나게 도와주세요. 한국어로 답변해주세요.",
}

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=Nunito:wght@700;800;900&display=swap');

/* 전체 배경 */
html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif !important;
    background: #f9fafb !important;
    color: #1f2937 !important;
}

/* ── 사이드바 ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f8f7ff 100%) !important;
    border-right: 2px solid #e9d5ff !important;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.2rem;
}

/* 사이드바 텍스트 전체 색상 강제 */
[data-testid="stSidebar"] * {
    color: #1f2937 !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div {
    color: #374151 !important;
}

/* 헤더 제거 */
header[data-testid="stHeader"] { display: none; }
.block-container {
    padding-top: 1.2rem !important;
    max-width: 820px;
}

/* 브랜드 로고 */
.brand-wrap {
    background: linear-gradient(135deg, #7c3aed, #db2777, #f59e0b);
    border-radius: 16px;
    padding: 16px;
    margin: 0 0 20px 0;
    text-align: center;
    color: white !important;
}
.brand-title {
    font-family: 'Nunito', sans-serif;
    font-size: 1.6rem;
    font-weight: 900;
    color: white !important;
    letter-spacing: -0.5px;
}
.brand-sub {
    font-size: 0.75rem;
    color: rgba(255,255,255,0.85) !important;
    margin-top: 2px;
}

/* 섹션 제목 */
.sidebar-section {
    font-size: 0.78rem;
    font-weight: 700;
    color: #6b7280 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 16px 0 8px 0;
}

/* 모델 카드 버튼 */
.stButton > button {
    width: 100%;
    border-radius: 12px !important;
    border: 2px solid #e5e7eb !important;
    background: white !important;
    color: #374151 !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    padding: 10px 14px !important;
    text-align: left !important;
    transition: all 0.18s !important;
    cursor: pointer;
    margin-bottom: 6px;
    line-height: 1.5 !important;
}
.stButton > button:hover {
    border-color: #a78bfa !important;
    background: #faf5ff !important;
    transform: translateX(3px);
    box-shadow: 2px 2px 8px rgba(124,58,237,0.15) !important;
}

/* 활성 모델 버튼 — active 클래스는 직접 못 넣으므로 JS로 처리 */
.model-opus button   { border-color: #d946ef !important; background: #fdf4ff !important; color: #86198f !important; }
.model-sonnet button { border-color: #3b82f6 !important; background: #eff6ff !important; color: #1d4ed8 !important; }
.model-haiku button  { border-color: #22c55e !important; background: #f0fdf4 !important; color: #15803d !important; }

/* selectbox */
[data-testid="stSelectbox"] > div > div {
    background: white !important;
    border: 2px solid #e5e7eb !important;
    border-radius: 10px !important;
    color: #374151 !important;
}

/* textarea */
[data-testid="stTextArea"] textarea {
    background: white !important;
    border: 2px solid #e5e7eb !important;
    border-radius: 10px !important;
    color: #374151 !important;
    font-size: 0.85rem !important;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: #a78bfa !important;
}

/* slider */
[data-testid="stSlider"] {
    padding: 0 !important;
}

/* 구분선 */
hr { border-color: #e9d5ff !important; margin: 14px 0 !important; }

/* ── 메인 채팅 영역 ── */
.current-model-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    background: white;
    border: 2px solid #e5e7eb;
    border-radius: 14px;
    padding: 10px 18px;
    margin-bottom: 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.current-model-bar .emoji { font-size: 1.4rem; }
.current-model-bar .name  { font-weight: 700; font-size: 0.95rem; }
.current-model-bar .desc  { font-size: 0.82rem; color: #9ca3af; }

/* 빈 화면 */
.empty-state {
    text-align: center;
    padding: 70px 30px;
}
.empty-emoji { font-size: 4rem; margin-bottom: 16px; }
.empty-title {
    font-family: 'Nunito', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    color: #1f2937;
    margin-bottom: 8px;
}
.empty-sub { color: #9ca3af; font-size: 0.9rem; line-height: 1.6; }

/* 환영 카드 */
.welcome-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    margin-top: 20px;
}
.chip {
    background: white;
    border: 2px solid #e5e7eb;
    border-radius: 20px;
    padding: 7px 16px;
    font-size: 0.83rem;
    color: #6b7280;
    cursor: pointer;
    transition: all 0.15s;
}
.chip:hover { border-color: #a78bfa; color: #7c3aed; background: #faf5ff; }

/* 메시지 */
.msg-wrap { margin-bottom: 18px; animation: popIn 0.25s ease; }
@keyframes popIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

.msg-header {
    font-size: 0.78rem;
    font-weight: 700;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.msg-header.user { color: #7c3aed; }
.msg-header.ai   { color: #0284c7; }

.msg-bubble {
    border-radius: 16px;
    padding: 14px 18px;
    line-height: 1.8;
    font-size: 0.92rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.msg-bubble.user {
    background: linear-gradient(135deg, #7c3aed, #9333ea);
    color: white !important;
    border-bottom-right-radius: 4px;
}
.msg-bubble.ai {
    background: white;
    border: 2px solid #e5e7eb;
    color: #1f2937;
    border-bottom-left-radius: 4px;
}

/* 토큰 뱃지 */
.token-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #f3f4f6;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.72rem;
    color: #6b7280;
    margin-top: 7px;
}
.token-badge .val { color: #374151; font-weight: 600; }

/* 통계 카드 */
.stat-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
    margin-top: 10px;
}
.stat-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 8px 10px;
    text-align: center;
}
.stat-card .sv { font-size: 1rem; font-weight: 700; color: #7c3aed !important; }
.stat-card .sk { font-size: 0.68rem; color: #9ca3af !important; margin-top: 1px; }

/* 초기화 버튼 강조 */
.reset-btn button {
    background: linear-gradient(135deg, #fee2e2, #fecaca) !important;
    border-color: #fca5a5 !important;
    color: #b91c1c !important;
}
.reset-btn button:hover {
    background: linear-gradient(135deg, #fecaca, #fca5a5) !important;
    border-color: #f87171 !important;
}

/* 입력창 */
[data-testid="stChatInput"] > div {
    border: 2px solid #e5e7eb !important;
    border-radius: 16px !important;
    background: white !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: #a78bfa !important;
    box-shadow: 0 2px 12px rgba(124,58,237,0.15) !important;
}
[data-testid="stChatInput"] textarea { color: #1f2937 !important; font-size: 0.93rem !important; }
</style>
""", unsafe_allow_html=True)

# ── API 클라이언트 ────────────────────────────────────────────
@st.cache_resource
def get_client():
    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        st.error("⚠️ Streamlit Secrets에 ANTHROPIC_API_KEY를 추가해주세요.")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)

client = get_client()

# ── 세션 초기화 ───────────────────────────────────────────────
def init_session():
    defaults = {
        "messages": [],
        "total_in": 0,
        "total_out": 0,
        "msg_count": 0,
        "selected_model": "claude-sonnet-4-5",
        "system_prompt": list(PRESETS.values())[0],
        "selected_preset": list(PRESETS.keys())[0],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ── 사이드바 ─────────────────────────────────────────────────
with st.sidebar:
    # 브랜드
    st.markdown("""
    <div class="brand-wrap">
        <div class="brand-title">🤖 나만의 AI</div>
        <div class="brand-sub">Powered by Claude API ✨</div>
    </div>
    """, unsafe_allow_html=True)

    # 모델 선택
    st.markdown('<div class="sidebar-section">🎯 모델 선택</div>', unsafe_allow_html=True)

    for model_id, info in MODELS.items():
        is_active = st.session_state.selected_model == model_id
        label = f"{info['emoji']}  **{info['full']}**\n{info['desc']}" + (" ← 현재 사용 중" if is_active else "")
        if st.button(label, key=f"model_{model_id}", use_container_width=True):
            st.session_state.selected_model = model_id
            st.rerun()

    st.markdown("---")

    # AI 성격 설정
    st.markdown('<div class="sidebar-section">🎭 AI 성격 설정</div>', unsafe_allow_html=True)
    preset_key = st.selectbox(
        "프리셋",
        list(PRESETS.keys()),
        index=list(PRESETS.keys()).index(st.session_state.selected_preset),
        label_visibility="collapsed",
    )
    if st.button("✅ 이 성격으로 시작하기", use_container_width=True):
        st.session_state.system_prompt  = PRESETS[preset_key]
        st.session_state.selected_preset = preset_key
        st.session_state.messages = []
        st.rerun()

    custom = st.text_area(
        "직접 설정",
        value=st.session_state.system_prompt,
        height=85,
        label_visibility="collapsed",
        placeholder="AI 역할을 자유롭게 입력하세요 ✏️",
    )
    if custom != st.session_state.system_prompt:
        if st.button("✏️ 직접 입력 적용", use_container_width=True):
            st.session_state.system_prompt = custom
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")

    # 응답 설정
    st.markdown('<div class="sidebar-section">⚙️ 응답 설정</div>', unsafe_allow_html=True)
    st.caption("최대 응답 길이 (토큰)")
    max_tokens = st.slider("토큰", 256, 4096, 1500, 128, label_visibility="collapsed")

    st.markdown("---")

    # 대화 관리
    st.markdown('<div class="sidebar-section">📊 대화 현황</div>', unsafe_allow_html=True)
    total_tokens = st.session_state.total_in + st.session_state.total_out
    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card">
            <div class="sv">{st.session_state.msg_count}</div>
            <div class="sk">💬 대화 수</div>
        </div>
        <div class="stat-card">
            <div class="sv">{total_tokens:,}</div>
            <div class="sk">🔢 총 토큰</div>
        </div>
        <div class="stat-card">
            <div class="sv">{st.session_state.total_in:,}</div>
            <div class="sk">📥 입력</div>
        </div>
        <div class="stat-card">
            <div class="sv">{st.session_state.total_out:,}</div>
            <div class="sk">📤 출력</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages  = []
        st.session_state.total_in  = 0
        st.session_state.total_out = 0
        st.session_state.msg_count = 0
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ── 메인 영역 ────────────────────────────────────────────────
cur = MODELS[st.session_state.selected_model]
st.markdown(f"""
<div class="current-model-bar">
    <span class="emoji">{cur['emoji']}</span>
    <div>
        <div class="name" style="color:{cur['text']}">{cur['full']}</div>
        <div class="desc">{cur['desc']} &nbsp;·&nbsp; {st.session_state.selected_preset}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── 대화 출력 ────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-emoji">🤖✨</div>
        <div class="empty-title">안녕하세요! 무엇을 도와드릴까요?</div>
        <div class="empty-sub">
            왼쪽에서 AI 모델과 성격을 골라보세요.<br>
            아래 입력창에 메시지를 입력하면 바로 시작됩니다!
        </div>
        <div class="welcome-chips">
            <div class="chip">💡 아이디어 내줘</div>
            <div class="chip">📝 이메일 써줘</div>
            <div class="chip">🐍 파이썬 코드 짜줘</div>
            <div class="chip">📖 영어 번역해줘</div>
            <div class="chip">🎯 오늘 할 일 정리해줘</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        role = msg["role"]
        if role == "user":
            st.markdown(f"""
            <div class="msg-wrap" style="padding-left:60px">
                <div class="msg-header user">🙋 나</div>
                <div class="msg-bubble user">{msg["content"].replace(chr(10), "<br>")}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            m = MODELS.get(msg.get("model_id", "claude-sonnet-4-5"), cur)
            content_html = msg["content"].replace("\n", "<br>")
            usage_html = ""
            if "usage" in msg:
                u = msg["usage"]
                usage_html = f"""
                <div class="token-badge">
                    📊 입력 <span class="val">{u['in']:,}</span>
                    · 출력 <span class="val">{u['out']:,}</span>
                    · 합계 <span class="val">{u['in']+u['out']:,}</span> 토큰
                </div>"""
            st.markdown(f"""
            <div class="msg-wrap" style="padding-right:60px">
                <div class="msg-header ai">{m['emoji']} {m['full']}</div>
                <div class="msg-bubble ai">{content_html}</div>
                {usage_html}
            </div>
            """, unsafe_allow_html=True)

# ── 입력창 ───────────────────────────────────────────────────
if prompt := st.chat_input("메시지를 입력하세요... (Shift+Enter: 줄바꿈)"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner(f"{cur['emoji']} AI가 생각하는 중..."):
        api_msgs = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        response = client.messages.create(
            model=st.session_state.selected_model,
            max_tokens=max_tokens,
            system=st.session_state.system_prompt,
            messages=api_msgs,
        )

    answer = response.content[0].text
    in_tok = response.usage.input_tokens
    out_tok = response.usage.output_tokens

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "model_id": st.session_state.selected_model,
        "usage": {"in": in_tok, "out": out_tok},
    })
    st.session_state.total_in  += in_tok
    st.session_state.total_out += out_tok
    st.session_state.msg_count += 1
    st.rerun()
