import pandas as pd
import streamlit as st
import random

# GoogleスプレッドシートのCSVリンク
SHEET_URL = "https://docs.google.com/spreadsheets/d/1-B3-c9xsGxAbh6iolhiafa4QeqsrXdQQvO4XIL-nPoQ/export?format=csv"

# データ読み込み関数（キャッシュ付き）
@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()  # 列名の空白を削除
    return df

# データを読み込む
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
initial_value = min(5, max_num)  # データ数が5未満ならそれに合わせる

num_questions = st.number_input(
    "出題数",
    min_value=1,
    max_value=max_num,
    value=initial_value,
    step=1
)

# --- テスト開始 ---
if st.button("テスト開始"):

    # 条件に合う単語を抽出
    filtered = df
    if parts:
        filtered = filtered[filtered["品詞"].isin(parts)]
    if lessons:
        filtered = filtered[filtered["レッスン"].isin(lessons)]

    if filtered.empty:
        st.warning("選択条件に合う単語がありません。")
    else:
        # 出題数分ランダム抽出
        questions = filtered.sample(min(num_questions, len(filtered)))

        score = 0
        for i, row in questions.iterrows():
            if direction == "日本語 → ドイツ語":
                answer = st.text_input(f"{i+1}. {row['日本語']}", key=f"q_{i}")
                if answer.strip().lower() == str(row["ドイツ語"]).strip().lower():
                    st.success("正解！")
                    score += 1
                elif answer != "":
                    st.error(f"不正解。正解は {row['ドイツ語']} です")
            else:
                answer = st.text_input(f"{i+1}. {row['ドイツ語']}", key=f"q_{i}")
                if answer.strip().lower() == str(row["日本語"]).strip().lower():
                    st.success("正解！")
                    score += 1
                elif answer != "":
                    st.error(f"不正解。正解は {row['日本語']} です")

        st.write(f"あなたのスコア: {score} / {len(questions)}")
