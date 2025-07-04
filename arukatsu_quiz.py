import streamlit as st
import pandas as pd
import random
import json
from datetime import datetime

# ページ設定
st.set_page_config(
    page_title="歩数クイズアプリ",
    page_icon="🚶‍♂️",
    layout="wide"
)

# サンプルデータ
TEAM_DATA = {
    "チームA": {
        "田中太郎": 8510,
        "佐藤花子": 9200,
        "鈴木一郎": 7800,
        "高橋美咲": 10500,
        "伊藤健太": 6900,
        "渡辺さくら": 11200,
        "山田次郎": 8800
    },
    "チームB": {
        "中村直人": 9500,
        "小林優子": 8200,
        "加藤大輔": 10800,
        "吉田麻衣": 7600,
        "松本拓也": 9900,
        "井上あい": 8400,
        "木村慎二": 7200
    },
    "チームC": {
        "林真理": 10200,
        "清水健一": 8900,
        "山口美穂": 9600,
        "森田哲也": 7400,
        "池田沙織": 10900,
        "橋本勇気": 8100,
        "石川みどり": 9300
    },
    "チームD": {
        "斎藤光一": 9800,
        "長谷川恵": 8600,
        "村上翔太": 10400,
        "岡田理沙": 7900,
        "藤田和也": 9100,
        "近藤美由紀": 8700,
        "後藤雄太": 10600
    }
}

# 事前に指定する伏せるメンバー（各チーム2人ずつ）
HIDDEN_MEMBERS = {
    "チームA": ["佐藤花子", "高橋美咲"],
    "チームB": ["小林優子", "松本拓也"],
    "チームC": ["山口美穂", "池田沙織"],
    "チームD": ["長谷川恵", "村上翔太"]
}

def calculate_team_average(team_name):
    """チームの平均歩数を計算"""
    team_members = TEAM_DATA[team_name]
    return sum(team_members.values()) / len(team_members)

def initialize_session_state():
    """セッション状態の初期化"""
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'total_questions' not in st.session_state:
        st.session_state.total_questions = 10
    if 'quiz_data' not in st.session_state:
        st.session_state.quiz_data = []
    if 'answers' not in st.session_state:
        st.session_state.answers = []
    if 'quiz_finished' not in st.session_state:
        st.session_state.quiz_finished = False
    if 'player_name' not in st.session_state:
        st.session_state.player_name = ""
    if 'all_results' not in st.session_state:
        st.session_state.all_results = []

def generate_quiz_data(num_questions):
    """クイズデータの生成（事前指定されたメンバーを伏せる）"""
    quiz_data = []
    
    # 全メンバーの名前リストを作成
    all_names = []
    for team_members in TEAM_DATA.values():
        all_names.extend(team_members.keys())
    
    for _ in range(num_questions):
        question_data = {}
        all_hidden_names = []
        
        # 各チームで事前指定されたメンバーを伏せる
        for team_name, team_members in TEAM_DATA.items():
            members_list = list(team_members.items())
            hidden_members = HIDDEN_MEMBERS[team_name]
            
            # 表示用データと正解データを作成
            display_data = []
            correct_answers = {}
            
            for i, (name, steps) in enumerate(members_list):
                if name in hidden_members:
                    question_id = f"{team_name}_member_{i}"
                    display_data.append(("???", steps))
                    correct_answers[question_id] = name
                    all_hidden_names.append(name)
                else:
                    display_data.append((name, steps))
            
            question_data[team_name] = {
                "display_data": display_data,
                "correct_answers": correct_answers,
                "hidden_members": hidden_members
            }
        
        # 選択肢を作成（正解 + ダミー選択肢）
        available_dummy_names = [name for name in all_names if name not in all_hidden_names]
        num_dummies_needed = max(8 - len(all_hidden_names), 4)
        
        if len(available_dummy_names) >= num_dummies_needed:
            dummy_names = random.sample(available_dummy_names, num_dummies_needed)
        else:
            dummy_names = available_dummy_names
        
        # 選択肢リストを作成（正解 + ダミー）
        choices = all_hidden_names + dummy_names
        random.shuffle(choices)
        
        question_data["choices"] = choices
        question_data["all_correct_answers"] = {}
        
        # 全チームの正解を統合
        for team_name in TEAM_DATA.keys():
            question_data["all_correct_answers"].update(question_data[team_name]["correct_answers"])
        
        quiz_data.append(question_data)
    
    return quiz_data

