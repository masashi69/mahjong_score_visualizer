import pandas as pd
import plotly.graph_objects as go
import sys
import numpy as np

df = pd.read_csv(sys.argv[1])
start_date = df['gameid'].head(1).to_numpy()[0][:6]
end_date = df['gameid'].tail(1).to_numpy()[0][:6]

# 対戦相手とのスコア差分を計算するためのセルフマージ
merged = pd.merge(df, df, on='gameid', suffixes=('_me', '_opponent'))

# 自分自身との対戦を除外
merged = merged[merged['player_me'] != merged['player_opponent']]

# 自分のスコア - 相手のスコア」
merged['score_diff'] = merged['score_me'] - merged['score_opponent']

# 名前ごとの平均スコア差分を集計（ピボットテーブル作成）
all_players = sorted(df['player'].unique())

heatmap_df = merged.pivot_table(
    index='player_me',
    columns='player_opponent',
    values='score_diff',
    aggfunc='mean'
)

heatmap_df = heatmap_df.reindex(index=all_players, columns=all_players)

# 対局回数算出
count_df = merged.pivot_table(
    index='player_me',
    columns='player_opponent',
    values='score_diff',
    aggfunc='count'
)

z_text = np.where(
    heatmap_df.notna(),
    heatmap_df.round(1).astype(str) + "<br>(" + count_df.astype(str) + "回)",
    ""
)

# ヒートマップの作成
fig = go.Figure(data=go.Heatmap(
    z=heatmap_df.values,
    x=heatmap_df.columns,
    y=heatmap_df.index,
    colorscale='RdBu',
    zmid=0,
    text=z_text,
    texttemplate="%{text}",
    hoverinfo='z',
    colorbar=dict(title="平均スコア差")
))

fig.update_layout(
    title=f'対戦相手別 相性ヒートマップ (自分 - 相手の平均点差) & 対局回数, 期間: {start_date} - {end_date}',
    xaxis_title='対戦相手',
    yaxis_title='自分',
    width=1200,
    height=1000
)

fig.write_image("対局相性ヒートマップ.png")
