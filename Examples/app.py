 #* Run this app with `python app.py` and
 #* visit http://127.0.0.1:8050/ in your web browser



from flask import Flask, render_template, abort

#~ Flask Server Setup
#~=============================================================================
server = Flask(__name__)

#~ Error Handling
@server.errorhandler(404)
def not_found(e):
    return '<h1>404 not found</h1>', 404

#~ Server Routing
@server.route('/')
def index():
    return render_template('index.html')

#~ serve file named in extension
@server.route('/<string:page_name>/')
def render_static(page_name):
    try:
        page = render_template('%s.html' % page_name)
    except:
        abort(404, not_found)

    return page
#~=============================================================================





from pandas import read_csv
from plotly.express import scatter

#* Plotly Figure
#*=============================================================================
dataframe = read_csv('Sun.txt')
figure = scatter(dataframe, x="MJD", y="V")
#*=============================================================================





from dash import Dash
import dash_bootstrap_components as dbc

#? Dash pages setup
#?=============================================================================
external_stylesheets = [dbc.themes.BOOTSTRAP]

app1 = Dash(
    __name__,
    server=server,
    url_base_pathname='/dash/',
    external_stylesheets=external_stylesheets
)

app2 = Dash(
    __name__,
    server=server,
    url_base_pathname='/dash1/',                         #? Has unique pathname
    external_stylesheets=external_stylesheets
)
#?=============================================================================





import dash_core_components as dcc
import dash_html_components as html
from datetime import date

#? Defining App Layouts
#?=============================================================================
app1.layout = html.Div(
    [
        html.H1("App 1", className="display-3"),

        dcc.DatePickerRange(
            month_format='MMMM Y',
            end_date_placeholder_text='MM/DD/YY',
            start_date=date(2019,6,21)
        ),

        dcc.Graph(
            id='example-graph',
            figure=figure
        )
    ]
)

app2.layout = html.Div(
    [
        html.H1("App 2", className="display-3"),

        html.Hr(className="my-2"),
        
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(html.Div(
                            [   "Input: ",
                                dcc.Input(id='my-input', 
                                        value='reactive test', 
                                        type='text')
                            ]
                        ), width=3),
                        dbc.Col(html.Div(id='my-output')),
                        dbc.Col(dbc.ButtonGroup(
                                    [
                                        dbc.Button("First", id="first"),
                                        dbc.Button("Second", id="second"),
                                        dbc.DropdownMenu(
                                            [dbc.DropdownMenuItem("Item 1"), 
                                             dbc.DropdownMenuItem("Item 2")],
                                            label="Dropdown",
                                            group=True,
                                        ),
                                    ]
                                ), width=3),
                    ]
                ),
            ]
        )
    ]
)
#?=============================================================================





from dash.dependencies import Input, Output

#* Define app callbacks
#*=============================================================================
@app2.callback(
    Output(component_id='my-output', component_property='children'),
    Input(component_id='my-input', component_property='value')
)
def update_output_div(input_value):
    return 'Output: {}'.format(input_value)
#*=============================================================================





#! Run Server
#!=============================================================================
if __name__ == '__main__':
    app1.run_server(debug=True)
#!=============================================================================