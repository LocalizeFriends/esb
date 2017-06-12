from __future__ import print_function
from esb import app, require_method, register_consumer

import zmq
import requests

@require_method('POST')
def fcm_message_queue(request):
    if request.json is None:
        raise Exception('JSON expected.')

    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect("tcp://localhost:5678")
    socket.send_json({
        'operation': 'send_fcm_message',
        'arguments': {
            'fcm_ids': request.json['fcm_ids'],
            'message': request.json['message']
        }
    })
    socket.close(100) # wait at most 100 ms to send message

@require_method('POST')
def fcm_message_statistics(request):
    requests.post('http://lfstats.ct8.pl/increment')

register_consumer('fcm_message', fcm_message_queue)
register_consumer('fcm_message', fcm_message_statistics)

if __name__ == '__main__':
    app.run()
