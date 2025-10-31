import streamlit as st
import pandas as pd
import random

SHEET_URL = "https://docs.google.com/spreadsheets/d/1-B3-c9xsGxAbh6iolhiafa4QeqsrXdQQvO4XIL-nPoQ/export?format=csv"

@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

df = load_data(SHEET_URL)

# セッションステート初期化
if "stage" not in st.session_state:
    st.session_state.stage = "setting"
if "questions" not in st.session_state:
    st.session_state.questions = []
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "direction" not in st.session_state:
    st.session_state.direction = "日本語 → ドイツ語"

def reset():
    st.session_state.stage = "setting"
    st.session_state.questions = []
    st.session_state.answers = {}
    st.session_state.current_index = 0
    st.session_state.direction = "日本語 → ドイツ語"

# ---------------- 設定画面 ----------------
if st.session_state.stage == "setting":
    st.title("ドイツ語単語テスト設定")

    parts = st.multiselect("品詞を選択", options=df["品詞"].unique())
    ranges = st.multiselect("出題範囲を選択（複数可）", options=df["出題範囲"].unique())
    st.session_state.direction = st.radio("出題方向", ["日本語 → ドイツ語", "ドイツ語 → 日本語"])
    num_questions = st.number_input("出題数", min_value=10, max_value=50, step=10)

    if st.button("テスト開始"):
        filtered = df.copy()
        if parts:
            filtered = filtered[filtered["品詞"].isin(parts)]
        if ranges:
            filtered = filtered[filtered["出題範囲"].isin(ranges)]
        st.session_state.questions = filtered.sample(min(num_questions, len(filtered))).to_dict(orient="records")
        st.session_state.stage = "quiz"
        st.session_state.current_index = 0
        st.experimental_rerun()  # ボタン押下時のみ

# ---------------- クイズ画面 ----------------
elif st.session_state.stage == "quiz":
    idx = st.session_state.current_index
    question = st.session_state.questions[idx]

    st.write(f"問題 {idx + 1} / {len(st.session_state.questions)}")

    if st.session_state.direction == "日本語 → ドイツ語":
        st.write(f"日本語: {question['日本語']}")
        ans = st.text_input("ドイツ語で答えてください", key=f"q{idx}")
        correct_answer = question["ドイツ語"]
    else:
        st.write(f"ドイツ語: {question['ドイツ語']}")
        ans = st.text_input("日本語で答えてください", key=f"q{idx}")
        correct_answer = question["日本語"]

    if st.button("回答を確認"):
        st.session_state.answers[idx] = ans.strip()
        if ans.strip() == correct_answer:
            st.success("正解！")
        else:
            st.error(f"不正解… 正解は: {correct_answer}")

    if st.button("次の問題"):
        if idx + 1 < len(st.session_state.questions):
            st.session_state.current_index += 1
        else:
            st.session_state.stage = "result"
        st.experimental_rerun()  # ボタン押下時のみ

    if st.button("最初の画面に戻る"):
        reset()
        st.experimental_rerun()  # ボタン押下時のみ

# ---------------- 結果画面 ----------------
elif st.session_state.stage == "result":
    st.title("テスト結果")
    correct_count = 0
    for i, q in enumerate(st.session_state.questions):
        user_ans = st.session_state.answers.get(i, "")
        correct_answer = q['ドイツ語'] if st.session_state.direction == "日本語 → ドイツ語" else q['日本語']
        if user_ans == correct_answer:
            correct_count += 1
        st.write(f"{i+1}. {q['日本語']} / {q['ドイツ語']} → あなた: {user_ans} / 正解: {correct_answer}")

    st.write(f"正解数: {correct_count} / {len(st.session_state.questions)}")

    if st.button("最初の画面に戻る"):
        reset()
        st.experimental_rerun()
