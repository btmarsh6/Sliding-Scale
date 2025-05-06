from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go


def create_kpi_cards(kpis):
    fig  = go.Figure()

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
        fig.add_trace(go.Indicator(
            mode='number',
            value=ind['value'],
            title={'text': ind['title'], 'font': {'size': 18}},
            number={'font': {'size': 28},
                    'prefix': '$' if ind['title'] in ['Avg Rate Charged', 'Total Revenue'] else '',
                    'valueformat': ',.2f' if ind['title'] in ['Avg Rate Charged', 'Total Revenue'] else ''},
            domain={'row': ind['row'], 'column': ind['column']}
        ))

    fig.update_layout(
        grid={'rows': 3, 'columns': 3, 'pattern': "independent"},
        margin=dict(l=20, r=20, t=20, b=20),
        height=500,
        paper_bgcolor="white"
    )
    return fig


def create_histograms(df, client_details):
    session_hist = px.histogram(
        df,
        x='Total',
        nbins=40,
        title='Sliding Scale Distribution by Session Count'
    )
    session_hist.update_layout(xaxis_title='Session Charge ($)',
                               yaxis_title='# of Sessions')
    session_hist.update_xaxes(range=[0, None])

    client_hist = px.histogram(
        client_details, x='Average Charged', nbins=30,
        title='Sliding Scale Distribution by Client Count'
        )
    client_hist.update_layout(xaxis_title='Average Charged ($)',
                              yaxis_title='# of Clients')
    client_hist.update_xaxes(range=[0, None])

    return session_hist, client_hist


def create_monthly_line_chart(monthly_details):
    fig = px.line(monthly_details,
                  x='Month',
                  y='# of Sessions',
                  title='Sessions per Month'
                  )
    fig.update_layout(xaxis_title=None)
    return fig


def create_weekday_bars(df):
    df['Day of Week'] = df['Purchase Date'].dt.day_name()
    date_count = df.groupby('Purchase Date').agg({
        'Invoice #': 'count',
        'Total': 'sum',
        'Day of Week': 'first'}).reset_index()
    day_name_count = date_count.groupby('Day of Week').agg({
        'Invoice #': 'mean',
        'Total': 'mean'})
    day_name_count.rename(columns={
        'Invoice #': 'Avg Sessions',
        'Total': 'Avg Revenue'}, inplace=True)
    day_name_count = day_name_count.reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
    fig = px.bar(day_name_count,
                 x=day_name_count.index,
                 y='Avg Sessions',
                 text=day_name_count['Avg Revenue'].apply(lambda x: f"${x:,.2f}"),
                 title='Average Sessions and Revenue by Day of Week')
    fig.update_traces(texttemplate='%{text}', textposition='inside')
    fig.update_layout(xaxis_title=None,
                      yaxis_title='Avg # of Sessions',
                      xaxis_tickvals=day_name_count.index,
                      xaxis_ticktext=day_name_count.index)
    return fig
