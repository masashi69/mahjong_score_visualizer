import plotly.graph_objects as go
from plotly.subplots import make_subplots
from summary import *
import sys

df = pd.read_csv(sys.argv[1])
result = CalculateScore(df)
playerlist = df['player'].unique().tolist()

for score in result:

    playername = playerlist.index(score[0])
    scoredf = df[df['player'] == playerlist[playername]].copy()
    scoredf = scoredf.sort_values('gameid')
    colors = ['royalblue' if val >= 0 else 'darkorange' for val in scoredf['score']]

    # 1. サブプロットの枠組みを作成
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.6, 0.4],
        specs=[[{"secondary_y": True, "type": "xy"}, {"type": "polar"}]],
        subplot_titles=("スコア・順位推移", "プレイスタイル分析"),
    )

    # --- 左側：スコア推移グラフ (2軸) ---
    # スコア（棒グラフ）
    fig.add_trace(
        go.Bar(x=scoredf['gameid'], y=scoredf['score'], name="スコア", 
               marker_color=colors, 
               opacity=0.6),
               row=1, col=1, secondary_y=False
    )

    # 順位（折れ線グラフ）
    fig.add_trace(
        go.Scatter(x=scoredf['gameid'], y=scoredf['rank'], name="順位", mode="lines+markers",
            line=dict(color='firebrick', width=2)
            ),
            row=1, col=1, secondary_y=True
    )

    # --- 右側：レーダーチャート ---
    avgscore = (score[2] + 80) / 160
    avgrank = (4-score[4]) / 3
    takefirst = score[5] / 100
    avoidlast = score[6] / 100

    fig.add_trace(
        go.Scatterpolar(
          r=[avgscore, avgrank, takefirst, avoidlast], # 各項目の値
          theta=['平均pt', '平均順位', 'トップ率', '4着回避率'],
          fill='toself',
          name='平均スコア・着順'
        ),
        row=1, col=2
    )

    # --- レイアウト設定 ---

    # 左軸（スコア）
    fig.update_yaxes(title_text="スコア", secondary_y=False, row=1, col=1)
    # 右軸（順位）
    fig.update_yaxes(title_text="順位", secondary_y=True, autorange="reversed", dtick=1, row=1, col=1)

    # レーダーチャートの回転設定
    fig.update_polars(
        angularaxis=dict(rotation=90, direction="clockwise"),
        radialaxis=dict(range=[0, 1]),
    )

    fig.update_layout(height=500, title_text="個人戦績ダッシュボード", showlegend=True, margin=dict(t=120))
    fig.update_annotations(yshift=20)

    fig.write_image(f"{score[0]}_result_graph.png", width=1200, height=800, scale=2)
