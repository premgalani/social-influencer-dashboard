# dashboard.py

"""
Interactive Social Influencer Dashboard
Focuses on your existing social_influencers_with_categories.csv data.

Dependencies:
    pip install dash plotly pandas
"""

import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# ===== CONFIG: point to your CSV file =====
DATA_PATH = '/Users/premgalani/Desktop/VTION_Influencer_Data/social_influencers_with_categories.csv'
# ==========================================

# 1) Load data and normalize column names
df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.strip().str.lower().str.replace(r'\s+', '_', regex=True)

# Expected columns: influencer_name, handle_name, event_count, unique_user_count,
# brands, platform, total_brand_collabs, categories

# 2) Prepare scatter DataFrame (event_count vs unique_user_count)
scatter_df = df[['handle_name', 'event_count', 'unique_user_count', 'total_brand_collabs']].copy()
scatter_df.columns = ['handle', 'event_count', 'unique_user_count', 'brand_collabs']

# 3) Initialize Dash app
app = Dash(__name__)

app.layout = html.Div(style={'padding':'20px','fontFamily':'Arial'}, children=[
    html.H1("Social Influencer Dashboard", style={'textAlign':'center'}),

    # Influencer dropdown
    dcc.Dropdown(
        id='influencer-dropdown',
        options=[{'label': name, 'value': name} for name in df['handle_name']],
        value=df['handle_name'].iloc[0],
        style={'width':'50%','margin':'auto'}
    ),
    html.Br(),

    # KPI cards container
    html.Div(id='kpi-container', style={'display':'flex','justifyContent':'space-around'}),
    html.Br(),

    # Brand bar chart & category pie chart side by side
    html.Div(style={'display':'flex'}, children=[
        dcc.Graph(id='brand-bar-chart', style={'flex':'1'}),
        dcc.Graph(id='category-pie-chart', style={'flex':'1'})
    ]),
    html.Br(),

    # Event Count vs Unique Users scatter plot
    dcc.Graph(id='events-vs-users-scatter'),
    html.Br(),

    # Brand collaborations treemap
    dcc.Graph(id='brand-treemap'),
])

@app.callback(
    Output('kpi-container', 'children'),
    Output('brand-bar-chart', 'figure'),
    Output('category-pie-chart', 'figure'),
    Output('events-vs-users-scatter', 'figure'),
    Output('brand-treemap', 'figure'),
    Input('influencer-dropdown', 'value')
)
def update_dashboard(selected_handle):
    # Fetch selected influencer row
    row = df[df['handle_name'] == selected_handle].iloc[0]

    # KPI values
    ev = int(row['event_count'])
    uu = int(row['unique_user_count'])
    tb = int(row['total_brand_collabs'])

    # Build KPI cards
    cards = [
        html.Div([html.H3("Event Count"), html.P(f"{ev:,}")],
                 style={'border':'1px solid #ccc','padding':'10px','borderRadius':'5px','width':'30%'}),
        html.Div([html.H3("Unique Users"), html.P(f"{uu:,}")],
                 style={'border':'1px solid #ccc','padding':'10px','borderRadius':'5px','width':'30%'}),
        html.Div([html.H3("Total Brand Collabs"), html.P(f"{tb:,}")],
                 style={'border':'1px solid #ccc','padding':'10px','borderRadius':'5px','width':'30%'}),
    ]

    # Parse brands & categories lists
    brands     = [b.strip() for b in str(row['brands']).split(',') if b.strip()]
    categories = [c.strip() for c in str(row['categories']).split(',') if c.strip()]
    bc_df = pd.DataFrame({'brand': brands, 'category': categories})

    # Brand Collaboration Bar Chart
    bar_fig = px.bar(bc_df, x='brand', color='category', title="Brand Collaborations")

    # Category Breakdown Pie Chart
    pie_df = bc_df['category'].value_counts().reset_index()
    pie_df.columns = ['category','count']
    pie_fig = px.pie(pie_df, names='category', values='count', title="Category Breakdown")

    # Event Count vs Unique Users Scatter
    scatter_fig = px.scatter(
        scatter_df, x='event_count', y='unique_user_count',
        hover_data=['handle'], title="Event Count vs Unique Users"
    )
    # Highlight selected influencer
    scatter_fig.add_vline(x=ev, line_dash="dash", annotation_text="Selected", annotation_position="top")
    scatter_fig.add_hline(y=uu, line_dash="dash", annotation_text="Selected", annotation_position="right")

    # Brand Collaborations Treemap
    tree_fig = px.treemap(bc_df, path=['category','brand'],
                          values=[1]*len(bc_df), title="Brand Collaborations Treemap")

    return cards, bar_fig, pie_fig, scatter_fig, tree_fig

if __name__ == '__main__':
    app.run(debug=True)
