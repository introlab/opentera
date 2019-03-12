import redis
import time

class User:
    def __init__(self):
        self.name = 'name'
        self.password = 'password'

    def __str__(self):
        return self.name + ':' + self.password


if __name__ == '__main__':
    print('Hello World!')
    r = redis.Redis(host='localhost', port=6379, db=0)

    p = r.pubsub()
    p.subscribe('mypub')

    r.publish('mypub', 'HELLO')

    while True:
        message = p.get_message()
        if message:
            print(message, message['data'])

        time.sleep(1)


