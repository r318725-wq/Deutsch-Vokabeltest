import streamlit as st
import pandas as pd

st.set_page_config(page_title="ドイツ語単語テスト", page_icon="🇩🇪")

st.title("🇩🇪 ドイツ語単語テスト")
st.caption("最新データ：スプレッドシートから自動読み込み")

# === GoogleスプレッドシートのCSVリンク ===
import pandas as pd
import streamlit as st

SHEET_URL = "https://docs.google.com/spreadsheets/d/1-B3-c9xsGxAbh6iolhiafa4QeqsrXdQQvO4XIL-nPoQ/export?format=csv"

@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()  # 列名の空白を削除
    return df

# データ読み込み
df = load_data(SHEET_URL)

# 列名を確認
st.write(df.columns)

# 例：品詞の選択肢
parts = st.multiselect("品詞を選択", df["品詞"].unique())

# データ読み込み
try:
    df = load_data(SHEET_URL)
except Exception as e:
    st.error("❌ スプレッドシートの読み込みに失敗しました。URLを確認してください。")
    st.stop()

# --- テスト条件 ---
parts = st.multiselect("品詞を選択", df["品詞"].unique())
lessons = st.multiselect("レッスンを選択", sorted(df["レッスン"].unique()))
direction = st.radio("出題方向を選択", ["日本語 → ドイツ語", "ドイツ語 → 日本語"])
num_questions = st.slider("出題数", 1, 30, 5)

# --- フィルタリング ---
filtered = df.copy()
if parts:
    filtered = filtered[filtered["品詞"].isin(parts)]
if lessons:
    filtered = filtered[filtered["レッスン"].isin(lessons)]

# --- 出題 ---
if st.button("📝 テスト開始！"):
    if len(filtered) == 0:
        st.warning("条件に合う単語がありません。")
    else:
        questions = filtered.sample(min(num_questions, len(filtered)))
        score = 0
        st.write("---")

        for i, row in enumerate(questions.itertuples(), 1):
            if direction == "日本語 → ドイツ語":
                question, answer = row.日本語, row.ドイツ語
            else:
                question, answer = row.ドイツ語, row.日本語

            user_input = st.text_input(f"{i}. {question}", key=f"q{i}")

            if user_input:
                if user_input.strip().lower() == answer.strip().lower():
                    st.success(f"✅ 正解！（{answer}）")
                    score += 1
                else:
                    st.error(f"❌ 不正解。正解は「{answer}」")

        st.write("---")
        st.info(f"🎯 結果：{score}/{len(questions)} 正解（{score/len(questions)*100:.1f}%）")

st.caption("Made with ❤️ by ChatGPT & Streamlit")
