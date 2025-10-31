import pandas as pd
import streamlit as st

# GoogleスプレッドシートのCSVリンク
SHEET_URL = "https://docs.google.com/spreadsheets/d/1-B3-c9xsGxAbh6iolhiafa4QeqsrXdQQvO4XIL-nPoQ/export?format=csv"

# データ読み込み関数（キャッシュ付き、ttlで更新反映可能）
@st.cache_data(ttl=60)  # 60秒ごとに最新を取得
def load_data(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()  # 列名の空白を削除
    return df

# データ読み込み
df = load_data(SHEET_URL)


# --- 品詞選択 ---
parts = st.multiselect(
    "品詞を選択してください（複数可）", 
    options=df["品詞"].unique()
)

# --- レッスン選択 ---
lessons = st.multiselect(
    "レッスンを選択してください（複数可）",
    options=df["レッスン"].unique()
)

# --- 出題方向選択 ---
direction = st.radio(
    "出題方向を選んでください",
    options=["日本語 → ドイツ語", "ドイツ語 → 日本語"]
)

# --- 出題数選択 ---
max_num = len(df)
initial_value = min(5, max_num)  # データ件数が5未満なら自動調整

num_questions = st.number_input(
    "出題数",
    min_value=1,
    max_value=max_num,
    value=initial_value,
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
        user_answers = {}

        st.write("各単語に回答してください:")

        # 入力フォーム
        for i, row in questions.iterrows():
            if direction == "日本語 → ドイツ語":
                user_answers[i] = st.text_input(f"{i+1}. {row['日本語']}", key=f"q_{i}")
            else:
                user_answers[i] = st.text_input(f"{i+1}. {row['ドイツ語']}", key=f"q_{i}")

        # 回答確認ボタン
        if st.button("回答を確認"):
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
