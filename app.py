import pandas as pd
import numpy as np
from datetime import datetime
from dash.dependencies import Input, Output
from dash import Dash, dcc, html, dash_table
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta
from kaggle.api.kaggle_api_extended import KaggleApi
import os

app = Dash(__name__)
server = app.server

api= KaggleApi()
api.authenticate()

# set up file path
DATA_PATH = 'data'
if not os.path.exists(DATA_PATH):
    # download dataset only once
    api.dataset_download_files(
        "retail-sales.csv",
        path=DATA_PATH,
        unzip=True
    )

#read csv file
retail_sales_df = pd.reac_csv("retail_sales.csv")


# change columns to their right data type
retail_sales_df["date"] = pd.to_datetime(retail_sales_df['date'])

# change object columns to numerical
cols_to_num = ['sales','price','promo','weekday','month']

retail_sales_df[cols_to_num] = retail_sales_df[cols_to_num].apply(pd.to_numeric, errors = 'coerce')

# change object columns to string
retail_sales_df[['store_id', 'item_id']] = retail_sales_df[['store_id','item_id']].fillna("").astype(str)

# create a total sales column
retail_sales_df['total_sales'] = retail_sales_df['sales'] * retail_sales_df['price']

# create a year column
retail_sales_df['year'] = retail_sales_df['date'].dt.year

grouped_sales = retail_sales_df.groupby(['date', 'store_id','item_id'])['total_sales'].sum().reset_index()

stores = grouped_sales['store_id'].unique()

KPI_STYLE = {
    "background": "linear-gradient(135deg, #1f2937, #111827)",
    "color": "white",
    "padding": "20px",
    "borderRadius": "12px",
    "width": "100%",
    "boxShadow": "0px 6px 16px rgba(0,0,0,0.3)",
    "textAlign": "left"
}

COLOR_SEQUENCE = px.colors.qualitative.Set2

color_discrete_sequence = COLOR_SEQUENCE

