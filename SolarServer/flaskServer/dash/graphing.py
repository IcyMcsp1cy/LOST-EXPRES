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
from datetime import date
import json
from astropy.time import Time
import dash_daq as daq



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

    data_2d = pd.read_csv('static/2d.csv')[["ORDER", "# WAVE", "FLUX"]]

    figure_2d = line(data_2d, x="# WAVE", y="FLUX", color="ORDER", render_mode="webgl")

    df = data[data['ACCEPT'] == True]
    print(type(df[['MJD']]))

    df['MJD'] = Time(df['MJD'], format='mjd').iso

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
            dcc.DatePickerRange(
                id='date-range',
                min_date_allowed=date(2020, 7, 5),
                max_date_allowed=date(2021, 9, 19),
                initial_visible_month=date(2020, 8, 5),
                end_date=date(2020, 9, 18)
            )
        ]),

        html.Div(
            id = 'rv-data',
            children = df.to_json(),
            className='d-none'
        ),
        html.Div(
            id = 'spec-data',
            children = [],
            className='d-none'
        ),
        html.Div([
            html.Pre(id='click-data'),
        ]),

        html.Div([
            dcc.Graph(
            id='spec-plot',
            className="pt-5",
            config={
                    "displaylogo": False,
                    'modeBarButtonsToRemove': ['pan2d','lasso2d', 'autoscale']
                }
            ),
            html.Div([
                dcc.Slider(
                    min=1,
                    max=200,
                    value=100,
                    marks={
                        1: {'label': '1:1', 'style': {'color': '#77b0b1'}},
                        20: {'label': '20:1'},
                        50: {'label': '50:1'},
                        100: {'label': '100:1'},
                        200: {'label': '200:1', 'style': {'color': '#f50'}}
                    },
                    id='resolution'
                ),
                dcc.RangeSlider(
                    id='spec-range',
                    min=0,
                    max=85,
                    step=1,
                    value=[45, 50],
                    marks={
                        0: {'label': '0'},
                        45: {'label': '45'},
                        50: {'label': '50'},
                        85: {'label': '85'}
                    }
                ),
            ], className='col'),
        ], id='spec-container'),
        html.Br(),
            daq.ToggleSwitch(
                label='lin / log',
                id='log-switch',
                className='row',
                labelPosition='bottom'
            ),
            daq.ToggleSwitch(
                label='1D / 2D',
                id='dim-switch',
                className='row',
                labelPosition='bottom'
            )
    ])


    app.clientside_callback(
        output=Output('click-data', 'children'),
        inputs=[Input('rv-plot', 'clickData'),
                State('rv-data', 'children')],
        clientside_function=ClientsideFunction(
            namespace='graphing',
            function_name ='clickData'
        )
    )

    app.clientside_callback(
        output=Output('rv-plot', 'figure'),
        inputs=[Input('date-range', 'start_date'),
                Input('date-range', 'end_date'),
                State('rv-data', 'children')],
        clientside_function=ClientsideFunction(
            namespace='graphing',
            function_name ='datefunc'
        )
    )

    app.clientside_callback(
        output=Output('spec-plot', 'figure'),
        inputs=[Input('resolution', 'value'),
                Input('spec-range', 'value'),
                Input('log-switch', 'value'),
                Input('spec-data', 'children')],
        clientside_function=ClientsideFunction(
            namespace='graphing',
            function_name ='specfunc'
        )
    )

    

    @app.callback(
        Output('spec-data', 'children'),
        Input('click-data', 'children'),
        Input('dim-switch', 'value')
    )
    def getGraph(children, dim):

        if(children == None):
            raise PreventUpdate

        print(type(dim))
        if(dim):
            return data_2d.to_json()


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
            if(x["# WAVE"] != ''):
                data_dict['wave'].append(float(x["# WAVE"]))
                data_dict['flux'].append(float(x["FLUX"]))
                realCount += 1
        return json.dumps(data_dict)
 
    with server.test_client() as client:
        client.get('/')
        app.index_string = render_template('data_page.html')
