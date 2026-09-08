import json
from wsgiref import simple_server

# Función principal encargada de procesar cada petición.
def main_app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'application/json')])
    return [bytes(json.dumps('Hello, World!'), 'utf-8')]

# Levantamos el servidor y lo dejamos escuchando en el puerto 9292 hasta que se interrumpa la ejecución del programa.
if __name__ == '__main__':
    server = simple_server.make_server('', 9292, main_app)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
