from dash import Dash
from json import dumps
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from dash.dependencies import Input, Output
from plotly.express import scatter
import pandas as pd


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
    __name__,
    server=server,
    url_base_pathname='/data/',
    external_stylesheets=external_stylesheets
    )

    data = pd.read_csv('static/Sun.txt')
    df = data[data['ACCEPT'] == True]

    figure = scatter(df, x="MJD", y="V")
    figure.update_layout(clickmode='event')


    app.layout = html.Div([
        navbar,
        html.Br(className='pb-5'),
        dcc.Graph(
            id='basic-interactions',
            figure=figure,
            className="pt-5"
        ),
        html.Div([
            dcc.Markdown("""
                **Click Data**
                Click on points in the graph.
            """),
            html.Pre(id='click-data'),
        ]),
        html.Div([
            dcc.Markdown("""
                **Layout Data**
                Click on points in the graph.
            """),
            html.Pre(id='relayout-data'),
        ]),
        dt.DataTable(id='new-table',
                        columns=[{"name": i, "id": i} for i in df.columns][1::],
                        data=df.to_dict('records')),
        html.Br(className='pb-5'),
    ])

    @app.callback(
        Output('click-data', 'children'),
        Input('basic-interactions', 'clickData'))
    def display_hover_data(clickData):
        return dumps(clickData, indent=2)


    # app.clientside_callback(
    #     """
    #     function(relayoutData) {
    #         return ;
    #     }
    #     """,
    #     Output('relayout-data', 'children'),
    #     Output('new-table', 'data'),
    #     Input('basic-interactions', 'relayoutData')
    # )
    @app.callback(
        Output('relayout-data', 'children'),
        Output('new-table', 'data'),
        Input('basic-interactions', 'relayoutData'))
    def display_relayout_data(relayoutData):
        sel = None
        if relayoutData != None:
            sel = df.copy()
            if 'xaxis.range[0]' in relayoutData:
                sel = df[df['MJD'] > relayoutData['xaxis.range[0]']]
                sel = sel[sel['MJD'] < relayoutData['xaxis.range[1]']]
                sel = sel[sel['V'] > relayoutData['yaxis.range[0]']]
                sel = sel[sel['V'] < relayoutData['yaxis.range[1]']]
                return dumps(relayoutData, indent=2), sel.to_dict('records') 
        return dumps(relayoutData, indent=2), df.to_dict('records')

    return app 
