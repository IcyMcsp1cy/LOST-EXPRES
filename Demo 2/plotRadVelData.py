import plotly.graph_objs as go
import plotly.io as pio
import mysql.connector
import pandas as pd

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="solar_expres"
)

mycursor = mydb.cursor()
mycursor.execute('select mjd, radVelocity, expTime, ev, filename from radialvelocity');

rows = mycursor.fetchall()
if(rows != []):
    print("not empty")
else:
    exit(1)

df = pd.DataFrame( [[ij for ij in i] for i in rows] )
df.rename(columns={0: 'MJD', 1: 'RadialVelocity', 2: 'ExposureTime', 3: 'EV', 4:'FileName'}, inplace=True)

trace1 = go.Scatter(
    x=df['MJD'],
    y=df['RadialVelocity'],
    text="",
    mode='markers'
)
layout = go.Layout(
    title='Radial Velocity vs MJD from MySQL database',
    xaxis=dict( type='log', title='MJD' ),
    yaxis=dict( title='Radial Velocity' )
)
data = [trace1]
fig = go.Figure(data=data, layout=layout)

import dash
import dash_core_components as dcc
import dash_html_components as html

colors = {
    'background': '#2b2d2f',
    'text': '#d1edf2'
}


fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

app = dash.Dash()
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='SOLAR EXPRES',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='Tech Demo #2', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Graph(
        id='example-graph-2',
        figure=fig
    )
])

app.run_server(debug=True, use_reloader=False)
# pio.write_html(fig, file="index.html", auto_open=True)
