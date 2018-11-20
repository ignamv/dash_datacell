import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import logging

from datacell import DashDataCell

logger = logging.getLogger('datacell')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

app = dash.Dash(__name__)
app.server.secret_key = '4ad6ccdfdbdafa7cda29542e6dfac3fd385d684a8645913c292e1c76805b09d1'

app.layout = html.Div([
    dcc.Input(id='in1', value='1'),
    html.Div(id='out1'),
])

# This class represents an object which you might want to pass between
# callbacks without using a hidden Div.
# It might be too large, or not even serializable
class HugeObject(object):
    def __getstate__(self):
        raise Exception('Not serializable')

# This instance can be used as an Input or Output in a callback
cell = DashDataCell()

@DashDataCell.callback(app, cell, [Input('in1', 'value')])
def output_arbitrary_object(inp):
    """
    This callback returns an object which cannot be serialized
    
    You couldn't put this in a hidden Div. 
    But with DashDataCell, the return value stays in the server without having
    to serialize it or send it through the network.
    """
    ret = HugeObject()
    ret.some_attribute = inp
    return ret

@DashDataCell.callback(app, Output('out1', 'children'), [cell])
def input_arbitrary_object(inp):
    """Receive an object just as it was returned by the previous callback"""
    return [html.Pre(repr(inp)), html.Pre(repr(inp.some_attribute))]

app.run_server(debug=True)
