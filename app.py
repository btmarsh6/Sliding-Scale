from dash import Dash, html, dcc
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

annual_details = df.groupby(df['Purchase Date'].dt.to_period('Y')).agg({
    'Invoice #': 'count',
    'Patient Guid': pd.Series.nunique,
    'Total': 'sum',
    'Collected': 'sum',
    'Balance': 'sum'
}).reset_index()
annual_details['Total_avg'] = round(
    annual_details['Total'] / annual_details['Invoice #'],
    2)
annual_details['Collected_avg'] = round(
    annual_details['Collected'] / annual_details['Invoice #'],
    2)
annual_details['Balance_avg'] = round(
    annual_details['Balance'] / annual_details['Invoice #'],
    2)
annual_details.columns = ['Year', '# of Sessions', 'Unique Clients',
                          'Total Charged', 'Total Collected',
                          'Toal Outstanding', 'Average Charged',
                          'Average Collected', 'Average Outstanding']

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

fig4 = go.Figure()
fig4.add_trace(go.Indicator(
    mode='number',
    title='Days with Clients',
    value=client_days,
    gauge={
        'axis': {'visible': False}},
    domain={'row': 0, 'column': 1}
    ))

fig4.add_trace(go.Indicator(
    mode='number',
    title='Days Worked',
    value=client_days + fridays,
    gauge={
        'axis': {'visible': False}},
    domain={'row': 0, 'column': 0}
))

fig4.add_trace(go.Indicator(
    mode='number',
    title='Total Sessions',
    value=len(df),
    gauge={
        'axis': {'visible': False}},
    domain={'row': 0, 'column': 2}
))

fig4.add_trace(go.Indicator(
    mode='number',
    title='Avg Sessions per Day',
    value=avg_sessions_per_day,
    gauge={
        'axis': {'visible': False}},
    domain={'row': 1, 'column': 0}
))

fig4.add_trace(go.Indicator(
    mode='number',
    title='Unique Clients',
    value=total_clients,
    gauge={
        'axis': {'visible': False}},
    domain={'row': 1, 'column': 1}
))

fig4.add_trace(go.Indicator(
    mode='number',
    title='Avg Rate Charged',
    value= avg_charged,
    gauge={
        'axis': {'visible': False}},
    domain={'row': 1, 'column': 2}
))

fig4.add_trace(go.Indicator(
    mode='number',
    title='Total Revenue',
    value=total_revenue,
    gauge={
        'axis': {'visible': False}},
    domain={'row': 2, 'column': 1}
))

fig4.update_layout(
    grid = {'rows': 3, 'columns': 3, 'pattern': "independent"},
    height=600)

app = Dash()

app.layout = [
    html.Div(children='Evergreen Counselling: Mar 2024 - Feb 2025'),
    dcc.Graph(figure=fig4),
    dcc.Graph(figure=px.line(monthly_details, x='Month', y='# of Sessions',
                             title='Sessions per Month')),
    dcc.Graph(
        figure=px.histogram(df, x='Total',
                            title='Sliding Scale Distribution by Session Count',
                            nbins=40)),

]

if __name__ == '__main__':
    app.run(debug=True)
