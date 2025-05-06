from dash import Dash, html, dcc, Input, Output, State, ctx
from data_processing.process_data import load_and_clean_data, filter_data
from components.layout import (
    create_kpi_cards, create_histograms,
    create_monthly_line_chart,
    create_weekday_bars, create_bar_and_line
)
import pandas as pd
import base64
import io




app = Dash()

df_raw = None

app.layout = html.Div(
    style={'backgroundColor': '#6ba569 ', 'padding': '20px'},
    children=[
        html.H1('Evergreen Counselling',
                style={'textAlign': 'center',
                       'marginTop': '0px',
                       'marginBottom': '15px',
                       'fontFamily': 'Helvetica',
                       'color': 'white',
                       'fontSize': '50px'}),
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
                start_date=None,
                end_date=None,
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
        html.Div(id='output-data-upload')
            ])





@app.callback(
    Output('output-data-upload', 'children'),
    Output('date-picker-range', 'start_date', allow_duplicate=True),
    Output('date-picker-range', 'end_date', allow_duplicate=True),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
    prevent_initial_call=True
)
def update_output(contents, filename, start_date, end_date):
    triggered_id = ctx.triggered_id
    if triggered_id == 'upload-data':
        if contents is not None:
            global df_raw
            df_raw = load_and_clean_data(contents, filename)
            start_date = df_raw['Purchase Date'].min().date()
            end_date = df_raw['Purchase Date'].max().date()
            return create_bar_and_line(df_raw), start_date, end_date
        return "No file uploaded", None, None
    elif triggered_id == 'date-picker-range':
        if df_raw is not None:
            df_filtered = filter_data(df_raw, start_date, end_date)
            return create_bar_and_line(df_filtered), start_date, end_date


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


if __name__ == '__main__':
    app.run(debug=True)
