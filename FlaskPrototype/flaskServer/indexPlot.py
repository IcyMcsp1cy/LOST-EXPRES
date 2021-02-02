from json import dumps
import numpy as np
import plotly
import plotly.graph_objs as go

def homepage_plot():

    N = 1000
    rand_x = np.random.randn(N)
    rand_y = np.random.randn(N)

    data = [go.Scatter(
        x = rand_x,
        y = rand_y,
        mode = 'markers'
    )]

    graphJSON = dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON