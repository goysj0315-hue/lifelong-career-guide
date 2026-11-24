"""생애 진로 설계 챗봇 — 첫 화면(단계 선택)과 단계별 챗봇.

실행: 챗봇 실행.bat 더블클릭
      (또는 python -m streamlit run app.py)

화면 흐름: 첫 화면에서 생애 단계 네모를 누른다 → 그 단계 챗봇으로 넘어간다
          → '처음으로'를 누르면 첫 화면으로 돌아간다.
단계 목록과 지시문은 stages.py에 있다.
"""

import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from stages import BY_KEY, STAGES, system_prompt

load_dotenv()

# 음성 챗봇에서 쓰던 모델. .env에 OPENAI_MODEL을 적으면 바꿀 수 있다.
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

HEADLINE = "무덤에서 요람까지"
SUBLINE = "효율적인 직업 설계를 도와드립니다!"

st.set_page_config(page_title="생애 진로 설계", page_icon="🧭", layout="centered")

# 둥근 네모 카드와 큰 제목 (꾸미기는 나중에 따로 다듬는다)
st.markdown(
    """
<style>
.headline {font-size: 3rem; font-weight: 800; text-align: center; margin: 0.5rem 0 0;}
.subline  {font-size: 1.3rem; text-align: center; color: #666; margin-bottom: 2rem;}
.ask      {font-size: 1.2rem; font-weight: 700; text-align: center; margin-bottom: 1rem;}
div[data-testid="stVerticalBlockBorderWrapper"] {border-radius: 20px;}
.card-icon  {font-size: 2.4rem; text-align: center;}
.card-title {font-size: 1.15rem; font-weight: 700; text-align: center;}
.card-desc  {font-size: 0.9rem; color: #777; text-align: center; min-height: 2.8em;}
</style>
""",
    unsafe_allow_html=True,
)


def go(stage_key):
    st.session_state.stage = stage_key


def home():
    st.markdown(f'<div class="headline">{HEADLINE}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subline">{SUBLINE}</div>', unsafe_allow_html=True)
    st.markdown('<div class="ask">지금 어떤 시기를 지나고 계신가요?</div>', unsafe_allow_html=True)

    for row in (STAGES[:3], STAGES[3:]):
        cols = st.columns(3)
        for col, s in zip(cols, row):
            with col, st.container(border=True):
                st.markdown(f'<div class="card-icon">{s["icon"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="card-title">{s["title"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="card-desc">{s["desc"]}</div>', unsafe_allow_html=True)
                label = "시작하기" if s["ready"] else "준비 중"
                st.button(label, key=f"go_{s['key']}", on_click=go, args=(s["key"],),
                          use_container_width=True, type="primary" if s["ready"] else "secondary")


def chat(stage):
    st.button("← 처음으로", on_click=go, args=(None,))
    st.subheader(f'{stage["icon"]} {stage["title"]} 진로 설계')
    if not stage["ready"]:
        st.info("이 단계의 전용 자료는 준비 중입니다. 일반 상담만 가능합니다.")

    # 단계마다 대화 기록을 따로 둔다 (다른 단계로 갔다 와도 섞이지 않게)
    history_key = f"messages_{stage['key']}"
    if history_key not in st.session_state:
        st.session_state[history_key] = [{"role": "assistant", "content": stage["greeting"]}]
    messages = st.session_state[history_key]

    for m in messages:
        st.chat_message(m["role"]).write(m["content"])

    if prompt := st.chat_input("메시지를 입력하세요"):
        messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error(".env 파일에 OPENAI_API_KEY가 없습니다.")
            st.stop()

        client = OpenAI(api_key=api_key)
        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": system_prompt(stage)}] + messages,
                temperature=0.3,
                stream=True,
            )
            reply = st.chat_message("assistant").write_stream(
                chunk.choices[0].delta.content or "" for chunk in stream if chunk.choices
            )
        except Exception as e:  # 실패 이유를 그대로 보여 준다
            st.error(f"답변을 받지 못했습니다: {type(e).__name__}: {e}")
            st.stop()
        messages.append({"role": "assistant", "content": reply})


stage_key = st.session_state.get("stage")
if stage_key in BY_KEY:
    chat(BY_KEY[stage_key])
else:
    home()
