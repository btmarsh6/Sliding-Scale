from dash import Dash, html, dcc, Input, Output
from data_processing.process_data import load_and_clean_data
from data_processing.process_data import get_client_details
from data_processing.process_data import get_monthly_details
from data_processing.process_data import get_kpis
from components.layout import create_kpi_cards
from components.layout import create_histograms
from components.layout import create_monthly_line_chart


app = Dash()

# Load Data
input_file = ('data/Sales_20240301_20250228.csv')
df = load_and_clean_data(input_file)
client_details = get_client_details(df)
monthly_details = get_monthly_details(df)
kpis = get_kpis(df)

# Create figures
kpi_cards = create_kpi_cards(kpis)
session_hist, client_hist = create_histograms(df, client_details)
monthly_line_chart = create_monthly_line_chart(monthly_details)

app.layout = html.Div(
    style={'backgroundColor': '#6ba569 ', 'padding': '20px'},
    children=[
        html.H1('Evergreen Counselling',
                style={'textAlign': 'center', 'marginBottom': '15px'}),
        html.Div([
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=df['Purchase Date'].min().date(),
                end_date=df['Purchase Date'].max().date(),
                display_format='YYYY-MM-DD'
            )
        ],
            style={'textAlign': 'center', 'marginBottom': '30px'}),
        html.Div(
            style={'display': 'flex', 'gap': '20px'},
            children=[
                html.Div(style={'flex': '1'},
                         children=dcc.Graph(figure=kpi_cards)),       
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
            children=dcc.Graph(figure=monthly_line_chart)
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
