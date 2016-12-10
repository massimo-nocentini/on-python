
import socket
from contextlib import suppress
from selectors import DefaultSelector, EVENT_WRITE

selector = DefaultSelector()

sock = socket.socket()
sock.setblocking(False)

def connected_eventhandler():
    selector.unregister(sock.fileno())
    print('connected')

# we want to know when the socket is "writable"
selector.register(sock.fileno(), EVENT_WRITE, connected_eventhandler) 

with suppress(BlockingIOError):
    sock.connect(('xkcd.com', 80))

def loop():
    while True:
        # Unlike in our fast-spinning loop above, the call to `select` 
        # here pauses, awaiting the next I/O events. 
        events = selector.select()
        for event_key, event_mask in events:
            callback = event_key.data
            callback()

# An async framework builds on the two features we have shown:
# non-blocking sockets and the event loop, to run concurrent operations on a single thread.

with suppress(KeyboardInterrupt):
    loop()
