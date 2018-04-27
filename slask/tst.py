from time import sleep

import connexion



def greeting(name: str):
    greeting.cnt += 1
    return 'Hello {name} {cnt}\n'.format(name=name, cnt=greeting.cnt)
greeting.cnt=0

def slow(name: str):
    sleep(10)
    return greeting(name)

if __name__ == '__main__':
    app = connexion.App(__name__, port=8000)
    app.add_api('tst.yaml', arguments={'title': 'Hello World Example'})
    app.run()
