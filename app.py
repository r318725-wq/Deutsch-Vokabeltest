st.write("各単語に回答してください:")

user_answers = st.session_state.get('user_answers', {})

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

# 結果表示
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
