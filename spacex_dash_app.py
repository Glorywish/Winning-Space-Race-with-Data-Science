import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load dataset
spacex_df = pd.read_csv("spacex_launch_dash.csv")

print("🧾 Columns in dataset:")
print(spacex_df.columns.tolist())

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "SpaceX Launch Records Dashboard"

# App layout
app.layout = html.Div([
    html.H1("SpaceX Launch Records Dashboard", style={'textAlign': 'center'}),

    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] +
                [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),

    html.Div([
        dcc.Graph(id='success-pie-chart')
    ], style={'margin-top': '20px', 'width': '80%', 'margin': 'auto'}),

    html.Div([
        html.Label("Payload range (Kg):", style={'font-weight': 'bold'}),
        dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10000,
            step=1000,
            marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
            value=[0, 10000]
        )
    ], style={'margin': '40px 10% 20px 10%'}),

    html.Div([
        dcc.Graph(id='success-payload-scatter-chart')
    ], style={'width': '100%', 'display': 'flex', 'justify-content': 'center'})
])

# Pie chart callback
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        success_counts = spacex_df[spacex_df['class'] == 1] \
            .groupby('Launch Site').size().reset_index(name='Success Count')
        fig = px.pie(success_counts, values='Success Count', names='Launch Site',
                     title='Total Success Launches by Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(filtered_df, names='class',
                     title=f'Success vs Failure for {selected_site}')
    fig.update_layout(height=400, margin=dict(l=40, r=40, t=40, b=40))
    return fig

# Scatter plot callback
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ].copy()

    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Booster Version'],
        title=f'Correlation between Payload and Outcome for {"All Sites" if selected_site == "ALL" else selected_site}',
        labels={
            'class': 'Launch Outcome',
            'Payload Mass (kg)': 'Payload Mass (kg)',
            'Booster Version Category': 'Booster Version Category'
        }
    )

    fig.update_traces(marker=dict(size=10))
    fig.update_layout(
        height=300,
        width=1200,
        margin=dict(l=10, r=10, t=60, b=100),
        yaxis=dict(
            tickmode='array',
            tickvals=[0, 1],
            ticktext=['0 = Failure', '1 = Success'],
            title='Launch Outcome'
        ),
        xaxis_title='Payload Mass (kg)',
        legend_title='Booster Version Category',
        legend=dict(
            orientation='v',
            yanchor='top',
            y=1,
            xanchor='left',
            x=1.02,
            font=dict(size=12)
        )
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)