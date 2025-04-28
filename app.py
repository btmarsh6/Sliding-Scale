from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


df = pd.read_csv('Sales_20240301_20250228.csv')
df.columns = df.columns.str.strip()
df.drop(columns=['Invoice Date', 'Unnamed: 4', 'Total', 'Location',
                 'Staff Member', 'Income Category', 'Payer', 'Details'],
        inplace=True)
df['Purchase Date'] = pd.to_datetime(df['Purchase Date'], format='%Y-%m-%d')
df.rename(columns={'Subtotal': 'Total'}, inplace=True)

monthly_details = df.groupby(df['Purchase Date'].dt.to_period('M')).agg({
    'Invoice #': 'count',
    'Patient Guid': pd.Series.nunique,
    'Total': 'sum',
    'Collected': 'sum',
    'Balance': 'sum'
}).reset_index()

monthly_details['Total_avg'] = round(
    monthly_details['Total'] / monthly_details['Invoice #'],
    2)
monthly_details['Collected_avg'] = round(
    monthly_details['Collected'] / monthly_details['Invoice #'],
    2)
monthly_details['Balance_avg'] = round(
    monthly_details['Balance'] / monthly_details['Invoice #'],
    2)
monthly_details.columns = ['Month', '# of Sessions', 'Unique Clients',
                           'Total Charged', 'Total Collected',
                           'Toal Outstanding', 'Average Charged',
                           'Average Collected', 'Average Outstanding']
monthly_details['Month'] = monthly_details['Month'].astype(str)


client_details = df.groupby('Patient Guid', as_index=False).agg({
    'Invoice #': 'count',
    'Total': 'sum',
    'Collected': 'sum',
    'Balance': 'sum'
}).reset_index(drop=True)

client_details.columns = ['Patient Guid', '# of Sessions', 'Total Charged',
                          'Total Collected', 'Total Outstanding']
client_avgs = df.groupby('Patient Guid', as_index=False).agg({
    'Total': 'mean',
    'Collected': 'mean',
    'Balance': 'mean'
}).reset_index(drop=True)
client_avgs.columns = ['Patient Guid', 'Average Charged',
                       'Average Collected', 'Average Balance']
client_details = pd.merge(client_details,
                          client_avgs,
                          how='left',
                          on='Patient Guid')
client_details['Average Charged'] = round(
    client_details['Average Charged'],
    2)
client_details['Average Collected'] = round(
    client_details['Average Collected'],
    2)

client_days = df['Purchase Date'].nunique()
avg_sessions_per_day = round(len(df) / client_days, 2)
fridays = df['Purchase Date'].dt.to_period('W').nunique()
avg_charged = df['Total'].mean()
total_clients = df['Patient Guid'].nunique()
total_revenue = df['Collected'].sum()

melted = monthly_details.melt(
    id_vars=['Month'],
    value_vars=['# of Sessions', 'Unique Clients'],
    var_name='Metric',
    value_name='Value'
)
# sliding scale histograms
session_hist = px.histogram(
    df,
    x='Total',
    nbins=40,
    title='Sliding Scale Distribution by Session Count'
)
session_hist.update_layout(xaxis_title='Session Charge', yaxis_title='Session Count')
session_hist.update_xaxes(range=[0, None])

client_hist = px.histogram(client_details, x='Average Charged', nbins=30, title='Sliding Scale Distribution by Client Count')
client_hist.update_layout(xaxis_title='Average Charged', yaxis_title='Client Count')
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
    {'title': 'Days Worked', 'value': client_days + fridays, 'row': 0, 'column': 0},
    {'title': 'Days with Clients', 'value': client_days, 'row': 0, 'column': 1},
    {'title': 'Total Sessions', 'value': len(df), 'row': 0, 'column': 2},
    {'title': 'Avg Sessions per Day', 'value': avg_sessions_per_day, 'row': 1, 'column': 0},
    {'title': 'Unique Clients', 'value': total_clients, 'row': 1, 'column': 1},
    {'title': 'Avg Rate Charged', 'value': avg_charged, 'row': 1, 'column': 2},
    {'title': 'Total Revenue', 'value': total_revenue, 'row': 2, 'column': 1},
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
# fig4 = go.Figure()
# fig4.add_trace(go.Indicator(
#     mode='number',
#     title='Days with Clients',
#     value=client_days,
#     domain={'row': 0, 'column': 1}
#     ))

# fig4.add_trace(go.Indicator(
#     mode='number',
#     title='Days Worked',
#     value=client_days + fridays,
#     domain={'row': 0, 'column': 0}
# ))

# fig4.add_trace(go.Indicator(
#     mode='number',
#     title='Total Sessions',
#     value=len(df),
#     domain={'row': 0, 'column': 2}
# ))

# fig4.add_trace(go.Indicator(
#     mode='number',
#     title='Avg Sessions per Day',
#     value=avg_sessions_per_day,
#     domain={'row': 1, 'column': 0}
# ))

# fig4.add_trace(go.Indicator(
#     mode='number',
#     title='Unique Clients',
#     value=total_clients,
#     domain={'row': 1, 'column': 1}
# ))

# fig4.add_trace(go.Indicator(
#     mode='number',
#     title='Avg Rate Charged',
#     value=avg_charged,
#     domain={'row': 1, 'column': 2}
# ))

# fig4.add_trace(go.Indicator(
#     mode='number',
#     title='Total Revenue',
#     value=total_revenue,
#     domain={'row': 2, 'column': 1}
# ))

# fig4.update_layout(
#     grid={'rows': 3, 'columns': 3, 'pattern': "independent"},
#     height=600)

# app = Dash()

# app.layout = [
#     html.Div(children='Evergreen Counselling: Mar 2024 - Feb 2025'),
#     dcc.Graph(figure=fig4),
#     dcc.Graph(figure=px.line(monthly_details, x='Month', y='# of Sessions',
#                              title='Sessions per Month')),
#     dcc.Graph(
#         figure=px.histogram(df, x='Total',
#                             title='Sliding Scale Distribution by Session Count',
#                             nbins=40)),

# ]

if __name__ == '__main__':
    app.run(debug=True)
