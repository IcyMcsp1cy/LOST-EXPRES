from flask import render_template, abort, request, redirect, url_for, session, g
from dash import Dash, callback_context
from flask_login import current_user
import dash_core_components as dcc
import dash_html_components as html
from dash_bootstrap_components import themes, Table, Alert, Card, CardBody, CardHeader, Button
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash.exceptions import PreventUpdate
from flask_wtf.recaptcha.widgets import JSONEncoder
from plotly.express import scatter
import pandas as pd
import dash_table
import uuid
import julian
from datetime import date, datetime
from bson.objectid import ObjectId
from ..extensions import mongo, JSONEncoder
from ..config import csv_label
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
            app.index_string = render_template('admin.html')
            if current_user.is_authenticated and current_user.accountType == 'admin':
                return
            abort(403)
            
    

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

    def getFiles():
        file = list(mongo.db.fs.files.find({}))
        df = pd.DataFrame(eval(JSONEncoder().encode(file)))
        
        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[
                {'id': 'filename', 'name': 'File Name'},
                {'id': 'filetype', 'name': 'Type'},
                {'id': 'uploadDate', 'name': 'Date'},
            ],
            style_cell_conditional=[
                {
                    'if': {'column_id': c},
                    'textAlign': 'left'
                } for c in ['Date', 'Region']
            ],
            style_as_list_view=True,
            id='file-table'
        )
        return [file_manager, table]



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
            placeholder='Entry Text',
            style={'height': 50},
            className='input-group w-75 form-control pb-2'
        ),
        html.Button('Submit', id='glos-submit', className='btn my-2'),
        html.Button('Delete', id='glos-delete', className='btn my-2 mx-2 d-none'),
        html.Div(className='', id='glos-alert'),
        html.Div(className='', id='glos-alert-2'),
        html.Br()
    ], className='mb-4')


    def getGlos():
        glos = list(mongo.db.glossary.find({}))
        df = pd.DataFrame(eval(JSONEncoder().encode(glos)))
        
        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[
                {'id': 'entry', 'name': 'Entry'},
                {'id': 'definition', 'name': 'Definition'},
                {'id': 'datetime', 'name': 'Date'},
            ],
            style_cell={
                'whiteSpace': 'normal',
                'height': 'auto',
            },
            style_cell_conditional=[
                {
                    'if': {'column_id': c},
                    'textAlign': 'left'
                } for c in ['entry', 'definition']
            ],
            style_as_list_view=True,
            id='glos-table',
        )
        return [glos_manager, table,]


    @app.callback(
        Output('glos-term', 'value'),
        Output('glos-text', 'value'),
        Output('glos-delete', 'className'),
        Input('glos-table', 'data'),
        Input('glos-table', 'active_cell'),
    )
    def selectGlos(data, cell):
        if cell and data and len(data) > cell['row']:
            record = data[cell['row']]
            return record['entry'], record['definition'], 'btn my-2 mx-2'
        raise PreventUpdate


    @app.callback(
        Output('glos-alert', 'children'),
        Output('glos-table', 'data'),
        Input('glos-submit', 'n_clicks'),
        Input('glos-delete', 'n_clicks'),
        State('glos-term', 'value'),
        State('glos-text', 'value'),
        State('glos-table', 'data'))
    def editGlos(submit, delete, term, definition, table):

        changed_id = [p['prop_id'] for p in callback_context.triggered][0]
        if 'glos-submit' in changed_id:
            for val in [term, definition]:
                if val is None or val == '':
                    return Alert(
                        "Please fill out all fields",
                        id="alert-auto",
                        is_open=True,
                        duration=10000,
                        color='danger'
                    ), table.to_dict('records')

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
            
            news = list(mongo.db.glossary.find({}))
            df = pd.DataFrame(eval(JSONEncoder().encode(news)))

            return Alert(
                ["Glossary Updated"],
                id="alert-auto",
                is_open=True,
                duration=10000,
            ), df.to_dict('records')
        elif 'glos-delete' in changed_id:
            result = mongo.db.glossary.find_one({'entry': term})
            if(result):
                mongo.db.glossary.delete_one(
                    {'_id': result['_id']}
                )
                alert = Alert([
                    "Post Deleted"
                    ],
                    id="alert-auto",
                    is_open=True,
                    duration=10000,
                )
            else:
                alert = Alert(
                    "Post does not exist",
                    id="alert-auto",
                    is_open=True,
                    duration=10000,
                    color='danger'
                )
            news = list(mongo.db.glossary.find())
            df = pd.DataFrame(eval(JSONEncoder().encode(news)))
            return alert, df.to_dict('records')
        else:
            raise PreventUpdate

            
       


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
            placeholder='Lorem Ipsum Dolor',
            style={'height': 100},
            className='input-group w-100 form-control pb-2'
        ),
        Button('Submit', id='news-submit', className='btn my-2', n_clicks=0, color='success'),
        Button('Delete', id='news-delete', className='btn my-2 mx-2 d-none', n_clicks=0, color='danger'),
        Button('Set on Homepage', id='news-home', className='btn my-2 mx-2 d-none', n_clicks=0, color='secondary'),
        html.Div(className='', id='news-alert'),
        html.Div(className='', id='news-alert-2'),
        html.Br()
    ], className='mb-4')

    def getNews():
        news = list(mongo.db.news.find({}))
        df = pd.DataFrame(eval(JSONEncoder().encode(news)))

        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[
                {'id': 'title', 'name': 'Post Title'},
                {'id': 'author', 'name': 'Author'},
                {'id': 'datetime', 'name': 'Date'},
            ],
            style_cell={
                'whiteSpace': 'normal',
                'height': 'auto',
            },
            style_cell_conditional=[
                {
                    'if': {'column_id': c},
                    'textAlign': 'left'
                } for c in ['title', 'author']
            ],
            style_as_list_view=True,
            id='news-table',
        )
        return [news_manager, table,]


    @app.callback(
        Output('news-title', 'value'),
        Output('news-subtitle', 'value'),
        Output('news-author', 'value'),
        Output('news-text', 'value'),
        Output('news-delete', 'className'),
        Output('news-home', 'className'),
        Input('news-table', 'data'),
        Input('news-table', 'active_cell'),
    )
    def selectNews(data, cell):
        if cell and data and len(data) > cell['row']:
            record = data[cell['row']]
            return record['title'], record['subtitle'], record['author'], record['content'], 'btn my-2 mx-2', 'btn my-2 mx-2'
        raise PreventUpdate


    @app.callback(
        Output('news-alert', 'children'),
        Output('news-table', 'data'),
        Input('news-submit', 'n_clicks'),
        Input('news-delete', 'n_clicks'),
        Input('news-home', 'n_clicks'),
        State('news-title', 'value'),
        State('news-subtitle', 'value'),
        State('news-author', 'value'),
        State('news-text', 'value'),
        State('news-table', 'data'))
    def editNews(submit, delete, home, title, subtitle, author, text, table):

        changed_id = [p['prop_id'] for p in callback_context.triggered][0]
        if 'news-submit' in changed_id:
            for val in [title, subtitle, author, text]:
                if val is None or val == '':
                    return Alert(
                        "Please fill out all fields",
                        id="alert-auto",
                        is_open=True,
                        duration=10000,
                        color='danger'
                    ), table.to_dict('records')

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
                        'datetime': datetime.now().strftime('%B %d, %Y')
                    }
                )
            else:
                post = {
                    '_id': ObjectId(),
                    'title': title,
                    'subtitle': subtitle,
                    'author': author,
                    'content': text,
                    'datetime': datetime.now().strftime('%B %d, %Y')
                }

                mongo.db.news.insert_one(post)

            url = url_for('post', post_id=str(post['_id']))
            
            news = list(mongo.db.news.find({}))
            df = pd.DataFrame(eval(JSONEncoder().encode(news)))

            return Alert([
                "Article posted to ",
                html.A("this link", href=url, className="alert-link")
                ],
                id="alert-auto",
                is_open=True,
                duration=10000,
            ), df.to_dict('records')

        elif 'news-delete' in changed_id:
            post = mongo.db.news.find_one({'title': title})
            if(post):
                mongo.db.news.delete_one(
                    {'_id': post['_id']}
                )
                alert = Alert([
                    "Post Deleted"
                    ],
                    id="alert-auto",
                    is_open=True,
                    duration=10000,
                )
            else:
                alert = Alert(
                    "Post does not exist",
                    id="alert-auto",
                    is_open=True,
                    duration=10000,
                    color='danger'
                )
            news = list(mongo.db.news.find().sort('datetime', DESCENDING))
            df = pd.DataFrame(eval(JSONEncoder().encode(news)))
            return alert, df.to_dict('records')
        elif 'news-home' in changed_id:
            post = mongo.db.news.find_one({'title': title})
            if(post):
                mongo.db.news.update_one({'location': 'home'}, {'$set': {'location': 'default'}}, True)
                mongo.db.news.update_one({'_id': post['_id']}, {'$set': {'location': 'home'}}, True)
                alert = Alert([
                    "Post set as home"
                    ],
                    id="alert-auto",
                    is_open=True,
                    duration=10000,
                )
            else:
                alert = Alert(
                    "Post does not exist",
                    id="alert-auto",
                    is_open=True,
                    duration=10000,
                    color='danger'
                )
            news = list(mongo.db.news.find().sort('datetime', DESCENDING))
            df = pd.DataFrame(eval(JSONEncoder().encode(news)))
            return alert, df.to_dict('records')
        else:
            raise PreventUpdate

        


    user_manager = html.Div([
        html.H1('User Management', className='mb-2'),
        html.Br(),
        html.Div([
            html.P('', className="d-none", id='user-email'),
        ], id='user-display'),
        Button('Verify', id='user-verify', className='btn my-2 mx-2 d-none', color='success'),
        Button('Reject', id='user-reject', className='btn my-2 mx-2 d-none', color='danger'),
        html.Br(),
        html.Div([
            Button('Purge Unverified Users', id='user-purge', className='btn my-2 mx-2', color='warning'),
        ],className='text-right', id='user-control'),
        html.Div(className='', id='user-alert'),
        
    ], className='mb-4')


    def getUser():
        users = list(mongo.db.user.find({}))
        df = pd.DataFrame(eval(JSONEncoder().encode(users)))
        
        table = dash_table.DataTable(
            data=df[['firstName', 'lastName', 'email', 'institution', 'type']].to_dict('records'),
            columns=[
                {'id': 'firstName', 'name': 'First'},
                {'id': 'lastName', 'name': 'Last'},
                {'id': 'email', 'name': 'Email'},
                {'id': 'institution', 'name': 'Institution'},
                {'id': 'type', 'name': 'Type'},
            ],
            style_cell={
                'whiteSpace': 'normal',
                'height': 'auto',
            },
            style_cell_conditional=[  
                {
                    'if': {'column_id': c},
                    'textAlign': 'left'
                } for c in ['lastName', 'institution']
            ]+[
                {   
                    'if': {
                        'filter_query': '{type} = "unverified"',
                    },
                    'color': '#ffc107',
                    'fontWeight': 'bold'
                },  
                {   
                    'if': {
                        'row_index': -1,
                        'column_id': 'type'
                    },
                    'backgroundColor': 'black'
                },  
            ],
            style_as_list_view=True,
            id='user-table',
        )
        return [user_manager, table,]



    @app.callback(
        Output('user-display', 'children'),
        Output('user-verify', 'className'),
        Output('user-reject', 'className'),
        Input('user-table', 'data'),
        Input('user-table', 'active_cell'),
    )
    def selectUser(data, cell):
        if cell and data and len(data) > cell['row']:
            record = data[cell['row']]
            type = record['type']
            color = 'secondary'
            dNone = ' d-none'
            if type == 'unverified':
                color = 'warning'
                dNone = ''
            elif type == 'researcher':
                color='primary'
            elif type == 'admin':
                color='danger'
            #'btn my-2 mx-2'
            return Card([
                    CardBody(
                        [
                            
                            html.H4(record['firstName']+" "+record['lastName'],
                                className="card-title text-"+color),
                            html.H6(record['institution'], className="card-subtitle"),
                            html.P(
                                record['email'],
                                className="card-text",
                                id='user-email'
                            ),
                            html.B(
                                "Unverified" if record['type'] == 'unverified' else record['type'],
                                className="card-text",
                            ),
                        ]
                    )],
                    style={"width": "18rem"},
                    className='border border-5 border-' + color
                ), 'btn my-2 mx-2'+dNone, 'btn my-2 mx-2'+dNone
        raise PreventUpdate


    @app.callback(
        Output('user-alert', 'children'),
        Output('user-table', 'data'),
        Input('user-verify', 'n_clicks'),
        Input('user-reject', 'n_clicks'),
        Input('user-purge', 'n_clicks'),
        State('user-email', 'children'),
        State('user-table', 'data'))
    def editUser(verify, reject, purge, email, table):
        print('test')
        changed_id = [p['prop_id'] for p in callback_context.triggered][0]
        if 'user-verify' in changed_id:
            if email is None or email == '':
                return Alert(
                    "Please select user",
                    id="alert-auto",
                    is_open=True,
                    duration=10000,
                    color='danger'
                ), table.to_dict('records')
                    

            entry = mongo.db.user.find_one({'email': email})
            
            if(entry):
                mongo.db.user.update_one(
                    {'_id': entry['_id']},
                    {"$set": 
                        {'type': 'researcher'}
                    }
                )
            else:
                return Alert(
                    "Please select user",
                    id="alert-auto",
                    is_open=True,
                    duration=10000,
                    color='danger'
                ), table.to_dict('records')
                
            
            result = list(mongo.db.user.find({}))
            df = pd.DataFrame(eval(JSONEncoder().encode(result)))

            return Alert(
                ["User Verified"],
                id="alert-auto",
                is_open=True,
                duration=10000,
            ), df.to_dict('records')
        elif 'user-reject' in changed_id:
            result = mongo.db.user.find_one({'email': email})
            if(result):
                mongo.db.user.delete_one(
                    {'_id': result['_id']}
                )
                alert = Alert([
                    "User Rejected"
                    ],
                    id="alert-auto",
                    is_open=True,
                    duration=10000,
                )
            else:
                alert = Alert(
                    "User does not exist",
                    id="alert-auto",
                    is_open=True,
                    duration=10000,
                    color='danger'
                )
            news = list(mongo.db.user.find())
            df = pd.DataFrame(eval(JSONEncoder().encode(news)))
            return alert, df.to_dict('records')

        elif 'user-purge' in changed_id:
            removed = mongo.db.user.remove({'type': 'unverified'})
            news = list(mongo.db.user.find())
            df = pd.DataFrame(eval(JSONEncoder().encode(news)))
            return Alert(
                "Applicants Deleted",
                id="alert-auto",
                is_open=True,
                duration=10000,
                color='danger'
            ), df.to_dict('records')
        else:
            raise PreventUpdate

            

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

    

    @app.callback(
        Output('page-wrapper', 'children'),
        Input('url', 'pathname'))
    def display_page(pathname):
        if pathname == url_base + 'news':
            return getNews()
        elif pathname == url_base + 'glossary':
            return getGlos()
        elif pathname == url_base + 'files':
            return getFiles()
        else:
            return getUser()

    
    return app
