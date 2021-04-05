from flask import render_template, abort, request, redirect, url_for, session, g
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash_bootstrap_components import themes, Table
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash.exceptions import PreventUpdate
from flask_wtf.recaptcha.widgets import JSONEncoder
from plotly.express import scatter
import pandas as pd
import dash_table
from datetime import date
from ..extensions import mongo, JSONEncoder


url_base = "/admin/"

def init_admin( server ):

    external_stylesheets = [themes.BOOTSTRAP]

    app = Dash(
    '__main__',
    server=server,
    url_base_pathname=url_base,
    assets_folder='static',
    external_stylesheets=external_stylesheets
    )

    @server.before_request
    def adminDash():
        if str(request.endpoint).startswith(url_base):
            app.index_string = render_template(
                'admin.html',
                nav_elements = g.nav,
                title = date.today()
                )
    

    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-wrapper')
    ])

    file_manager = html.Div([
        html.H1('File Management', className='mb-2'),
        dcc.DatePickerSingle(
            id='date-picker',
            min_date_allowed=date(1995, 8, 5),
            max_date_allowed=date.today(),
            initial_visible_month=date.today(),
        ),
        html.Button('Submit', id='date-submit', className='btn mx-2'),
        html.Div(id='output-container-date-picker-single'),

        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=True
        ),
    ])

    news_manager = html.Div([
        html.H1('News Management', className='mb-2'),
        html.Br(),
        dcc.Input(
            id="news-title",
            type='text',
            placeholder="Post Title (Naming a post after another will replace that post)",
            className='w-75 form-control mb-2'
        ),
        dcc.Input(
            id="news-subtitle",
            type='text',
            placeholder="Subtitle",
            className='w-75 form-control mb-2'
        ),
        dcc.Input(
            id="news-author",
            type='text',
            placeholder="Author",
            className='w-50 form-control mb-2'
        ),
        dcc.Textarea(
            id='news-text',
            value='Text Block',
            style={'height': 300},
            className='input-group w-100 form-control pb-2'
        ),
        html.Button('Submit', id='news-submit', className='btn my-2'),
        html.Br()
    ], className='mb-4')


    glos_manager = html.Div([
        html.H1('Glossary Management', className='mb-2'),
        html.Br(),
        dcc.Input(
            id="glos-term",
            type='text',
            placeholder="Glossary Term (Naming a term after another will replace that term)",
            className='w-75 form-control mb-2'
        ),
        dcc.Textarea(
            id='glos-text',
            value='Text Block',
            style={'height': 50},
            className='input-group w-75 form-control pb-2'
        ),
        html.Button('Submit', id='glos-submit', className='btn my-2'),
        html.Br()
    ], className='mb-4')


    @app.callback(Output('page-wrapper', 'children'),
                Input('url', 'pathname'))
    def display_page(pathname):
        if pathname == url_base + 'news':
            news = list(mongo.db.news.find({}))
            df = pd.DataFrame(eval(JSONEncoder().encode(news)))
            table = Table.from_dataframe(
                df[['title', 'author', 'datetime']], 
                striped=True, 
                bordered=True, 
                hover=True
                )
            return [news_manager, table,]

        elif pathname == url_base + 'glossary':
            glos = list(mongo.db.glossary.find({}))
            df = pd.DataFrame(eval(JSONEncoder().encode(glos)))
            table = Table.from_dataframe(
                df[['entry', 'definition', 'datetime']], 
                striped=True, 
                bordered=True, 
                hover=True
                )
            return [glos_manager, table,]

        else:
            file = list(mongo.db.fs.files.find({}))
            df = pd.DataFrame(eval(JSONEncoder().encode(file)))
            table = Table.from_dataframe(
                df[['filename', 'filetype']], 
                striped=True, 
                bordered=True, 
                hover=True
                )
            return [file_manager, table,]



    @app.callback(
        Output('output-container-date-picker-single', 'children'),
        Input('date-submit', 'n_clicks'),
        State('date-picker', 'date'))
    def update_output(submit, date_value):
        string_prefix = 'You have selected: '
        if date_value is not None:
            date_object = date.fromisoformat(date_value)
            date_string = date_object.strftime('%B %d, %Y')
            return string_prefix + date_string

    return app