from dash_html_components.Div import Div
from flask import render_template, request, g
from dash import Dash
from dash_core_components import (
    Graph, Slider, RangeSlider, 
    DatePickerRange, Loading)
from dash_html_components import Div, Pre, Br
from dash_bootstrap_components import themes
from dash.dependencies import (Input, 
    Output, State, ClientsideFunction)
from dash.exceptions import PreventUpdate
from plotly.express import scatter
from pandas import read_csv
from ..extensions import mongo
from ..config import csv_label
import julian
from datetime import date
import dash_daq as daq
import gridfs



url_base = '/data/'

def from_mjd(num):
    return str(julian.from_jd(num, fmt='mjd'))[0:23]
    
def to_mjd(num):
    return julian.to_jd(date(num), fmt='jd')


def init_graphing( server ):

    fs = gridfs.GridFS(mongo.db)
    # file = open('static/Sun_200912.1113_2d.csv', 'rb')
    # id = fs.put(file,
    #     filename='Sun_200912.1113.2ds.csv',
    #     filetype='2d')

    external_stylesheets = [themes.BOOTSTRAP]

    app = Dash(
        '__main__',
        server=server,
        url_base_pathname=url_base,
        assets_folder='static',
        external_stylesheets=external_stylesheets
    )


    @server.before_request
    def update():
        if request.endpoint == url_base:
            app.index_string = render_template(
                'data_page.html'
            )


    data = read_csv(fs.find_one({'filetype':'rv'}))

    df = data[data[csv_label['accept']] == True]

    df[csv_label['mjd']] = df[csv_label['mjd']].apply(from_mjd)

 
    app.layout = Div([
        Loading([
            DatePickerRange(
                id='date-range',
                className='pt-5 d-flex justify-content-end w-100',
                min_date_allowed=date(2020, 8, 23),
                max_date_allowed=date(2021, 9, 19),
                initial_visible_month=date(2020, 8, 23),
                end_date=date(2020, 9, 18)
            ),
            Graph(
                id='rv-plot',
                className="",
                config={
                    "displaylogo": False,
                    'modeBarButtonsToRemove': ['pan2d','lasso2d', 'autoscale']
                }
            ),
        ], type="default", className='d-flex justify-content-end w-100'),

        Div(
            id = 'rv-data',
            children = df[[csv_label['mjd'], csv_label['velocity'], csv_label['filename']]].to_json(),
            className='d-none'
        ),
        
        Div([
            Pre(id='click-data'),
        ]),

        Div([
            Loading([
                Div(
                    id = 'spec-data',
                    children = [],
                    className='d-none'
                ),
                Graph(
                id='spec-plot',
                className="pt-0",
                config={
                        "displaylogo": False,
                        'modeBarButtonsToRemove': ['pan2d','lasso2d', 'autoscale']
                    }
                ),
            ], type="default",),
            Div([
                Slider(
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
                    id='resolution',
                    className='col',

                ),
                RangeSlider(
                    id='spec-range',
                    className='col',
                    min=0,
                    max=85,
                    step=1,
                    value=[40, 45],
                    marks={
                        0: {'label': '0'},
                        40: {'label': '40'},
                        45: {'label': '45'},
                        85: {'label': '85'}
                    }
                ),
            ], className='row'),
        ], id='spec-container'),
        Br(),
        Div([
            daq.ToggleSwitch(
                label='lin / log',
                id='log-switch',
                className='col',
                labelPosition='bottom'
            ),
            daq.ToggleSwitch(
                label='1D / 2D',
                id='dim-switch',
                className='col',
                labelPosition='bottom'
            )
        ], className="row")
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

        if(dim):
            return read_csv(fs.find_one({'filetype':'2d'})).to_json()

        test = read_csv(fs.find_one({'filetype':'1d'}))
        
        return test.to_json()

    

    return app
