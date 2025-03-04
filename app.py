import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set page configuration
st.set_page_config(page_title="Big West Basketball Analytics", layout="wide")
st.title("Big West Basketball Analytics Dashboard")

# Load data
@st.cache_data
def load_data():
    file_path = "BigWestCareerRankings.csv"
    return pd.read_csv(file_path)

df = load_data()

# Set visualization style
sns.set(style="whitegrid")
custom_palette = sns.color_palette("husl", n_colors=df["TEAM"].nunique())
team_colors = dict(zip(df["TEAM"].unique(), custom_palette))

# Highlight UC Santa Barbara
highlight_team = "UC Santa Barbara"
team_colors[highlight_team] = "red"

# Select relevant statistics
metrics = ["ORTG", "EFG", "TS", "3P", "2P", "AST", "TO", "STL", "BLK", "USG", "BPM"]
df_numeric = df[["PLAYER", "TEAM"] + metrics].dropna()

# Sidebar filters
st.sidebar.header("Filters")
selected_team = st.sidebar.multiselect(
    "Select Teams",
    options=df["TEAM"].unique(),
    default=[highlight_team]
)

# Filter data based on selection
filtered_data = df_numeric if not selected_team else df_numeric[df_numeric["TEAM"].isin(selected_team)]

# Top Players Section
st.header("Top Players Analysis")
col1, col2 = st.columns(2)

with col1:
    # Top players by BPM
    st.subheader("Top Players by Box Plus/Minus (BPM)")
    fig, ax = plt.subplots(figsize=(10, 6))
    top_players = filtered_data.nlargest(10, "BPM")
    sns.barplot(data=top_players, x="BPM", y="PLAYER", hue="TEAM", palette=team_colors)
    plt.xlabel("Box Plus/Minus (BPM)")
    plt.ylabel("Player")
    st.pyplot(fig)

with col2:
    # Offensive Rating vs True Shooting
    st.subheader("Offensive Rating vs. True Shooting %")
    fig, ax = plt.subplots(figsize=(10, 6))
    filtered_players = pd.concat([
        filtered_data.nlargest(20, "ORTG"),
        filtered_data.nsmallest(20, "ORTG")
    ])
    sns.scatterplot(data=filtered_players, x="ORTG", y="TS", hue="TEAM", alpha=0.7, palette=team_colors)
    plt.xlabel("Offensive Rating (ORTG)")
    plt.ylabel("True Shooting % (TS)")
    st.pyplot(fig)

# Radar Chart
st.header("Player Comparison Radar Chart")
def radar_chart(players_df, metrics):
    labels = np.array(metrics)
    num_vars = len(labels)
    
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    min_vals = players_df[metrics].min()
    max_vals = players_df[metrics].max()
    scaled_players_df = (players_df[metrics] - min_vals) / (max_vals - min_vals)
    
    for _, row in scaled_players_df.iterrows():
        team = players_df.loc[row.name, "TEAM"]
        color = "red" if team == highlight_team else "gray"
        values = row.values.flatten().tolist()
        values += values[:1]
        ax.plot(angles, values, label=players_df.loc[row.name, "PLAYER"], color=color)
        ax.fill(angles, values, alpha=0.2, color=color)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.2)
    plt.title("Top Players Comparison")
    return fig

# Allow user to select number of top players to compare
num_players = st.slider("Select number of players to compare", 2, 10, 5)
radar_metrics = ["ORTG", "TS", "USG", "AST", "BPM"]
top_players_radar = filtered_data.nlargest(num_players, "BPM")
radar_fig = radar_chart(top_players_radar, radar_metrics)
st.pyplot(radar_fig)

# Additional Statistics
st.header("Team Statistics")
col3, col4 = st.columns(2)

with col3:
    # Box Plot for True Shooting %
    st.subheader("True Shooting % Distribution by Team")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=filtered_data, x="TEAM", y="TS")
    plt.xticks(rotation=45)
    plt.xlabel("Team")
    plt.ylabel("True Shooting % (TS)")
    st.pyplot(fig)

with col4:
    # Usage Rate vs Assist/Turnover Ratio
    st.subheader("Usage Rate vs. Assist/Turnover Ratio")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=filtered_data, x="USG", y="AST", hue="TEAM", alpha=0.7, palette=team_colors)
    plt.xlabel("Usage Rate (USG)")
    plt.ylabel("Assists (AST)")
    st.pyplot(fig)

# Add data table with sortable columns
st.header("Player Statistics Table")
st.dataframe(
    filtered_data[["PLAYER", "TEAM"] + metrics].sort_values("BPM", ascending=False),
    hide_index=True
) 