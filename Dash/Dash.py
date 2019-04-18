import dash
import dash_core_components as dcc
import dash_html_components as html
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import Plotting.plot_funcs as pf
from KeyEventParser import vkconvert
import numpy as np

ddd = np.load('../hkm_data.npy')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Dash Test App'),
    
    html.Div(children='''
             Dash: a web application framework for Python.
             '''),
    dcc.Graph(
        id='tgplot',
        style={
            'height':800
        },
        figure = pf.plot_tri_matrix(ddd,vkconvert)
    ),
    
    #dcc.Graph(
    #    id='example-graph',
    #    figure = {
    #        'data': [
    #            {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
    #            {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
    #        ],
    #        'layout': {
    #            'title': 'Dash Data Visualization'
    #        }
    #    }
    #)
])

if __name__ == '__main__':
    app.run_server(debug=True)