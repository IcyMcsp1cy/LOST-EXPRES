from dash_html_components.Div import Div
from flask import render_template, request, g
from dash import Dash
from dash_core_components import (
    Graph, Slider, RangeSlider,
    DatePickerRange, Loading)
from dash_html_components import Div, Pre, Br, Button
from dash_bootstrap_components import themes
from dash.dependencies import (Input,
                               Output, State, ClientsideFunction)
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame
from dash.exceptions import PreventUpdate
from pandas import read_csv, DataFrame
from ..extensions import collection, mongo
from ..config import csv_label
import julian
from datetime import date
import dash_daq as daq
import gridfs
from json import dumps
import plotly
import time
import plotly.graph_objs as go

url_base = '/data/'

rv_plot = None


def from_mjd(num):
    return str(julian.from_jd(float(num), fmt='mjd'))[0:23]


def to_mjd(num):
    return julian.to_jd(date(num), fmt='mjd')

def rv_plot(server):
    with server.app_context():
        entries = list(collection('radialvelocity').find())
        data = DataFrame(entries)

        rv = data[data['PUBLIC'] == True]
        rv[csv_label['mjd']] = rv[csv_label['mjd']].apply(from_mjd)

        fig = go.Scatter(
            x= rv[csv_label['mjd']],
            y= rv[csv_label['velocity']],
            mode="markers",
            marker=go.scatter.Marker(
                opacity=0.6,
                colorscale="Viridis"
            )
        )

        rv_plot.result = dumps([fig], cls=plotly.utils.PlotlyJSONEncoder)
        rv_plot.data = rv
        return rv



def init_graphing(server):
    fs = gridfs.GridFS(mongo.db)
    
    rv = rv_plot(server)
    
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
            rv = rv_plot.data
            app.layout = Div([
                Loading([
                    Div(
                        id='rv-download-container'
                    ),
                    Button(
                        'Download Radial Velocities',
                        id='rv-download',
                        className='btn btn-primary btn-sm float-right',
                    ),
                    Download(
                        id='rv-download-data'
                    ),
                    DatePickerRange(
                        id='date-range',
                        className='pt-1 d-flex justify-content-end w-100',
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
                            'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'autoscale']
                        }
                    ),
                ], type="default", className='d-flex justify-content-end w-100'),
                Div(
                    id='rv-data',
                    children=rv[[csv_label['mjd'], csv_label['velocity'], csv_label['filename']]].to_json(),
                    className='d-none'
                ),
                Div([
                    Pre(id='click-data'),
                ]),
                
                Br(),
                Br(),
                Div([
                    Loading([
                        Div([
                            Div([
                                Button(
                                    'Download 1D',
                                    id='1d-spec-download',
                                    className='btn btn-primary btn-sm',
                                ),
                                Download(
                                    id='1d-spec-download-data'
                                ),
                            ], className='d-none'),
                            Div([
                                Button(
                                    'Download 2D',
                                    id='2d-spec-download',
                                    className='btn btn-primary btn-sm',
                                ),
                                Download(
                                    id='2d-spec-download-data'
                                ),
                            ], className="d-none"),
                        ], className="row justify-content-end d-none", id="spec-download-container"),
                        Div(
                            id='spec-data',
                            children=[],
                            className='d-none'
                        ),
                        Graph(
                            id='spec-plot',
                            className="pt-0",
                            config={
                                "displaylogo": False,
                                'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'autoscale']
                            }
                        ),
                    ], type="default", ),
                    Div([
                    ],
                    id='slide-label',
                    className='w-100 text-center'),
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
                            className='col d-none',
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

    

    app.layout = Div([])

    app.clientside_callback(
        output=Output('click-data', 'children'),
        inputs=[Input('rv-plot', 'clickData'),
                State('rv-data', 'children')],
        clientside_function=ClientsideFunction(
            namespace='graphing',
            function_name='clickData'
        )
    )

    app.clientside_callback(
        output=Output('rv-plot', 'figure'),
        inputs=[Input('date-range', 'start_date'),
                Input('date-range', 'end_date'),
                State('rv-data', 'children')],
        clientside_function=ClientsideFunction(
            namespace='graphing',
            function_name='datefunc'
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
            function_name='specfunc'
        )
    )

    @app.callback(Output('rv-download-data', 'data'),
                  Input('rv-download', 'n_clicks'))
    def rvDownload(n_clicks):
        if (n_clicks is not None) and (n_clicks > 0):
            return send_data_frame(rv.to_csv, filename="radial_velocities.csv")

    @app.callback(Output('1d-spec-download-data', 'data'),
                  Input('1d-spec-download', 'n_clicks'),
                  Input('click-data', 'children'))
    def oneDownload(n_clicks, children):
        if (n_clicks is not None) and (n_clicks > 0) and (children is not None):
            searchDate = children.split('_')[1]
            searchDate = searchDate.strip('.fits')
            try:
                specData = read_csv(fs.find_one({'filetype': '1d',
                                                 'filename': {'$regex': '.*' + searchDate + '.*'},
                                                 }))
                return send_data_frame(specData.to_csv, filename=searchDate + "1d_spectrum.csv")
            except:
                specData = read_csv(fs.find_one({'filetype': '1d',
                                                 'filename': {'$regex': '.*200912.1113.*'},
                                                 }))
                return send_data_frame(specData.to_csv, filename="200912.1113.1d_spectrum.csv")

    @app.callback(Output('2d-spec-download-data', 'data'),
                  Input('2d-spec-download', 'n_clicks'),
                  Input('click-data', 'children'))
    def twoDownload(n_clicks, children):
        if (n_clicks is not None) and (n_clicks > 0) and (children is not None):
            searchDate = children.split('_')[1]
            searchDate = searchDate.strip('.fits')
            try:
                specData = read_csv(fs.find_one({'filetype': '2d',
                                                 'filename': {'$regex': '.*' + searchDate + '.*'},
                                                 }))
                return send_data_frame(specData.to_csv, filename=searchDate + "2d_spectrum.csv")
            except:
                specData = read_csv(fs.find_one({'filetype': '2d',
                                                 'filename': {'$regex': '.*200912.1113.*'},
                                                 }))
                return send_data_frame(specData.to_csv, filename="200912.1113.2d_spectrum.csv")


    @app.callback(
        Output('spec-data', 'children'),
        Output('spec-download-container', 'children'),
        Output('spec-range', 'className'),
        Output('resolution', 'className'),
        Output('slide-label', 'children'),
        Input('click-data', 'children'),
        Input('dim-switch', 'value')
    )
    def getGraph(children, dim):

        if (children == None):
            raise PreventUpdate

        download = [
            Div([
                Button(
                    'Download 1D',
                    id='1d-spec-download',
                    className='btn btn-primary btn-sm',
                ),
                Download(
                    id='1d-spec-download-data'
                ),
            ], className='px-1'),
            Div([
                Button(
                    'Download 2D',
                    id='2d-spec-download',
                    className='btn btn-primary btn-sm',
                ),
                Download(
                    id='2d-spec-download-data'
                ),
            ], className="px-1"),
        ]

        if (dim):
            return read_csv(fs.find_one({'filetype': '2d'})).to_json(), download, 'col', 'col d-none', 'Order Range\n'

        return read_csv(fs.find_one({'filetype': '1d'})).to_json(), download, 'col d-none', 'col', 'Resolution\n'

    return app
