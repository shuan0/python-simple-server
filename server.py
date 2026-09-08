import json
from wsgiref import simple_server

# Listado de tareas que será mostrado y modificado con las peticiones.
tasks = {}

# Contador histórico de tareas creadas. Servirá principalmente para asignar un identificador único a cada tarea y así facilitar su búsqueda en el listado.
task_counter = 0

# Función encargada de obtener la información de una tarea. En caso de no especificar una, devuelve la información del listado completo.
def get_tasks(args):
    # Si no se especificó el ID de una tarea, devolvemos el listado completo de tareas.
    if len(args) < 2:
        return ['200 OK', tasks.values()]

    # En caso de que se haya especificado el ID de una tarea, ésta se busca en el listado.
    task = tasks.get(args[1])

    # Si la tarea no existe, respondemos con error 404.
    if task is None:
        return ['404 Not Found', 'task not found']

    # Devolvemos la tarea especificada en caso de existir.
    return ['200 OK', task]

# Función encargada de crear una tarea con la información brindada en el cuerpo de la petición.
def create_task(args, body):
    global task_counter

    # Incrementamos el contador de tareas creadas y luego lo utilizamos para asignarle un identificador a la nueva tarea.
    task_counter += 1
    tasks[task_counter] = {
        'title': body['title'],
        'done': body['done'],
    }

    return ['201 Created', 'task created']

# Listado de controladores para cada verbo.
routes = {
    'GET': {
        'controller': get_tasks,
        'min_args': 0,
        'max_args': 1,
    },
    'POST': {
        'controller': create_task,
        'min_args': 0,
        'max_args': 0,
    },
}

# Función principal encargada de validar cada petición para derivarla al controlador que corresponda.
def main_app(environ, start_response):
    # El campo "REQUEST_METHOD" contiene el verbo de la petición (GET, POST, PATCH o DELETE).
    method = str(environ['REQUEST_METHOD'])

    # Validamos que el verbo exista y recuperamos la información de su controlador correspondiente. En caso de no existir, respondemos con error 405.
    query_info = routes.get(method)
    if query_info is None:
        start_response('405 Method Not Allowed', [('Content-Type', 'application/json')])
        return [b'method not allowed']

    # El campo "PATH_INFO" contiene la información de la ruta a la que se está disparando la petición.
    path_args = str(environ['PATH_INFO']).removeprefix('/').split('/')
    total_args = len(path_args) - 1

    # Validamos que la ruta exista, en caso contrario, respondemos con error 404.
    if total_args < query_info['min_args'] or total_args > query_info['max_args'] or path_args[0] != 'tasks':
        start_response('404 Not Found', [('Content-Type', 'application/json')])
        return [b'route not found']

    controller = query_info['controller']

    # En caso de que el verbo sea POST o PATCH, recuperamos la información contenida por el cuerpo de la petición para pasársela al controlador.
    if method in ['POST', 'PATCH']:
        body = environ['wsgi.input'].read(int(environ['CONTENT_LENGTH']))
        body_data = json.loads(body.decode('utf-8'))
        query_result = controller(path_args, body_data)
    else:
        query_result = controller(path_args)

    # Luego de que el controlador haya procesado la petición, respondemos al cliente con el resultado final.
    start_response(query_result[0], [('Content-Type', 'application/json')])
    return [bytes(json.dumps(query_result[1]), 'utf-8')]

# Levantamos el servidor y lo dejamos escuchando en el puerto 9292 hasta que se interrumpa la ejecución del programa.
if __name__ == '__main__':
    server = simple_server.make_server('', 9292, main_app)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
