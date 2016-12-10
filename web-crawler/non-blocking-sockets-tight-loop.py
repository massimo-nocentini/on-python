
import socket
from contextlib import suppress

sock = socket.socket()
sock.setblocking(False)

# `BlockingIOError` exception replicates the irritating behavior of the underlying C function, 
# which sets errno to EINPROGRESS to tell you it has begun.
with suppress(BlockingIOError):
    sock.connect(('xkcd.com', 80))

url='/'
request = 'GET {} HTTP/1.0\r\nHost: xkcd.com\r\n\r\n'.format(url)
encoded = request.encode('ascii')

# we needs a way to know when the connection is established, 
# simply keep trying in a tight loop:
while True:
    with suppress(OSError):
        sock.send(encoded)
        break  # Done.

print('sent')

# This method not only wastes electricity, but it cannot efficiently 
# await events on multiple sockets, since we're required to use *one* thread.
