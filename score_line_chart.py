import plotly.graph_objects as go
from plotly.subplots import make_subplots
from summary import *
import sys

df = pd.read_csv(sys.argv[1])

# クォータ列作成
df['date'] = pd.to_datetime(df['gameid'].astype(str).str[:6], format='%Y%m')
df['quarter'] = df['date'].dt.to_period('Q').astype(str)

result = CalculateScore(df)
playerlist = df['player'].unique().tolist()

for score in result:

    player_name = score[0]
    scoredf = df[df['player'] == player_name].copy()
    scoredf = scoredf.sort_values('gameid')
    colors = ['royalblue' if val >= 0 else 'darkorange' for val in scoredf['score']]

    quarters = sorted(scoredf['quarter'].unique())
    num_quarters = len(quarters)

    # --- 1. サブプロットのレイアウト枠組みを自動計算 ---
    # 1行目は総合。2行目以降に各クォータを配置するため、総行数は「1 + クォータ数」
    total_rows = 1 + num_quarters

    # 各行のサブプロットのタイプを指定（左: xy軸、右: 極座標polar）
    row_specs = [[{"secondary_y": True, "type": "xy"}, {"type": "polar"}] for _ in range(total_rows)]

    # 各サブプロットのタイトルを生成
    subplot_titles = ["総合：スコア・順位推移", "総合：プレイスタイル分析"]
    for q in quarters:
        subplot_titles.extend([f"{q}：スコア・順位推移", f"{q}：プレイスタイル分析"])

    fig = make_subplots(
        rows=total_rows, cols=2,
        column_widths=[0.6, 0.4],
        specs=row_specs,
        subplot_titles=subplot_titles,
        vertical_spacing=0.16 # 縦のグラフ間の隙間を調整
    )
    def add_dashboard_row(scoredf, row_idx, summary_score):
        colors = ['royalblue' if val >= 0 else 'darkorange' for val in scoredf['score']]

        # 左側：スコア（棒グラフ）
        fig.add_trace(
            go.Bar(x=scoredf['gameid'], y=scoredf['score'], name="スコア",
                   marker_color=colors, opacity=0.6, showlegend=(row_idx == 1)),
            row=row_idx, col=1, secondary_y=False
        )
        # 左側：順位（折れ線グラフ）
        fig.add_trace(
            go.Scatter(x=scoredf['gameid'], y=scoredf['rank'], name="順位", mode="lines+markers",
                       line=dict(color='firebrick', width=2), showlegend=(row_idx == 1)),
            row=row_idx, col=1, secondary_y=True
        )
        # 右側：レーダーチャート用の計算
        avgscore = (summary_score[2] + 80) / 160
        avgrank = (4 - summary_score[4]) / 3
        takefirst = summary_score[5] / 100
        avoidlast = summary_score[6] / 100

        fig.add_trace(
            go.Scatterpolar(
                r=[avgscore, avgrank, takefirst, avoidlast],
                theta=['平均pt', '平均順位', 'トップ率', '4着回避率'],
                fill='toself', name='平均スコア・着順', showlegend=(row_idx == 1),
                fillcolor='rgba(0, 170, 110, 0.3)',
                line=dict(color='rgb(0, 170, 110)', width=2)
            ),
            row=row_idx, col=2
        )

        # 各行個別の軸設定
        fig.update_yaxes(title_text="スコア", secondary_y=False, row=row_idx, col=1)
        fig.update_yaxes(title_text="順位", secondary_y=True, autorange="reversed", dtick=1, row=row_idx, col=1)
        fig.update_xaxes(nticks=16, row=row_idx, col=1)

    # --- 2. データのプロット実行 ---
    # 総合データの描画
    add_dashboard_row(scoredf, 1, score)

    # クォータごとの描画
    for idx, q in enumerate(quarters):
        current_row = idx + 2
        q_df = scoredf[scoredf['quarter'] == q]

        # クォータ個別の集計処理（CalculateScore関数と同じロジックを通すための擬似df作成）
        q_summary = CalculateScore(df[df['quarter'] == q])
        # このクォータにおける該当プレイヤーの成績を取り出す
        q_score = [s for s in q_summary if s[0] == player_name][0]

        add_dashboard_row(q_df, current_row, q_score)

    # レーダーチャートの回転設定
    fig.update_polars(
        angularaxis=dict(rotation=90, direction="clockwise"),
        radialaxis=dict(range=[0, 1]),
    )

    # グラフの行数に応じて、画像の縦幅（height）を引き伸ばし
    dynamic_height = 500 * total_rows

    fig.update_layout(
        height=dynamic_height,
        title_text=f"{player_name} ：個人戦績ダッシュボード (総合 & クォータ別)",
        showlegend=True,
        margin=dict(t=120, b=50)
    )
    fig.update_annotations(yshift=25)

    # 画像として保存
    fig.write_image(f"{player_name}_result_graph.png", width=1200, height=dynamic_height, scale=2)
