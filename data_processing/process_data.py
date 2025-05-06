import pandas as pd
import base64
import io
from dash import html


def load_and_clean_data(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    df.columns = df.columns.str.strip()
    df.drop(columns=['Invoice Date', 'Unnamed: 4', 'Total', 'Location',
                     'Staff Member', 'Income Category', 'Payer', 'Details'],
            inplace=True)
    df['Purchase Date'] = pd.to_datetime(
        df['Purchase Date'], format='%Y-%m-%d'
        )
    df.rename(columns={'Subtotal': 'Total'}, inplace=True)

    return df


def get_monthly_details(df):
    monthly_details = df.groupby(
        df['Purchase Date'].dt.to_period('M')
        ).agg({
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

    return monthly_details


def get_client_details(df):
    client_details = df.groupby('Patient Guid',
                                as_index=False).agg({
                                    'Invoice #': 'count',
                                    'Total': 'sum',
                                    'Collected': 'sum',
                                    'Balance': 'sum'
                                }).reset_index(drop=True)

    client_details.columns = ['Patient Guid', '# of Sessions', 'Total Charged',
                              'Total Collected', 'Total Outstanding']
    client_avgs = df.groupby('Patient Guid',
                             as_index=False).agg({
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
    return client_details


def get_kpis(df):
    client_days = df['Purchase Date'].nunique()
    fridays = df['Purchase Date'].dt.to_period('W').nunique()

    return {
        'Days Worked': client_days + fridays,
        'Days with Clients': client_days,
        'Total Sessions': len(df),
        'Avg Sessions per Day': round(len(df) / client_days, 2),
        'Unique Clients': df['Patient Guid'].nunique(),
        'Avg Rate Charged': df['Total'].mean(),
        'Total Revenue': df['Collected'].sum()
    }


def filter_data(df_raw, start_date, end_date):
    df = df_raw.copy()
    if start_date:
        df = df[df['Purchase Date'] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df['Purchase Date'] <= pd.to_datetime(end_date)]
    return df

# melted = monthly_details.melt(
#     id_vars=['Month'],
#     value_vars=['# of Sessions', 'Unique Clients'],
#     var_name='Metric',
#     value_name='Value'
# )
