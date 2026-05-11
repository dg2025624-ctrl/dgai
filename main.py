import streamlit as st
import anthropic
from datetime import datetime

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="나만의 AI",
    page_icon="✦",
    layout="wide",
)

# ── 모델 정의 ─────────────────────────────────────────────────
MODELS = {
    "claude-opus-4-5": {
        "label": "Claude Opus 4.5",
        "desc": "가장 강력 · 복잡한 작업",
        "icon": "◆",
        "color": "#7c3aed",
    },
    "claude-sonnet-4-5": {
        "label": "Claude Sonnet 4.5",
        "desc": "균형 잡힌 성능 · 추천",
        "icon": "◈",
        "color": "#2563eb",
    },
    "claude-haiku-4-5": {
        "label": "Claude Haiku 4.5",
        "desc": "초고속 · 간단한 질문",
        "icon": "◇",
        "color": "#059669",
    },
}

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg: #0c0c0f;
    --surface: #14141a;
    --surface2: #1c1c25;
    --border: #2a2a38;
    --text: #e8e8f0;
    --muted: #6b6b88;
    --accent: #7b61ff;
    --accent2: #00d4aa;
    --user-bg: #1a1a2e;
    --ai-bg: #141420;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: var(--bg) !important;
    color: var(--text) !important;
}

/* 사이드바 */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* 헤더 숨기기 */
header[data-testid="stHeader"] { display: none; }
.block-container { padding-top: 1.5rem !important; max-width: 860px; }

/* 브랜드 */
.brand {
    font-family: 'Instrument Serif', serif;
    font-size: 1.5rem;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #7b61ff, #00d4aa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.25rem;
}
.brand-sub { font-size: 0.78rem; color: var(--muted); margin-bottom: 1.5rem; }

