# Import required libraries
import pandas as pd
import dash
import plotly.express as px

from dash import Dash, dcc, html, Input, Output, callback


# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

dropdowndict = []
for name in spacex_df['Launch Site'].unique():
    dropdowndict += [{'label': name, 'value': name}]

print(dropdowndict)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                             options=[{'label': 'All Sites', 'value': 'ALL'}, *dropdowndict]),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider', min=0, max=10000, step=1000,
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])


# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_dropdown_value(launchsite):

    if launchsite == 'ALL':
        df = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').sum()
        df.rename(columns={'class': 'Successful Launches'}, inplace=True)
        fig = px.pie(df, values='Successful Launches', names=df.index, title='Successful Launches of all Sites')
    else:
        df = spacex_df[spacex_df['Launch Site'] == launchsite].groupby('class').sum()
        df.rename(index={0: 'Failure', 1: 'Success'}, inplace=True)
        df.rename(columns={'Flight Number': 'Number of Flights'}, inplace=True)
        fig = px.pie(df, values='Number of Flights', names=df.index, title=f'{launchsite} Site Success Breakdown',
                     color_discrete_map={'Failure': 'red', 'Success': 'green'})

    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('payload-slider', 'value'), Input('site-dropdown', 'value')]
)
def update_scatter_plot(payloadval, launchsite):
    if launchsite == 'ALL':
        fig = px.scatter(data_frame=spacex_df, x='Payload Mass (kg)', y='class', color='Booster Version Category')
    else:
        df = spacex_df[spacex_df['Launch Site'] == launchsite]
        df = df[df['Payload Mass (kg)'].between(*payloadval)]
        fig = px.scatter(df, x='Payload Mass (kg)', y='class', color='Booster Version Category')

    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
