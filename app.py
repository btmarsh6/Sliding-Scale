from dash import Dash, html, dcc, Input, Output
from data_processing.process_data import (
    load_and_clean_data, get_client_details,
    get_monthly_details, get_kpis
)
from components.layout import (
    create_kpi_cards, create_histograms,
    create_monthly_line_chart,
    create_weekday_bars
)
import pandas as pd
import os


app = Dash()

# Load Data
input_file = ('data/Sales_20240301_20250228.csv')
df_raw = load_and_clean_data(input_file)

# Dashboard Layout
app.layout = html.Div(
    style={'backgroundColor': '#6ba569 ', 'padding': '20px'},
    children=[
        html.H1('Evergreen Counselling',
                style={'textAlign': 'center', 'marginBottom': '15px'}),
        html.Div([
            dcc.Upload(
                id='upload-data',
                children=html.Div(['Drag and Drop or ', html.A('Select File')],
                                  style={
                                      'textAlign': 'left',
                                      'padding': '20px',
                                      'height': '20px',
                                      'width': '300px',
                                      'borderWidth': '1px',
                                      'borderStyle': 'dashed',
                                      'borderRadius': '5px',
                                      'backgroundColor': '#b6b6b6',
                                      'color': '#333'
                                  }),
                style={'display': 'flex', 'marginRight': '20px'},
                multiple=False,
                accept='.csv'
            ),
            html.Div(id='uploaded-filename', style={
                                'minWidth': '150px',
                                'textAlign': 'center',
                                'color': '#fff'
                            }),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=df_raw['Purchase Date'].min().date(),
                end_date=df_raw['Purchase Date'].max().date(),
                display_format='YYYY-MM-DD',
                style={
                    'height': '50px',
                    'padding': '6px 12px',
                    'borderRadius': '5px',
                    'borderWidth': '1px',
                    'borderStyle': 'solid',
                    'borderColor': '#ccc'
                }
            ),
            html.Button("Reset", id="reset-button",
                        n_clicks=0, style={
                            'marginLeft': '20px',
                            'padding': '6px 12px',
                            'backgroundColor': '#b6b6b6',
                            'color': '#333',
                            'border': '1px solid #ccc',
                            'cursor': 'pointer'
                        })
        ],
            style={'display': 'flex',
                   'justifyContent': 'center',
                   'alignItems': 'center',
                   'gap': '20px',
                   'marginBottom': '30px'}),
        html.Div(
            style={'display': 'flex', 'gap': '20px'},
            children=[
                html.Div(style={'flex': '1'},
                         children=dcc.Graph(id='kpi-cards')),
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

        # Second Row: Monthly and Weekly Charts
        html.Div(
            style={'display': 'flex', 'gap': '20px', 'marginTop': '40px'},
            children=[
                html.Div(style={'flex': '1'},
                         children=dcc.Graph(id='weekly-bar-graph')),
                html.Div(style={'flex': '1'},
                         children=dcc.Graph(id='monthly-line-graph'))
            ]
        )
    ]
)


# --- Helper to filter raw data ---
def filter_data(start_date, end_date):
    df = df_raw.copy()
    if start_date:
        df = df[df['Purchase Date'] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df['Purchase Date'] <= pd.to_datetime(end_date)]
    return df


# --- Callback: KPI cards ---
@app.callback(
    Output('kpi-cards', 'figure'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')
)
def update_kpi_cards(start_date, end_date):
    df_filtered = filter_data(start_date, end_date)
    kpis = get_kpis(df_filtered)
    return create_kpi_cards(kpis)


# --- Callback: Histogram ---
@app.callback(
    Output('histogram-graph', 'figure'),
    Input('histogram-toggle', 'value'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')
)
def update_histogram(selected_value, start_date, end_date):
    df_filtered = filter_data(start_date, end_date)
    client_details = get_client_details(df_filtered)
    session_hist, client_hist = create_histograms(df_filtered, client_details)
    return session_hist if selected_value == 'session' else client_hist


# --- Callback: Line chart ---
@app.callback(
    Output('monthly-line-graph', 'figure'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')
)
def update_line_chart(start_date, end_date):
    df_filtered = filter_data(start_date, end_date)
    monthly_details = get_monthly_details(df_filtered)
    return create_monthly_line_chart(monthly_details)


@app.callback(
    Output('weekly-bar-graph', 'figure'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')
)
def update_weekly_bar_chart(start_date, end_date):
    df_filtered = filter_data(start_date, end_date)
    return create_weekday_bars(df_filtered)

# --- Callback: Reset button ---
@app.callback(
    Output('date-picker-range', 'start_date'),
    Output('date-picker-range', 'end_date'),
    Input('reset-button', 'n_clicks'),
    prevent_initial_call=True
)
def reset_dates(n_clicks):
    return (
        df_raw['Purchase Date'].min().date(),
        df_raw['Purchase Date'].max().date()
    )


@app.callback(
    Output('uploaded-filename', 'children'),
    Input('upload-data', 'filename')
)
def update_uploaded_filename(filename):
    if filename is not None:
        return f"Uploaded: {os.path.basename(filename)}"
    return ""


if __name__ == '__main__':
    app.run(debug=True)
