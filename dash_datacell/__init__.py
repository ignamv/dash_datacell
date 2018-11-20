import logging
import random
from flask import session

import dash_html_components as html
from dash.dependencies import Input, Output
from cache import SimpleCache

__all__ = ['DashDataCell']

logger = logging.getLogger(__name__)

class SessionSpecificCache(object):
    def __init__(self, cache):
        self.cache = cache

    def session_id(self):
        try:
            return session['cache_id']
        except KeyError:
            ret = random.randint(0, 0xffffffffffffffff)
            session['cache_id'] = ret
            return ret

    def get(self, key):
        return self.cache.get((self.session_id, key))

    def set(self, key, value):
        self.cache.set((self.session_id, key), value)

cache = SessionSpecificCache(SimpleCache())

class DashDataCell(object):
    def __init__(self):
        self.div_id = 'datacell_{:08x}'.format(random.randint(0,0xffffffff))
        self.counter = 0

    def output(self):
        """dash.dependencies.Output for passing to app.callback()"""
        return Output(self.div_id, 'children')

    def input(self):
        """dash.dependencies.Input for passing to app.callback()"""
        return Input(self.div_id, 'children')

    def get(self):
        """Return value of the cell"""
        return cache.get(self.div_id)

    def set(self, value):
        """Set value of the cell. Return counter which increments on each modification"""
        if value != self.get():
            self.counter += 1
            cache.set(self.div_id, value)
        return self.counter

    def add_to_layout(self, layout):
        """Insert hidden div into layout if not already present"""
        logger.debug('Add to layout DashDataCell id %s', self.div_id)
        if self.div_id not in layout.keys():
            layout.children.append(html.Div(id=self.div_id, className='datacell', style={'display': 'none'}))

    @classmethod
    def wrap_output(cls, output):
        """If output is a DashDataCell, replace it with a real dash.dependency.Output"""
        if isinstance(output, cls):
            return output.output()
        else:
            return output

    @classmethod
    def wrap_input(cls, input_):
        """If input is a DashDataCell, replace it with a real dash.dependency.Input"""
        if isinstance(input_, cls):
            return input_.input()
        else:
            return input_

    @classmethod
    def get_inputs(cls, inputs, args):
        """Replace args that correspond to DashDataCells with the value of the cell"""
        for input_, arg in zip(inputs, args):
            if isinstance(input_, cls):
                yield input_.get()
            else:
                yield arg

    @classmethod
    def set_output(cls, output, result):
        """If output is a DashDataCell, set the cell value and return the change counter instead"""
        if isinstance(output, cls):
            return output.set(result)
        else:
            return result

    @classmethod
    def add_hidden_divs(cls, app, *inoutputs):
        """Insert into layout hidden divs for all arguments that are DashDataCells"""
        for inoutput in inoutputs:
            if isinstance(inoutput, cls):
                inoutput.add_to_layout(app.layout)

    @classmethod
    def callback(cls, app, output, inputs):
        """Use this like app.callback, except you can use DashDataCells as an Input/Output"""
        real_output = cls.wrap_output(output)
        real_inputs = map(cls.wrap_input, inputs)
        def ret(innerfunc):
            cls.add_hidden_divs(app, output, *inputs)
            def wrapper(*args):
                logger.debug('Wrapper got args %s', args)
                mapped_args = list(cls.get_inputs(inputs, args))
                logger.debug('Wrapper passing args %s', mapped_args)
                result = innerfunc(*mapped_args)
                logger.debug('Wrapper got result %s', result)
                mapped_result = cls.set_output(output, result)
                logger.debug('Wrapper returning %s', mapped_result)
                return mapped_result
            return app.callback(real_output, real_inputs)(wrapper)
        return ret
