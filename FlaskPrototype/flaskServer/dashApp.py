import dash
from dash import Dash
from json import dumps
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from dash.dependencies import Input, Output, State
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
    assets_folder='static',
    external_stylesheets=external_stylesheets
    )

    data = pd.read_csv('static/Sun.txt')
    df = data[data['ACCEPT'] == True]

    rv_figure = scatter(df, x="MJD", y="V")
    rv_figure.update_layout(clickmode='event')


    app.layout = html.Div([
        navbar,
        html.Br(className='pb-5'),
        dcc.Graph(
            id='rv-plot',
            figure=rv_figure,
            className="pt-5"
        ),
    # Input field for axes changes in text box
        html.Label('Edit X and Y axes range here:'),
            html.Div(
            dcc.Input(placeholder='(X)-(X)', id='input-on-submit-x', type='text')),
            dcc.Input(placeholder='(Y)-(Y)', id='input-on-submit-y', type='text'),
                html.Button('Submit', id='submit-button-state', n_clicks=0),
                    html.Div(id='output-state'),

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
        ], className='d-none'),
        html.Br(className='pb-5'),
    ])

    # @app.callback(
    #     Output('click-data', 'children'),
    #     Input('basic-interactions', 'clickData'))
    # def display_hover_data(clickData):
    #     return dumps(clickData, indent=2)


    # app.clientside_callback(
    #     """
    #     function(relayoutData) {
    #         console.log(relayoutData);
    #         let obj = JSON.stringify(relayoutData);
    #         return obj;
    #     }
    #     """,
    #     Output('click-data', 'children'),
    #     Input('rv-plot', 'clickData')
    # )

    app.clientside_callback(
        """
        function(clickData, table) {
            if(clickData === undefined) {
                return;
            }
            console.log(table);

            let pointData = clickData.points[0];
            let data = JSON.stringify(table[pointData.pointIndex].FILENAME)

            return data;
        }
        """,
        Output('click-data', 'children'),
        Input('rv-plot', 'clickData'),
        Input('rv-table', 'data')
    )
    @app.callback(Output('output-state', 'children'),
                  Input('submit-button-state', 'n_clicks'),
                  State('input-on-submit-x', 'value'),
                  State('input-on-submit-y', 'value'))
    def update_output(n_clicks, input1, input2):
        return u'''
            The Button has been pressed {} times,
            Input 1 is "{}",
            and Input 2 is "{}"
        '''.format(n_clicks, input1, input2)

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


    # @app.callback(
    #     Output('relayout-data', 'children'),
    #     Output('new-table', 'data'),
    #     Input('basic-interactions', 'relayoutData'))
    # def display_relayout_data(relayoutData):
    #     sel = None
    #     if relayoutData != None:
    #         sel = df.copy()
    #         if 'xaxis.range[0]' in relayoutData:
    #             sel = df[df['MJD'] > relayoutData['xaxis.range[0]']]
    #             sel = sel[sel['MJD'] < relayoutData['xaxis.range[1]']]
    #             sel = sel[sel['V'] > relayoutData['yaxis.range[0]']]
    #             sel = sel[sel['V'] < relayoutData['yaxis.range[1]']]
    #             return dumps(relayoutData, indent=2), sel.to_dict('records') 
    #     return dumps(relayoutData, indent=2), df.to_dict('records')

    # return app 
