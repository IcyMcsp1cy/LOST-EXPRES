from dash import Dash
from json import dumps
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from dash.dependencies import Input, Output, State, ClientsideFunction
from plotly.express import scatter
import pandas as pd

import numpy as np
import plotly
import plotly.graph_objs as go


#<nav class="navbar navbar-expand-md navbar-dark bg-dark fixed-top">
navbar = html.Nav([
    #<a class="navbar-brand" href="#">EXPRES</a>
    html.A("EXPRES", className="navbar-brand", href="#"),
    #<button class="navbar-toggler" type="button">
    html.Button([
        #<span class="navbar-toggler-icon"></span>
        html.Span(className="navbar-toggler-icon"),
    #</button>
    ], className="navbar-toggler", type="button"),
    #<div class="collapse navbar-collapse" id="navbarsExampleDefault">
    html.Div([
        #<ul class="navbar-nav mr-auto">
        html.Ul([
            #<li class="nav-item active">
            html.Li([
                #<a class="nav-link" href="/">Home
                html.A(["Home",
                    #<span class="sr-only">(current)</span></a>
                    html.Span("(current)", className="sr-only"),
                ], className="nav-link", href="/"),
            #</li>
            ], className="nav-item active"),
            #<li class="nav-item">
            html.Li([
                #<a class="nav-link" href="/news/">News</a>
                html.A("News", className="nav-link", href="/news/"),
            #</li>
            ], className="nav-item"),

            #<li class="nav-item">
            html.Li([
                #<a class="nav-link" href="/data/">Data</a>
                html.A("Data", className="nav-link", href="/data/"),
            #</li>
            ], className="nav-item"),
            #<li class="nav-item">
            html.Li([
                #<a class="nav-link" href="/glossary/">Appendix</a>
                html.A("Appendix", className="nav-link", href="/glossary/"),
            #</li>
            ], className="nav-item"),
            #<li class="nav-item">
            html.Li([
                #<a class="nav-link" href="/login/">Login</a>
                html.A("Login", className="nav-link", href="/login/"),
            #</li>
            ], className="nav-item"),
            #<li class="nav-item">
            html.Li([
                #<a class="nav-link" href="/account/">Account</a>
                html.A("Account", className="nav-link", href="/account/"),
            #</li>
            ], className="nav-item"),
        #</ul>
        ], className="navbar-nav mr-auto"),
    #</div>
    ], className="collapse navbar-collapse", id="navbarsExampleDefault"),
#</nav>
], className="navbar navbar-expand-md navbar-fixed-top navbar-dark bg-dark fixed-top")



def init_dash( server ):

    external_stylesheets = [dbc.themes.BOOTSTRAP]

    app = Dash(
    '__main__',
    server=server,
    url_base_pathname='/data/',
    assets_folder='static',
    external_stylesheets=external_stylesheets
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
        navbar,
        html.Br(className='pb-5'),
        dcc.Store(
            id='test',
            data=[{
                'x': df[['MJD']].to_json(),
                'y': df[['V']].to_json()
            }]
        ),
        html.Div(
            id = 'data',
            children = df.to_json(),
            className='d-none'
        ),
        html.Div(
            id = 'json',
        ),
        dcc.Graph(
            id='rv-plot',
            figure=rv_figure,
            className="pt-5"
        ),
        dcc.RangeSlider(
            id='range-slider',
            min=59000,
            max=59110,
            step=10,
            value=[59010, 59100]
        ),
        html.Div([
            dcc.Markdown("""
                **Click Data**
                Click on points in the graph.
            """),
            html.Pre(id='click-data'),
        ]),
        html.Div([], id='spec-container'),
        html.Div([
            dt.DataTable(id='rv-table',
                    columns=[{"name": i, "id": i} for i in df.columns][1::],
                    data=df.to_dict('records')),
        ], className=''),
        html.Br(className='pb-5'),
    ])



    app.clientside_callback(
        output=Output('click-data', 'children'),
        inputs=[Input('rv-plot', 'clickData'),
                State('rv-table', 'data')],
        clientside_function=ClientsideFunction(
            namespace='graphing',
            function_name ='clickData'
        )
    )



    app.clientside_callback(
        output=Output('rv-plot', 'figure'),
        inputs=[Input('range-slider', 'value'), State('data', 'children')],
        clientside_function=ClientsideFunction(
            namespace='graphing',
            function_name ='zoomfunc'
        )
    )

    # @app.callback(
    #     Output('json', 'children'),
    #     Input('rv-plot', 'figure')
    # )
    # def teststuff(figure):
    #     return dumps([fig], cls=plotly.utils.PlotlyJSONEncoder)

    @app.callback(
        Output('spec-container', 'children'),
        Input('click-data', 'children')
    )
    def getGraph(children):
        if(children == None):
            return

        return [dcc.Graph(
            id='spec-plot',
            figure=rv_figure,
            className="pt-5"
        ), children]
