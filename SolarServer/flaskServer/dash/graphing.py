from dash_html_components.Div import Div
from flask import render_template
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash_bootstrap_components import themes
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash.exceptions import PreventUpdate
from plotly.express import scatter, line
import pandas as pd
from ..extensions import mongo
import json


url_base = '/data/'

def init_graphing( server ):

    external_stylesheets = [themes.BOOTSTRAP]

    app = Dash(
    '__main__',
    server=server,
    url_base_pathname=url_base,
    assets_folder='static',
    external_stylesheets=external_stylesheets
    )
    
    data = pd.read_csv('static/Sun.txt')

    df = data[data['ACCEPT'] == True]

    rv_figure = scatter(df, x="MJD", y="V")
    rv_figure.update_layout(clickmode='event')

 
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
        print("Start")
        if(children == None):
            raise PreventUpdate

        data = mongo.db.onespectrum.find({"FILENAME": "Sun_200911.1062"}, {"_id": 0, "# WAVE": 1, "FLUX": 1})

        data_dict = {
        'wave': [],
        'flux': []
        }
        count = 0
        realCount = 0
        print(data[0]["# WAVE"])
        for x in data:
            count += 1
            if(x["# WAVE"] != '' and count % 10 == 0):
                data_dict['wave'].append(float(x["# WAVE"]))
                data_dict['flux'].append(float(x["FLUX"]))
                realCount += 1
        print("Get")
        spec = line(data_dict, x="wave", y="flux", render_mode="webgl")
        print(realCount)
        
        return [children,
        dcc.Graph(
            id='spec-plot',
            figure=spec,
            className="pt-5"
        ),]

    with server.test_client() as client:
        client.get('/')
        app.index_string = render_template('data_page.html')