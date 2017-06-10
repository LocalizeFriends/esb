from flask import Flask
from flask import Response, request
from werkzeug.datastructures import MultiDict
import json
import traceback

app = Flask(__name__)

registered_consumers = MultiDict({
    # path: func(request)
})

def register_consumer(path, consumer):
    global registered_consumers
    registered_consumers.add(path, consumer)


class MethodNotAllowed(Exception):
    def __init__(self, allowed_methods):
        self.allowed_methods = allowed_methods
        self.headers = {
            'Allow': ','.join(allowed_methods)
        }
        message = 'Allowed methods: {}.'.format(','.join(allowed_methods))
        super(Exception, self).__init__(message)


def require_method(methods):
    if methods is not list:
        methods = [methods]
    def decorator(consumer):
        def wrapper(request, *args, **kwargs):
            if request.method not in methods:
                raise MethodNotAllowed(methods)
            return consumer(request, *args, **kwargs)
        wrapper.__name__ = consumer.__name__
        return wrapper
    return decorator


@app.route('/', methods=['GET', 'POST'], defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST'])
def entrance(path):
    consumers = registered_consumers.getlist(path)
    consumers_called_successfully = []
    exceptions = []

    for consumer in consumers:
        try:
            consumer(request)
            consumers_called_successfully.append(consumer.__name__)
        except MethodNotAllowed as e:
            pass
        except:
            exceptions.append({
                'consumer': consumer.__name__,
                'string': traceback.format_exc()
            })

    if len(exceptions) > 0:
        return Response(json.dumps({
            'errors': True,
            'consumers_called_successfully': consumers_called_successfully,
            'message': 'Exception(s) occured.',
            'exceptions': exceptions
        }), mimetype='application/json')

    return Response(json.dumps({
        'errors': False,
        'consumers_called_successfully': consumers_called_successfully,
    }), mimetype='application/json')
