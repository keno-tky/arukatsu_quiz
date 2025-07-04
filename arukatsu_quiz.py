import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(
    page_title="チーム結果一覧",
    page_icon="📊",
    layout="wide"
)

# チームデータ（サンプル）
TEAM_DATA = {
    "SeawaterA": {
        "嶋": 13242,
        "仲井": 5476,
        "内藤（順）": 12577,
        "冨田": 10107,
        "★菅野": 17742,
        "吉川": 9352,
        "高島": 12742
    },
    "SeawaterB": {
        "★慶野": 8688,
        "平松": 7218,
        "久保田": 6868,
        "戸田": 7693,
        "澤村": 3844,
        "鈴木": 8601,
        "依田": 5865
    },
    "SeawaterC": {
        "★辻": 12627,
        "北条": 8786,
        "河田": 10624,
        "岩越": 8928,
        "財津": 9679,
        "内藤（洋）": 9041,
        "遠藤": 9388
    },
    "SeawaterD": {
        "浅見": 7261,
        "池田": 9538,
        "小原": 4566,
        "★青木": 14507,
        "加藤": 8000,
        "阿多": 7874,
        "谷口": 8187
    }
}

def show_team_table(team_name, member_data):
    """チームメンバーと平均を表示"""
    df = pd.DataFrame(member_data.items(), columns=["メンバー名", "歩数"])
    df.index = range(1, len(df) + 1)
    avg = sum(member_data.values()) / len(member_data)
    
    st.subheader(f"📌 {team_name}")
    st.caption(f"平均歩数: {avg:.0f} 歩")
    st.dataframe(df, use_container_width=True, height=280)

def main():
    st.title("📊 チーム別 歩数結果一覧")
    st.markdown("各チームのメンバーとその歩数、平均を表示します。　★：各チームの1位")

    cols = st.columns(2)
    teams = list(TEAM_DATA.items())
    
    for i, (team_name, members) in enumerate(teams):
        with cols[i % 2]:
            show_team_table(team_name, members)
            st.markdown("---")

if __name__ == "__main__":
    main()
