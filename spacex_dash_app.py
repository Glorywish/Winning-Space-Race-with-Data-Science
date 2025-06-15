import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load SpaceX launch data
spacex_df = pd.read_csv("Spacex.csv")

# Debugging: Check column names
print(spacex_df.columns)
print(spacex_df.head())  # Display first few rows for verification

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "SpaceX Launch Records Dashboard"

# Layout definition
app.layout = html.Div([
    html.H1("SpaceX Launch Records Dashboard", style={'textAlign': 'center'}),

    # Launch Site Dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] + 
                [{'label': site, 'value': site} for site in spacex_df['Launch_Site'].unique()],
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),

    # Payload Range Slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
        value=[0, 10000]
    ),

    # Pie Chart Section
    html.Div([
        dcc.Graph(id='success-pie-chart')
    ], style={'margin-top': '20px', 'display': 'flex', 'justify-content': 'center', 'width': '80%'}),

    # Scatter Plot Section - Enlarged for full visibility
    html.Div([
        dcc.Graph(id='success-payload-scatter-chart')
    ], style={'margin-top': '20px', 'width': '100%', 'height': '1400px', 'display': 'flex', 'justify-content': 'center'})
])

# Callback for Pie Chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == "ALL":
        # Count successful missions per site
        success_counts = spacex_df[spacex_df['Mission_Outcome'] == 'Success'].groupby('Launch_Site').size().reset_index(name='Success Count')
        fig = px.pie(success_counts, values='Success Count', names='Launch_Site', 
                     title='Total Success Launches by Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch_Site'] == selected_site]
        fig = px.pie(filtered_df, names='Mission_Outcome', 
                     title=f'Success Rate for {selected_site}')

    fig.update_layout(height=400, margin=dict(l=40, r=40, t=40, b=40))
    return fig

# Callback for Scatter Plot
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    # Filtering data based on payload range
    filtered_df = spacex_df[
        (spacex_df['PAYLOAD_MASS__KG_'] >= payload_range[0]) &
        (spacex_df['PAYLOAD_MASS__KG_'] <= payload_range[1])
    ]

    if selected_site != "ALL":
        filtered_df = filtered_df[filtered_df['Launch_Site'] == selected_site]

    fig = px.scatter(filtered_df, x='PAYLOAD_MASS__KG_', y='Mission_Outcome', 
                     color='Booster_Version', title='Payload vs. Launch Success')

    # Adjusting layout for full-page fit
    fig.update_layout(height=1400, width=1300, margin=dict(l=10, r=10, t=50, b=50))
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)