def create_team_table(team_name, display_data):
    """チーム表の作成（平均歩数付き）"""
    df = pd.DataFrame(display_data, columns=["メンバー名", "平均歩数"])
    df.index = range(1, len(df) + 1)
    
    team_average = calculate_team_average(team_name)
    
    st.subheader(f"📊 {team_name}")
    st.caption(f"チーム平均: {team_average:.0f}歩")
    st.dataframe(df, use_container_width=True, height=280)

def save_result(player_name, score, total_possible, accuracy):
    """結果を保存"""
    result = {
        "player_name": player_name,
        "score": score,
        "total_possible": total_possible,
        "accuracy": accuracy,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.all_results.append(result)

def show_ranking():
    """ランキング表示"""
    if not st.session_state.all_results:
        st.info("まだ結果がありません。クイズを実行してください。")
        return
    
    # 正答率でソート
    sorted_results = sorted(st.session_state.all_results, key=lambda x: x["accuracy"], reverse=True)
    top_5 = sorted_results[:5]
    
    st.markdown("### 🏆 正解ランキング TOP5")
    
    for i, result in enumerate(top_5):
        rank_emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i]
        col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
        
        with col1:
            st.markdown(f"### {rank_emoji}")
        with col2:
            st.markdown(f"**{result['player_name']}**")
        with col3:
            st.markdown(f"{result['score']}/{result['total_possible']}問正解")
        with col4:
            st.markdown(f"**{result['accuracy']:.1f}%**")
    
    # 全結果の詳細表示
    if len(st.session_state.all_results) > 0:
        st.markdown("### 📊 全結果")
        results_df = pd.DataFrame(st.session_state.all_results)
        results_df = results_df.sort_values("accuracy", ascending=False)
        results_df["順位"] = range(1, len(results_df) + 1)
        results_df = results_df[["順位", "player_name", "score", "total_possible", "accuracy", "timestamp"]]
        results_df.columns = ["順位", "回答者名", "正解数", "総問題数", "正答率(%)", "実施日時"]
        st.dataframe(results_df, use_container_width=True)

