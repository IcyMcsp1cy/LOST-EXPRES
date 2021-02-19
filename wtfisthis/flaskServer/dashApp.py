from flask import render_template, abort, request
from dash import Dash
from json import dumps
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash.exceptions import PreventUpdate
from plotly.express import scatter
import pandas as pd

import numpy as np
import plotly
import plotly.graph_objs as go

url_base = '/data/'

def init_dash( server ):

    external_stylesheets = [dbc.themes.BOOTSTRAP]

    app = Dash(
    '__main__',
    server=server,
    url_base_pathname=url_base,
    assets_folder='static',
    external_stylesheets=external_stylesheets,
    )
    


    data = pd.read_csv('static/Sun.txt')

    df = data[data['ACCEPT'] == True]

    rv_figure = scatter(df, x="MJD", y="V")
    rv_figure.update_layout(clickmode='event')

    rand_x = np.random.randn(500)
    rand_y = np.random.randn(500)

    fig = scatter(
        x= rand_x,
        y= rand_y,
    )

    app.layout = html.Div([
        dcc.Loading([
            dcc.Graph(
                id='rv-plot',
                className="pt-5",
                config={
                    "displaylogo": False,
                    'modeBarButtonsToRemove': ['pan2d','lasso2d', 'autoscale']
                }
            ),
        dcc.Input(id="x1", type="number", placeholder="", debounce=True),
        dcc.Input(id="x2", type="number", placeholder="", debounce=True),
        html.Br(),
        dcc.Input(id="y1", type="number", placeholder="", debounce=True),
        dcc.Input(id="y2", type="number", placeholder="", debounce=True),
        ]),

        html.Div(
            id = 'data',
            children = df.to_json(),
            className='d-none'
        ),
        html.Div([
            dcc.Markdown("""
                **Click Data**
                Click on points in the graph.
            """),
            html.Pre(id='click-data'),
        ]),
        html.Div([], id='spec-container'),
    ])


    app.clientside_callback(
        output=Output('click-data', 'children'),
        inputs=[Input('rv-plot', 'clickData'),
                State('data', 'children')],
        clientside_function=ClientsideFunction(
            namespace='graphing',
            function_name ='clickData'
        )
    )

    app.clientside_callback(
        output=Output('rv-plot', 'figure'),
        inputs=[Input('x1', 'value'),
                Input('x2', 'value'),
                Input('y1', 'value'),
                Input('y2', 'value'),
                State('data', 'children')],
        clientside_function=ClientsideFunction(
            namespace='graphing',
            function_name ='zoomfunc'
        )
    )
    

    @app.callback(
        Output('spec-container', 'children'),
        Input('click-data', 'children')
    )
    def getGraph(children):
        if(children == None):
            raise PreventUpdate
        return [children,
        dcc.Graph(
            id='spec-plot',
            figure=rv_figure,
            className="pt-5"
        )]

    with server.test_client() as client:
        client.get('/')
        app.index_string = render_template('data_page.html')