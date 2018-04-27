from time import sleep

import connexion



if __name__ == '__main__':
    app = connexion.App(__name__, port=8000)
    app.add_api('swagger.yaml')
    app.run()