def main():
    initialize_session_state()
    
    # タブの作成
    tab1, tab2 = st.tabs(["🎮 クイズ", "📊 結果"])
    
    with tab1:
        st.title("🚶‍♂️ 歩数クイズアプリ")
        st.markdown("---")
        
        if not st.session_state.quiz_started:
            # クイズ開始前の画面
            st.markdown("### 📋 ゲームルール")
            st.markdown("""
            1. **4チーム同時出題**: 全4チームが同時に表示されます
            2. **名前が伏せられる**: 事前に指定された各チーム2人のメンバー名が「???」で表示されます
            3. **選択式回答**: 選択肢から正しい名前を選んで回答してください
            4. **正答率を競う**: 全問題終了後、正答率が表示されます
            """)
            
            # 伏せられるメンバーの表示
            st.markdown("### 👥 伏せられるメンバー")
            cols = st.columns(4)
            for i, (team_name, hidden_members) in enumerate(HIDDEN_MEMBERS.items()):
                with cols[i]:
                    st.markdown(f"**{team_name}**")
                    for member in hidden_members:
                        st.write(f"• {member}")
            
            st.markdown("### ⚙️ 設定")
            player_name = st.text_input("回答者名", placeholder="お名前を入力してください")
            num_questions = st.slider("問題数", min_value=5, max_value=15, value=10)
            st.session_state.total_questions = num_questions
            
            if st.button("🎮 クイズを開始", type="primary", use_container_width=True):
                if player_name.strip():
                    st.session_state.player_name = player_name.strip()
                    st.session_state.quiz_started = True
                    st.session_state.quiz_data = generate_quiz_data(num_questions)
                    st.session_state.current_question = 0
                    st.session_state.score = 0
                    st.session_state.answers = []
                    st.session_state.quiz_finished = False
                    st.rerun()
                else:
                    st.warning("⚠️ 回答者名を入力してください")
        
        elif not st.session_state.quiz_finished:
            # クイズ実行中の画面
            current_q = st.session_state.current_question
            total_q = st.session_state.total_questions
            
            # プレイヤー名と進捗表示
            st.markdown(f"### 👤 回答者: {st.session_state.player_name}")
            progress = (current_q) / total_q
            st.progress(progress)
            st.markdown(f"### 問題 {current_q + 1} / {total_q}")
            
            # 現在のスコア表示
            if current_q > 0:
                total_answered = sum(len(q_data["all_correct_answers"]) for q_data in st.session_state.quiz_data[:current_q])
                accuracy = (st.session_state.score / total_answered) * 100
                st.metric("現在の正答率", f"{accuracy:.1f}%")
            
            # 4チーム表示
            quiz_item = st.session_state.quiz_data[current_q]
            
            st.markdown("### 📊 チーム一覧")
            # 2x2のレイアウトで4チーム表示
            col1, col2 = st.columns(2)
            team_names = list(TEAM_DATA.keys())
            
            with col1:
                create_team_table(team_names[0], quiz_item[team_names[0]]["display_data"])
                st.markdown("<br>", unsafe_allow_html=True)
                create_team_table(team_names[2], quiz_item[team_names[2]]["display_data"])
            
            with col2:
                create_team_table(team_names[1], quiz_item[team_names[1]]["display_data"])
                st.markdown("<br>", unsafe_allow_html=True)
                create_team_table(team_names[3], quiz_item[team_names[3]]["display_data"])
            
            st.markdown("---")
            st.markdown("### 💭 回答を選択してください")
            
            # 回答選択フォーム
            user_answers = {}
            correct_answers = quiz_item["all_correct_answers"]
            choices = ["選択してください"] + quiz_item["choices"]
            
            # 質問をチーム別に整理
            questions_by_team = {}
            for question_id in correct_answers.keys():
                team_name = question_id.split('_member_')[0]
                if team_name not in questions_by_team:
                    questions_by_team[team_name] = []
                questions_by_team[team_name].append(question_id)
            
            # チーム別に回答選択肢を表示
            cols = st.columns(2)
            team_list = list(questions_by_team.keys())
            
            for i, team_name in enumerate(team_list):
                with cols[i % 2]:
                    st.markdown(f"**{team_name}**")
                    for question_id in questions_by_team[team_name]:
                        member_index = int(question_id.split('_member_')[1])
                        user_answers[question_id] = st.selectbox(
                            f"位置 {member_index + 1} の名前:",
                            choices,
                            key=f"answer_{current_q}_{question_id}"
                        )
            
            # 回答送信
            if st.button("📝 回答を送信", type="primary", use_container_width=True):
                if all(answer != "選択してください" for answer in user_answers.values()):
                    # 採点
                    question_score = 0
                    results = {}
                    
                    for question_id, user_answer in user_answers.items():
                        correct_answer = correct_answers[question_id]
                        is_correct = user_answer == correct_answer
                        results[question_id] = {
                            "user_answer": user_answer,
                            "correct_answer": correct_answer,
                            "is_correct": is_correct
                        }
                        if is_correct:
                            question_score += 1
                    
                    st.session_state.score += question_score
                    st.session_state.answers.append(results)
                    
                    # 結果表示
                    st.markdown("### 📊 この問題の結果")
                    
                    # チーム別に結果を表示
                    result_cols = st.columns(2)
                    team_results = {}
                    
                    for question_id, result in results.items():
                        team_name = question_id.split('_member_')[0]
                        if team_name not in team_results:
                            team_results[team_name] = []
                        team_results[team_name].append((question_id, result))
                    
                    for i, (team_name, team_result_list) in enumerate(team_results.items()):
                        with result_cols[i % 2]:
                            st.markdown(f"**{team_name}**")
                            for question_id, result in team_result_list:
                                member_index = int(question_id.split('_member_')[1])
                                if result["is_correct"]:
                                    st.success(f"位置 {member_index + 1}: ✅ {result['correct_answer']}")
                                else:
                                    st.error(f"位置 {member_index + 1}: ❌ {result['user_answer']} → {result['correct_answer']}")
                    
                    st.info(f"この問題のスコア: {question_score} / {len(correct_answers)}")
                    
                    # 次の問題へ
                    if current_q + 1 < total_q:
                        if st.button("➡️ 次の問題へ", use_container_width=True):
                            st.session_state.current_question += 1
                            st.rerun()
                    else:
                        if st.button("🏁 結果を見る", use_container_width=True):
                            st.session_state.quiz_finished = True
                            st.rerun()
                else:
                    st.warning("⚠️ すべての回答を選択してください")
        
        else:
            # 結果画面
            st.markdown(f"### 🎉 {st.session_state.player_name}さん、クイズお疲れ様でした！")
            
            total_possible = sum(len(quiz_item["all_correct_answers"]) for quiz_item in st.session_state.quiz_data)
            final_accuracy = (st.session_state.score / total_possible) * 100
            
            # 結果を保存
            save_result(st.session_state.player_name, st.session_state.score, total_possible, final_accuracy)
            
            # 結果表示
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("正解数", f"{st.session_state.score} / {total_possible}")
            with col2:
                st.metric("正答率", f"{final_accuracy:.1f}%")
            with col3:
                if final_accuracy >= 90:
                    grade = "🥇 素晴らしい！"
                elif final_accuracy >= 70:
                    grade = "🥈 良くできました！"
                elif final_accuracy >= 50:
                    grade = "🥉 もう少し！"
                else:
                    grade = "💪 頑張りましょう！"
                st.metric("評価", grade)
            
            # 詳細結果
            st.markdown("### 📋 詳細結果")
            for i, (quiz_item, answers) in enumerate(zip(st.session_state.quiz_data, st.session_state.answers)):
                with st.expander(f"問題 {i + 1}"):
                    # チーム別に結果を整理
                    team_results = {}
                    for question_id, result in answers.items():
                        team_name = question_id.split('_member_')[0]
                        if team_name not in team_results:
                            team_results[team_name] = []
                        team_results[team_name].append((question_id, result))
                    
                    # チーム別に表示
                    for team_name, team_result_list in team_results.items():
                        st.markdown(f"**{team_name}**")
                        for question_id, result in team_result_list:
                            member_index = int(question_id.split('_member_')[1])
                            status = "✅" if result["is_correct"] else "❌"
                            st.write(f"{status} 位置 {member_index + 1}: {result['user_answer']} → {result['correct_answer']}")
            
            # リスタート
            if st.button("🔄 もう一度プレイ", type="primary", use_container_width=True):
                # 結果は保持したまま、クイズ関連の状態のみリセット
                st.session_state.quiz_started = False
                st.session_state.current_question = 0
                st.session_state.score = 0
                st.session_state.quiz_data = []
                st.session_state.answers = []
                st.session_state.quiz_finished = False
                st.session_state.player_name = ""
                st.rerun()
    
    with tab2:
        st.title("📊 クイズ結果")
        st.markdown("---")
        show_ranking()
        
        # 結果リセットボタン
        if st.session_state.all_results:
            if st.button("🗑️ 全結果をリセット", type="secondary"):
                st.session_state.all_results = []
                st.rerun()

if __name__ == "__main__":
    main()