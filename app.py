import pandas as pd
import streamlit as st

# Googleスプレッドシート CSV 形式の URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1-B3-c9xsGxAbh6iolhiafa4QeqsrXdQQvO4XIL-nPoQ/export?format=csv"

# --- データ読み込み ---
@st.cache_data(ttl=60)
def load_data(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()  # 列名の空白を除去
    return df

df = load_data(SHEET_URL)

st.title("ドイツ語単語テスト")

# --- セッション初期化 ---
if 'quiz_started' not in st.session_state:
    st.session_state['quiz_started'] = False
if 'show_result' not in st.session_state:
    st.session_state['show_result'] = False
if 'user_answers' not in st.session_state:
    st.session_state['user_answers'] = {}

# --- 設定画面 ---
if not st.session_state['quiz_started']:
    parts = st.multiselect(
        "品詞を選択してください（複数可）",
        options=df["品詞"].unique()
    )

    lessons = st.multiselect(
        "レッスンを選択してください（複数可）",
        options=df["レッスン"].unique()
    )

    direction = st.radio(
        "出題方向を選んでください",
        options=["日本語 → ドイツ語", "ドイツ語 → 日本語"]
    )

    max_num = len(df)
    num_questions = st.number_input(
        "出題数",
        min_value=1,
        max_value=max_num,
        value=min(5, max_num),
        step=1
    )

    # --- テスト開始 ---
    if st.button("テスト開始"):
        filtered = df
        if parts:
            filtered = filtered[filtered["品詞"].isin(parts)]
        if lessons:
            filtered = filtered[filtered["レッスン"].isin(lessons)]

        if filtered.empty:
            st.warning("選択条件に合う単語がありません。")
        else:
            questions = filtered.sample(min(num_questions, len(filtered)))
            st.session_state['questions'] = questions
            st.session_state['quiz_started'] = True
            st.session_state['direction'] = direction
            st.session_state['show_result'] = False
            st.session_state['user_answers'] = {}

# --- テスト画面（フォームなし） ---
if st.session_state['quiz_started']:
    questions = st.session_state['questions']
    direction = st.session_state['direction']
    user_answers = st.session_state['user_answers']

    st.write("各単語に回答してください:")

    for i, row in questions.iterrows():
        key_name = f"q_{i}"
        if direction == "日本語 → ドイツ語":
            user_answers[i] = st.text_input(
                f"{i+1}. {row['日本語']}",
                value=user_answers.get(i, "")
            )
        else:
            user_answers[i] = st.text_input(
                f"{i+1}. {row['ドイツ語']}",
                value=user_answers.get(i, "")
            )

    st.session_state['user_answers'] = user_answers

    # 「回答を確認」ボタンでのみ正解を表示
    if st.button("回答を確認"):
        st.session_state['show_result'] = True

    # --- 正解表示 ---
    if st.session_state.get('show_result', False):
        score = 0
        for i, row in questions.iterrows():
            ans = str(user_answers.get(i, "")).strip().lower()
            correct = row['ドイツ語' if direction == "日本語 → ドイツ語" else '日本語'].strip().lower()
            if ans == correct:
                st.success(f"{i+1}. 正解！")
                score += 1
            else:
                st.error(f"{i+1}. 不正解。正解は {correct} です")

        st.write(f"スコア: {score}/{len(questions)}")

 
  # --- 最初に戻るボタン ---
    if st.button("最初の画面に戻る"):
        st.session_state['page'] = 'setup'
        st.session_state['show_result'] = False
        st.session_state['user_answers'] = {}
