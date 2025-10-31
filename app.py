import pandas as pd
import streamlit as st

# GoogleスプレッドシートのCSVリンク
SHEET_URL = "https://docs.google.com/spreadsheets/d/1-B3-c9xsGxAbh6iolhiafa4QeqsrXdQQvO4XIL-nPoQ/export?format=csv"

# データ読み込み関数（キャッシュ付き、ttlで更新反映可能）
@st.cache_data(ttl=60)
def load_data(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

df = load_data(SHEET_URL)

st.title("ドイツ語単語テスト")

# --- 設定画面 ---
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

# --- テスト開始ボタン ---
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
        st.session_state['show_result'] = False  # 正解非表示フラグ

# --- フォーム方式で問題を表示 ---
if st.session_state.get('quiz_started', False):
    questions = st.session_state['questions']
    direction = st.session_state['direction']
    user_answers = st.session_state.get('user_answers', {})

    with st.form("quiz_form"):
        st.write("各単語に回答してください:")

        for i, row in questions.iterrows():
            key_name = f"q_{i}"
            if direction == "日本語 → ドイツ語":
                user_answers[i] = st.text_input(f"{i+1}. {row['日本語']}", key=key_name, value=user_answers.get(i, ""))
            else:
                user_answers[i] = st.text_input(f"{i+1}. {row['ドイツ語']}", key=key_name, value=user_answers.get(i, ""))

        submitted = st.form_submit_button("回答を確認")
        if submitted:
            st.session_state['user_answers'] = user_answers
            st.session_state['show_result'] = True

    # --- 正解表示 ---
    if st.session_state.get('show_result', False):
        score = 0
        for i, row in questions.iterrows():
            ans = user_answers[i].strip().lower()
            if direction == "日本語 → ドイツ語":
                correct = str(row["ドイツ語"]).strip().lower()
            else:
                correct = str(row["日本語"]).strip().lower()

            if ans == correct:
                st.success(f"{i+1}. 正解！")
                score += 1
            else:
                st.error(f"{i+1}. 不正解。正解は {correct} です")

        st.write(f"あなたのスコア: {score} / {len(questions)}")

        # リセットボタン
        if st.button("テストをリセット"):
            for key in ["questions", "quiz_started", "direction", "show_result", "user_answers"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.experimental_rerun()
