# dash_datacell

Pass data between callbacks without going through the network or futzing with hidden divs.

## Usage

```python
from dash_datacell import DashDataCell

# This instance can be used as an Input or Output in callbacks
cell = DashDataCell()

@DashDataCell.callback(app, cell, [Input('normal_input', 'value')])
def output_arbitrary_object(normal_input):
    """Return an object, which won't be sent through the network"""
    return SomeHugeObject()

@DashDataCell.callback(app, Output('normal_output', 'children'), [cell])
def input_arbitrary_object(huge_object):
    """Receive an object ready for use"""
    return str(huge_object)
```

