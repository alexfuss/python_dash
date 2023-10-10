import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

# Load your CSV files and perform data processing (same as your original script)
search_console_csv = './csv_files/tf_dummy_gsc.csv'
search_console_df = pd.read_csv(search_console_csv)
analytics_csv = './csv_files/tf_dummy_ga.csv'
analytics_df = pd.read_csv(analytics_csv)

# Define a regular expression pattern to identify branded queries
pattern = r'.*thermo.*'

# Use the regular expression pattern to create a new 'Category' column
search_console_df['Category'] = search_console_df['Query'].str.contains(pattern, case=False, regex=True)
search_console_df['Category'] = search_console_df['Category'].map({True: 'branded', False: 'non-brand'})

# Merge the two DataFrames based on the 'url' column
combined_df = pd.merge(search_console_df, analytics_df, on='URL', how='left')

# Fill any NaN (null) values in the 'Sessions' column with 0
combined_df['Sessions'] = combined_df['Sessions'].fillna(0)

# Calculate branded and non-brand clicks based on the 'Category' column
combined_df['Clicks_branded'] = combined_df['Clicks'] * (combined_df['Category'] == 'branded')
combined_df['Clicks_non_brand'] = combined_df['Clicks'] * (combined_df['Category'] == 'non-brand')

# Calculate the percentage of branded and non-brand clicks
combined_df['Percentage_branded'] = (combined_df['Clicks_branded'] / (combined_df['Clicks_branded'] + combined_df['Clicks_non_brand'])) * 100
combined_df['Percentage_non_brand'] = (combined_df['Clicks_non_brand'] / (combined_df['Clicks_branded'] + combined_df['Clicks_non_brand'])) * 100

# Calculate the branded and non-brand views based on the percentages
combined_df['Branded_Traffic'] = (combined_df['Sessions'] * combined_df['Percentage_branded']) / 100
combined_df['Non_Brand_Traffic'] = (combined_df['Sessions'] * combined_df['Percentage_non_brand']) / 100

# Extract the month from the 'Date_x' column
combined_df['Month'] = pd.to_datetime(combined_df['Date_x']).dt.month

# Sum the branded and non-brand traffic for each URL
result_df = combined_df.groupby('URL').agg({
    'Sessions': 'sum',
    'Month': 'first',  # Use 'first' to keep the month associated with the URL
    'Branded_Traffic': 'sum',
    'Non_Brand_Traffic': 'sum'
}).reset_index()

# Create a Dash app instance
app = dash.Dash(__name__)

# Define the layout of your web application
app.layout = html.Div([
    html.H1('Data Visualization'),
    
    dcc.Graph(
        id='branded-traffic-bar-chart',
        className='bar-chart'  # Apply the bar-chart class to the chart
    ),
    dcc.Graph(
        id='non-brand-traffic-bar-chart',
        className='bar-chart'  # Apply the bar-chart class to the chart
    ),
    
    # Link the CSS file
    html.Link(
        rel='stylesheet',
        href='/assets/styles.css'  # Update the path to your CSS file as needed
    )
])

# Define callback functions to update components
@app.callback(
    Output('branded-traffic-bar-chart', 'figure'),  # Update the branded traffic chart
    Input('branded-traffic-bar-chart', 'selectedData')  # Correct input ID
)
def update_branded_traffic_chart(selected_data):
    # Create a bar chart for branded traffic by month using Plotly Express
    fig = px.bar(result_df, x='Month', y='Branded_Traffic', title='Branded Traffic by Month')
    
    return fig

@app.callback(
    Output('non-brand-traffic-bar-chart', 'figure'),  # Update the non-brand traffic chart
    Input('non-brand-traffic-bar-chart', 'selectedData')  # Correct input ID
)
def update_non_brand_traffic_chart(selected_data):
    # Create a bar chart for non-brand traffic by month using Plotly Express
    fig = px.bar(result_df, x='Month', y='Non_Brand_Traffic', title='Non-Brand Traffic by Month')
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
