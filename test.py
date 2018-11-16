import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import logging

from datacell import DataCell

logger = logging.getLogger('datacell')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

app = dash.Dash(__name__)
app.server.secret_key = '4ad6ccdfdbdafa7cda29542e6dfac3fd385d684a8645913c292e1c76805b09d1'

app.layout = html.Div([
    dcc.Input(id='in1', value='1'),
    html.Div(id='out1'),
])

class MyClass(object):
    pass

cell = DataCell()

@DataCell.mycallback(app, cell, [Input('in1', 'value')])
def output_arbitrary_object(inp):
    ret = MyClass()
    ret.somekey = [c.upper() for c in inp]
    return ret#.somekey

@DataCell.mycallback(app, Output('out1', 'children'), [cell])
def input_arbitrary_object(inp):
    return [html.Pre(repr(inp)), html.Pre(repr(inp.somekey))]

app.run_server(debug=True)
