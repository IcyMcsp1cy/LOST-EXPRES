from flask import render_template, abort, request, redirect, url_for, session, g
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash_bootstrap_components import themes, Table, Alert
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash.exceptions import PreventUpdate
from flask_wtf.recaptcha.widgets import JSONEncoder
from plotly.express import scatter
import pandas as pd
import dash_table
import uuid
from datetime import date, datetime
from bson.objectid import ObjectId
from ..extensions import mongo, JSONEncoder
from pymongo import DESCENDING


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
        html.Div(className='', id='news-alert'),
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
        html.Div(className='', id='glos-alert'),
        html.Br()
    ], className='mb-4')


    @app.callback(Output('page-wrapper', 'children'),
                Input('url', 'pathname'))
    def display_page(pathname):
        if pathname == url_base + 'news':
            news = list(mongo.db.news.find({}))
            df = pd.DataFrame(eval(JSONEncoder().encode(news)))
            table = html.Div([
                Table.from_dataframe(
                    df[['title', 'author', 'datetime']],
                    striped=True,
                    bordered=True,
                    hover=True,
                )
            ], id='news-table')
            return [news_manager, table,]

        elif pathname == url_base + 'glossary':
            glos = list(mongo.db.glossary.find({}))
            df = pd.DataFrame(eval(JSONEncoder().encode(glos)))
            table = html.Div([
                Table.from_dataframe(
                    df[['entry', 'definition', 'datetime']],
                    striped=True,
                    bordered=True,
                    hover=True,
                )
            ], id='glos-table')
            return [glos_manager, table,]

        else:
            file = list(mongo.db.fs.files.find({}))
            df = pd.DataFrame(eval(JSONEncoder().encode(file)))
            table = html.Div([
                Table.from_dataframe(
                    df[['filename', 'filetype']],
                    striped=True,
                    bordered=True,
                    hover=True,
                )
            ], id='file-table')
            return [file_manager, table,]


    @app.callback(
        [Output('glos-alert', 'children'),
        Output('glos-table', 'children')],
        [Input('glos-submit', 'n_clicks')],
        [State('glos-term', 'value'),
        State('glos-text', 'value'),
        State('glos-table', 'children')])
    def edit_glossary(submit, term, definition, table):
        if submit is None:
            raise PreventUpdate
        for val in [term, definition]:
            if val is None or val == '':
                return Alert(
                    "Please fill out all fields",
                    id="alert-auto",
                    is_open=True,
                    duration=10000,
                    color='danger'
                ), table

        entry = mongo.db.glossary.find_one({'entry': term})

        if(entry):
            mongo.db.glossary.replace_one(
                {'_id': entry['_id']},
                {
                    '_id': entry['_id'],
                    'entry': term,
                    'definition': definition,
                    'datetime': datetime.now()
                }
            )
        else:
            entry = {
                '_id': ObjectId(),
                'entry': term,
                'definition': definition,
                'datetime': datetime.now()
            }

            mongo.db.glossary.insert_one(
                {
                    '_id': entry['_id'],
                    'entry': term,
                    'definition': definition,
                    'datetime': datetime.now()
                }
            )

        news = list(mongo.db.glossary.find({}).sort('datetime', DESCENDING))
        df = pd.DataFrame(eval(JSONEncoder().encode(news)))

        return Alert(
            [
                "Glossary Updated"
            ],
            id="alert-auto",
            is_open=True,
            duration=10000,
        ), Table.from_dataframe(
            df[['entry', 'definition', 'datetime']],
            striped=True,
            bordered=True,
            hover=True,
        )

    @app.callback(
        [Output('news-alert', 'children'),
        Output('news-table', 'children'),],
        Input('news-submit', 'n_clicks'),
        State('news-title', 'value'),
        State('news-subtitle', 'value'),
        State('news-author', 'value'),
        State('news-text', 'value'),
        State('news-table', 'children'))
    def edit_news(submit, title, subtitle, author, text, table):

        if submit is None:
            raise PreventUpdate
        for val in [title, subtitle, author, text]:
            if val is None or val == '':
                return Alert(
                    "Please fill out all fields",
                    id="alert-auto",
                    is_open=True,
                    duration=10000,
                    color='danger'
                ), table

        post = mongo.db.news.find_one({'title': title})


        if(post):
            mongo.db.news.replace_one(
                {'_id': post['_id']},
                {
                    '_id': post['_id'],
                    'title': title,
                    'subtitle': subtitle,
                    'author': author,
                    'content': text,
                    'datetime': datetime.now().strftime('%B %d, %Y'),
                    'locationtype': "default"
                }
            )
        else:
            post = {
                '_id': ObjectId(),
                'title': title,
                'subtitle': subtitle,
                'author': author,
                'content': text,
                'datetime': datetime.now().strftime('%B %d, %Y'),
                'locationtype': "default"
            }

            mongo.db.news.insert_one(post)

        url = url_for('post', post_id=str(post['_id']))

        news = list(mongo.db.news.find().sort('datetime', DESCENDING))
        df = pd.DataFrame(eval(JSONEncoder().encode(news)))

        return Alert([
            "Article posted to ",
            html.A("this link", href=url, className="alert-link")
            ],
            id="alert-auto",
            is_open=True,
            duration=10000,
        ),Table.from_dataframe(
            df[['title', 'author', 'datetime']],
            striped=True,
            bordered=True,
            hover=True,
        )


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