/* 모델 카드 */
.model-card {
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 13px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.2s;
    background: var(--surface2);
}
.model-card.active {
    border-color: var(--accent);
    background: #1a1428;
    box-shadow: 0 0 0 1px var(--accent);
}
.model-card:hover { border-color: #4a4a60; }
.model-icon { font-size: 1.1rem; }
.model-name { font-size: 0.88rem; font-weight: 600; }
.model-desc { font-size: 0.75rem; color: var(--muted); }

/* 채팅 메시지 */
.msg-wrap { margin-bottom: 1.5rem; animation: fadeUp 0.3s ease; }
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.msg-header {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.msg-header.user { color: var(--accent); }
.msg-header.ai   { color: var(--accent2); }

.msg-bubble {
    border-radius: 14px;
    padding: 14px 18px;
    line-height: 1.75;
    font-size: 0.93rem;
    border: 1px solid var(--border);
}
.msg-bubble.user { background: var(--user-bg); border-color: #2a2a50; }
.msg-bubble.ai   { background: var(--ai-bg);   border-color: #1e1e30; }

/* 사용량 뱃지 */
.usage-badge {
    display: inline-flex;
    gap: 12px;
    background: #0f0f1a;
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.72rem;
    color: var(--muted);
    margin-top: 8px;
}
.usage-badge span { color: var(--text); font-weight: 500; }

/* 빈 화면 */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: var(--muted);
}
.empty-state .big { font-family: 'Instrument Serif', serif; font-size: 2.8rem; margin-bottom: 10px; color: #2a2a3a; }
.empty-state p { font-size: 0.9rem; }

/* 입력창 */
.stChatInput > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    color: var(--text) !important;
}
.stChatInput textarea { color: var(--text) !important; background: transparent !important; }

/* 통계 바 */
.stat-row {
    display: flex;
    justify-content: space-between;
    font-size: 0.78rem;
    color: var(--muted);
    padding: 8px 0;
    border-top: 1px solid var(--border);
    margin-top: 12px;
}
.stat-row b { color: var(--text); }

/* 구분선 */
hr { border-color: var(--border) !important; margin: 1rem 0; }

/* 라디오 / 슬라이더 스타일 */
[data-testid="stRadio"] label { font-size: 0.85rem !important; }
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
if "messages" not in st.session_state:
    st.session_state.messages = []
if "total_in" not in st.session_state:
    st.session_state.total_in = 0
if "total_out" not in st.session_state:
    st.session_state.total_out = 0
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "claude-sonnet-4-5"
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "당신은 친절하고 똑똑한 AI 어시스턴트입니다. 한국어로 답변해주세요."
if "conversations" not in st.session_state:
    st.session_state.conversations = {"기본 대화": []}
if "current_conv" not in st.session_state:
    st.session_state.current_conv = "기본 대화"

# ── 사이드바 ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="brand">✦ 나만의 AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Powered by Claude API</div>', unsafe_allow_html=True)

    # 모델 선택
    st.markdown("**모델 선택**")
    for model_id, info in MODELS.items():
        is_active = st.session_state.selected_model == model_id
        card_class = "model-card active" if is_active else "model-card"
        if st.button(
            f"{info['icon']}  {info['label']}\n{info['desc']}",
            key=f"btn_{model_id}",
            use_container_width=True,
        ):
            st.session_state.selected_model = model_id
            st.rerun()

    st.markdown("---")

    # 시스템 프롬프트
    st.markdown("**AI 성격 설정**")
    presets = {
        "🤖 기본 어시스턴트": "당신은 친절하고 똑똑한 AI 어시스턴트입니다. 한국어로 답변해주세요.",
        "👨‍💻 코딩 전문가": "당신은 시니어 소프트웨어 엔지니어입니다. 코드와 기술적 질문에 정확하고 실용적으로 답변하세요. 한국어로 답변해주세요.",
        "✍️ 글쓰기 코치": "당신은 전문 작가이자 편집자입니다. 글쓰기, 문장 교정, 창작에 도움을 주세요. 한국어로 답변해주세요.",
        "📊 비즈니스 분석가": "당신은 경험 많은 비즈니스 컨설턴트입니다. 데이터와 전략적 관점으로 답변하세요. 한국어로 답변해주세요.",
        "🎨 창의적 파트너": "당신은 창의적이고 상상력이 풍부한 AI입니다. 아이디어, 브레인스토밍, 창작 활동을 도와주세요. 한국어로 답변해주세요.",
    }
    selected_preset = st.selectbox("프리셋 선택", list(presets.keys()), label_visibility="collapsed")
    if st.button("프리셋 적용", use_container_width=True):
        st.session_state.system_prompt = presets[selected_preset]
        st.session_state.messages = []
        st.rerun()

    custom_sys = st.text_area(
        "직접 설정",
        value=st.session_state.system_prompt,
        height=90,
        label_visibility="collapsed",
        placeholder="AI의 역할과 성격을 직접 입력하세요...",
    )
    if custom_sys != st.session_state.system_prompt:
        if st.button("적용", use_container_width=True):
            st.session_state.system_prompt = custom_sys
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")

    # 응답 설정
    st.markdown("**응답 설정**")
    max_tokens = st.slider("최대 응답 길이", 256, 4096, 1500, 128, label_visibility="collapsed")

    st.markdown("---")

    # 대화 관리
    st.markdown("**대화 관리**")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🗑️ 초기화", use_container_width=True):
            st.session_state.messages = []
            st.session_state.total_in = 0
            st.session_state.total_out = 0
            st.rerun()

    # 누적 통계
    if st.session_state.total_in > 0:
        total = st.session_state.total_in + st.session_state.total_out
        st.markdown(f"""
        <div class="stat-row">
            <span>입력 <b>{st.session_state.total_in:,}</b></span>
            <span>출력 <b>{st.session_state.total_out:,}</b></span>
            <span>합계 <b>{total:,}</b></span>
        </div>
        """, unsafe_allow_html=True)

# ── 메인 영역 ────────────────────────────────────────────────
model_info = MODELS[st.session_state.selected_model]

# 현재 모델 표시
st.markdown(f"""
<div style="display:flex; align-items:center; gap:10px; margin-bottom:1rem;">
    <span style="font-size:1.3rem">{model_info['icon']}</span>
    <span style="font-size:0.88rem; color:#6b6b88;">현재 모델:</span>
    <span style="font-size:0.88rem; font-weight:600; color:{model_info['color']};">{model_info['label']}</span>
    <span style="font-size:0.78rem; color:#3a3a50; margin-left:4px;">— {model_info['desc']}</span>
</div>
""", unsafe_allow_html=True)

# ── 대화 출력 ────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
        <div class="big">✦</div>
        <p>무엇이든 물어보세요.<br>왼쪽에서 AI 모델과 성격을 바꿀 수 있어요.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        role = msg["role"]
        if role == "user":
            st.markdown(f"""
            <div class="msg-wrap">
                <div class="msg-header user">▲ 나</div>
                <div class="msg-bubble user">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            content_html = msg["content"].replace("\n", "<br>")
            usage_html = ""
            if "usage" in msg:
                u = msg["usage"]
                usage_html = f"""
                <div class="usage-badge">
                    입력 <span>{u['in']:,}</span> · 출력 <span>{u['out']:,}</span> · 합계 <span>{u['in']+u['out']:,}</span> 토큰
                </div>"""
            st.markdown(f"""
            <div class="msg-wrap">
                <div class="msg-header ai">✦ AI · {msg.get('model_label','Claude')}</div>
                <div class="msg-bubble ai">{content_html}</div>
                {usage_html}
            </div>
            """, unsafe_allow_html=True)

# ── 입력창 ───────────────────────────────────────────────────
if prompt := st.chat_input("메시지를 입력하세요... (Shift+Enter: 줄바꿈)"):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})

    # API 호출
    with st.spinner(""):
        api_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        response = client.messages.create(
            model=st.session_state.selected_model,
            max_tokens=max_tokens,
            system=st.session_state.system_prompt,
            messages=api_messages,
        )

    answer        = response.content[0].text
    input_tokens  = response.usage.input_tokens
    output_tokens = response.usage.output_tokens

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "model_label": model_info["label"],
        "usage": {"in": input_tokens, "out": output_tokens},
    })
    st.session_state.total_in  += input_tokens
    st.session_state.total_out += output_tokens
    st.rerun()
