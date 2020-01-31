import time
from datetime import datetime
import asyncio
import logging
import concurrent.futures
import stomp

import listeners


fmt = "%(asctime)s %(message)s"
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='asyncserver.log', mode='a', encoding='utf-8', delay=False)
handler.setFormatter(logging.Formatter(fmt))
logger.addHandler(handler)


def execute_listener(event, **kwargs):
    logger.debug(event)
    logger.debug(kwargs)
    func = getattr(listeners, event, None)
    if func:
        logger.debug(str(func))
        func(**kwargs)
    else:
        logger.error(f"{event} listener not defined.")


def connect_and_subscribe(conn, retry=3):
    for i in range(retry):
        try:
            time.sleep(10.0)
            conn.connect('admin', 'password', wait=True)
            break
        except Exception:
            pass
    conn.subscribe(destination='/queue/testqueue', id=1)


class MyListener(stomp.ConnectionListener):
    def __init__(self, conn, queue):
        self.conn = conn
        self.queue = queue

    def on_error(self, headers, message):
        logger.debug('received an error "%s"' % message)

    def on_message(self, headers, message):
        logger.debug('received a message "%s"' % headers)
        queuename = headers.get('destination')[len('/queue/'):]
        self.queue.put_nowait([queuename, dict(message=message)])

    def on_disconnected(self):
        connect_and_subscribe(self.conn)


future_list = []
async def main():
    queue = asyncio.Queue()
    conn = stomp.Connection([('activemq', 61613)])
    conn.set_listener('', MyListener(conn, queue))
    connect_and_subscribe(conn)

    with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executer:
        while True:
            if not queue.empty():
                queuedata = await queue.get()
                logger.debug("queue count -> {}".format(queue.qsize()))
                if queuedata[0] == 'stop':
                    logger.debug("Stop Listener")
                    break
                future = executer.submit(fn=execute_listener, event=queuedata[0], **queuedata[1])
                future_list.append(future)
                concurrent.futures.as_completed(future_list)
            else:
                await asyncio.sleep(10.0)
    conn.disconnect()


if __name__ == '__main__':
    logger.debug("main start")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