def style_figure(fig):
    fig.update_layout(
        plot_bgcolor="#020617",
        paper_bgcolor="#020617",
        font=dict(color="white"),
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig


app.layout = html.Div([
    html.H1('Retail Sales Dashboard', 
            style={
                'textAlign':"center",
                'color':'white',
                'marginBottom':'30px',
                'backgroundColor': '#020617',
                'padding':'30px',
                'fontFamily':'Arial'
            }),
    
    #filters
    html.Div([
        dcc.Dropdown(
            id='store-dropdown',
            options=[{'label': f" Store {s}", "value":s} for s in stores],
            multi = True,
            value = ['store_10'],
            style = {
                'width':'300px',
                'color':'black'
            }
        ),
        dcc.Dropdown(
            id = 'item-dropdown',
            multi = True,
            placeholder = 'Select items (optional)',
            style = {
                'width':'300px',
                'color':'black'
            }
        ),
        dcc.DatePickerRange(
            id = 'date-range',
            min_date_allowed = grouped_sales['date'].min(),
            max_date_allowed = grouped_sales['date'].max(),
            start_date = grouped_sales['date'].min(),
            end_date = grouped_sales['date'].max(),
            style = {
                'backgroundColor':'#1f2937',
                'color':'white',
                'borderRadius':'8px',
                'padding':'5px'
            }
        ),
        dcc.Dropdown(
            id='time-filter',
            options =[
                {'label': "Last 30 Days", 'value': '30D'},
                {'label': "Last 60 Days", 'value': '60D'},
                {'label': "Last 90 Days", 'value': '90D'},
                {'label': "Last Year", 'value': '1Y'},
                {'label': "All", 'value': 'ALL'}
            ],
            value = 'ALL'
        )
        
    ], style={'display': 'flex', 
              'gap':'20px',
              'alignItems':'center',
              'justifyContent':'center',
              'marginBottom':'30px'
             }),
    
    # KPI
    html.Div([
        html.Div(id = 'kpi-total-sales'),
        html.Div(id = 'kpi-avg-sales'),
        html.Div(id = 'kpi-store-count'),
        html.Div(id = 'kpi-top-store'),
    ], style = {
        'display': 'flex',
        'justifyContent':'center',
        'gap':'20px',
        'marginBottom': '30px',
        'maxWidth':'1200px',
        'marginLeft':'auto',
        'marginRight':'auto'
    }),

    #Line Chart
    dcc.Graph(id = 'line-chart', 
              style = {
                  'marginBottom': '30px',
                  'display':'flex',
              }),
    
    # Bar + Pie
    html.Div([
        dcc.Graph(id='bar-chart', style = {"width":'50%'}),
        dcc.Graph(id = 'pie-chart', style = {"width":'50%'})
    ], style = {
        "display":'flex',
        "gap":'20px',
        "marginBottom":"30px"
               }),
    
    # Average Sales Table
    html.Div([
        dcc.Graph(id = 'rolling-chart')
    ], style = {'marginBottom':'30px'}),
    
    # Summary Table (data table)
    html.Div([
        dash_table.DataTable(
            id = 'summary-table'
            #style_data = {'backgroundColor':"#111827", "color":'white'},
            #style_table = {'overflowX':'auto'},
            #style_cell = {'textAlign':'center', "padding":'10px'},
            #style_header = {"backgroundColor": '#1f2937', "color":"white", "fontweight":"bold"}
        )
    ], style = {
        "backgroundColor":"#0f172a",
        "minHeight": "20vh",
        "padding":"30px",
        "fontFamily":"Arial"
    },
    )

])


@app.callback(
    Output('item-dropdown','options'),
    Output('item-dropdown', 'value'),
    Input('store-dropdown', 'value')
)


def update_dashboards(selected_store):
    df_store = grouped_sales[grouped_sales['store_id'].isin(selected_store)]
    
    items = df_store['item_id'].unique()
    
    options = [
        {'label': f" Item {i}","value":i}
        for i in items
    ]
    
    # Default: top 1 across selected stores
    top_items = (
        df_store.groupby('item_id')['total_sales']
        .sum()
        .nlargest(1)
        .index
        .tolist()
    )

    
    return options, top_items


@app.callback(
    Output('line-chart','figure'),
    Output('kpi-total-sales','children'),
    Output('kpi-avg-sales', 'children'),
    Output('kpi-store-count', 'children'),
    Output('kpi-top-store', 'children'),
    Output('bar-chart', 'figure'),
    Output('pie-chart', 'figure'),
    Output('rolling-chart', 'figure'),
    Output('summary-table', 'data'),
    Output('summary-table', 'columns'),
    Input('store-dropdown','value'),
    Input('item-dropdown','value'),
    Input('time-filter', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date'),
)

def update_graph(stores, selected_items,time_filter,start_date, end_date):
    # store filter
    if isinstance(stores, str):
        stores = [stores]
        
    df_filtered_store = grouped_sales[grouped_sales['store_id'].isin(stores)]
    
    # item filter
    if selected_items:
        df_filtered = df_filtered_store[df_filtered_store['item_id'].isin(selected_items)]
    
        # determie date range
        max_date = df_filtered['date'].max()
            
        if time_filter == '30D':
            start_date = max_date - timedelta(days=30)
        elif time_filter == '60D':
            start_date = max_date - timedelta(days=60)
        elif time_filter == '90D':
            start_date = max_date - timedelta(days=90)
        elif time_filter == '1Y':
            start_date = max_date - timedelta(days=365)
            
        # fallack to manual range
        df_date_filter = df_filtered[(df_filtered['date'] >= start_date)&
                                (df_filtered['date'] <= end_date)]
        
        
        df_grouped = (
            df_date_filter.groupby(['date','store_id'])['total_sales'].sum().reset_index()
        )
        
        #KPI Calculations
        total_sales = df_filtered['total_sales'].sum()
        avg_sales = df_filtered['total_sales'].mean()
        store_count = df_filtered['store_id'].nunique()
        top_store = (
            df_filtered.groupby('store_id')['total_sales'].sum().idxmax()if not df_filtered.empty else 'N/A'
        )
        

        # line chart
        line_fig = px.line(
            df_grouped,
            x='date',
            y='total_sales',
            color='store_id',
            title="Sales Trend"
        )
        
        # Aggregate sales by store
        bar_df = (
            df_filtered.groupby('store_id')['total_sales'].sum().reset_index().sort_values(by='total_sales', ascending = False)
        )
        
        # bar chart
        bar_df = bar_df.head(10)
        
        bar_fig = px.bar(
            bar_df,
            x = 'store_id',
            y = 'total_sales',
            title = 'Top Stores by Sales'
        )
        
        # pie chart
        pie_fig = px.pie(
            bar_df,
            names = 'store_id',
            values = 'total_sales',
            title = 'Sales Distribution'
        )
        
        pie_fig.update_layout(
            paper_bgcolor = "#0f172a",
            font = dict(color = 'white')
        )
        
        # sort first (critical)
        rolling_df = df_filtered.sort_values('date')
        
        # create rilling average per store
        rolling_df['rolling_7'] = (
            rolling_df.groupby('store_id')['total_sales'].transform(lambda x: x.rolling(7).mean())
        )  
        
        rolling_fig = px.line(
            rolling_df,
            x = 'date',
            y="rolling_7",
            color = 'store_id',
            title ='7-Day Rolling Average Sales'
        )
        
        # summary table
        table_df = (
            df_filtered.groupby('store_id')['total_sales'].agg(
            total_sales = 'sum',
            avg_sales='mean',
            max_sales='max',
            min_sales='min'
        ).reset_index()
        )
        
        # Add ranking
        table_df['rank'] = table_df["total_sales"].rank(ascending=False, method = 'dense')
        
        # sort by best performers
        table_df = table_df.sort_values('total_sales', ascending = False)
        
        table_data = table_df.to_dict('records')
        
        table_columns = [
            {"name": col.replace("_", " ").title(), "id":col} for col in table_df.columns
        ]
        
        # update fig wtith color code
        line_fig = style_figure(line_fig)
        bar_fig = style_figure(bar_fig)
        pie_fig = style_figure(pie_fig)
        rolling_fig = style_figure(rolling_fig)
        
        
        
        return( 
            line_fig, 
            html.Div([
                html.P('Total Sales'),
                html.H2(f"${total_sales:,.0f}")
            ], style = KPI_STYLE),
            html.Div([
                html.P("Avg Daily Sales"),
                html.H2(f"${avg_sales: ,.0f}")
            ], style = KPI_STYLE),
            html.Div([
               html.P('Stores Selected'),
                html.H2(store_count)
            ], style = KPI_STYLE),
            html.Div([
                html.P('Top Store'),
                html.H2(top_store)
            ], style = KPI_STYLE),
            bar_fig,
            pie_fig,
            rolling_fig,
            table_data, 
            table_columns
        )
    

# run app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port = port)