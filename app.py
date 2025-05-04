from dash import Dash, html, dcc, Input, Output
from data_processing.process_data import load_and_clean_data
from data_processing.process_data import get_client_details
from data_processing.process_data import get_monthly_details
from data_processing.process_data import get_kpis
import plotly.express as px
import plotly.graph_objects as go


input_file = ('data/Sales_20240301_20250228.csv')
df = load_and_clean_data(input_file)
client_details = get_client_details(df)
monthly_details = get_monthly_details(df)
kpis = get_kpis(df)

# sliding scale histograms
session_hist = px.histogram(
    df,
    x='Total',
    nbins=40,
    title='Sliding Scale Distribution by Session Count'
)
session_hist.update_layout(xaxis_title='Session Charge',
                           yaxis_title='Session Count')
session_hist.update_xaxes(range=[0, None])

client_hist = px.histogram(client_details, x='Average Charged', nbins=30,
                           title='Sliding Scale Distribution by Client Count')
client_hist.update_layout(xaxis_title='Average Charged',
                          yaxis_title='Client Count')
client_hist.update_xaxes(range=[0, None])

line_fig = px.line(
    monthly_details,
    x='Month',
    y='# of Sessions',
    title='Sessions per Month'
)

# KPI Cards
fig4 = go.Figure()

# Indicators
indicators = [
    {'title': 'Days Worked',
     'value': kpis.get('Days Worked'),
     'row': 0, 'column': 0},
    {'title': 'Days with Clients',
     'value': kpis.get('Days with Clients'),
     'row': 0, 'column': 1},
    {'title': 'Total Sessions',
     'value': kpis.get('Total Sessions'),
     'row': 0, 'column': 2},
    {'title': 'Avg Sessions per Day',
     'value': kpis.get('Avg Sessions per Day'),
     'row': 1, 'column': 0},
    {'title': 'Unique Clients',
     'value': kpis.get('Unique Clients'),
     'row': 1, 'column': 1},
    {'title': 'Avg Rate Charged',
     'value': kpis.get('Avg Rate Charged'),
     'row': 1, 'column': 2},
    {'title': 'Total Revenue',
     'value': kpis.get('Total Revenue'),
     'row': 2, 'column': 1},
]

for ind in indicators:
    fig4.add_trace(go.Indicator(
        mode='number',
        value=ind['value'],
        title={'text': ind['title'], 'font': {'size': 18}},
        number={'font': {'size': 28}},
        domain={'row': ind['row'], 'column': ind['column']}
    ))

fig4.update_layout(
    grid={'rows': 3, 'columns': 3, 'pattern': "independent"},
    margin=dict(l=20, r=20, t=20, b=20),
    height=500,  # more compact height
    paper_bgcolor="white"
)

# --- Create App Layout ---
app = Dash()

app.layout = html.Div(
    style={'backgroundColor': '#f9f9f9', 'padding': '20px'},
    children=[
        html.H1('Evergreen Counselling: Mar 2024 - Feb 2025', style={'textAlign': 'center', 'marginBottom': '30px'}),
        html.Div(
            style={'display': 'flex', 'gap': '20px'},
            children=[
                html.Div(style={'flex': '1'}, children=dcc.Graph(figure=fig4)),       
                html.Div(style={'flex': '1'}, children=[
                    # Dropdown selector
                    dcc.Dropdown(
                        id='histogram-toggle',
                        options=[
                            {'label': 'By Session Count', 'value': 'session'},
                            {'label': 'By Client Count', 'value': 'client'}
                        ],
                        value='session',
                        clearable=False,
                        style={'marginBottom': '10px'}
                    ),
                    dcc.Graph(id='histogram-graph')
                ])
            ]
        ),

        # Second Row: Line Chart Full Width
        html.Div(
            style={'marginTop': '40px'},
            children=dcc.Graph(figure=line_fig)
        )
    ]
)


# --- Callbacks for Histogram Toggle ---
@app.callback(
    Output('histogram-graph', 'figure'),
    Input('histogram-toggle', 'value')
)
def update_histogram(selected_value):
    if selected_value == 'session':
        return session_hist
    else:
        return client_hist


if __name__ == '__main__':
    app.run(debug=True)
