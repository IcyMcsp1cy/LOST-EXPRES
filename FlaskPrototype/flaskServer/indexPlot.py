from json import dumps
import numpy as np
import plotly
import plotly.graph_objs as go

def homepage_plot():

    N = 1000
    rand_x = np.random.randn(N)
    rand_y = np.random.randn(N)


    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x= rand_x,
        y= rand_y,
        mode="markers",
        marker=go.scatter.Marker(
            opacity=0.6,
            colorscale="Viridis"
        )
    ))

    #return html.Img(src=img_b64, style={'width': '100%'})

    graphJSON = dumps([fig], cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON