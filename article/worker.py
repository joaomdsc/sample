# worker.py - un worker python pour X4B Scenario

"""Ce script contient la partie générique du code du worker python, avec la
gestion de la file d'attente des tâches, l'appel aux fonctions "métier" de
l'utilisateur, et la publication des status des tâches.

Le script importe un module utilisateur qui contient la partie spécifique du
code, avec l'implémentation des tâches "métier", l'idée étant de ré-utiliser à
chaque fois cette partie générique.

"""

import os
import sys
import json
import requests
from time import sleep
from datetime import datetime

#-------------------------------------------------------------------------------
# Configuration / environnement
#-------------------------------------------------------------------------------

# L'adresse cible (URL) du serveur X4B Scenario et la clé d'API qui fournit
# l'authentification et les autorisations pour les appels REST X4B sont
# attendues dans des variables d'environnement. Ce mécanisme permet de
# configurer facilement le worker, notamment lorsqu'il est exécuté dans un
# container docker.

# Adresse cible serveur (URL), par exemple https://scenario.xcomponent.com pour
# la plateforme en ligne Invivoo
if 'X4B_SCENARIO_SERVER' not in os.environ:
    raise RuntimeError('Missing X4B_SCENARIO_SERVER environment variable')
server_url = os.environ['X4B_SCENARIO_SERVER']

# Clé d'API pour les appels REST,  à récupérer depuis l'écran "Settings"
if 'X4B_APIKEY' not in os.environ:
    raise RuntimeError('Missing X4B_APIKEY environment variable')
apikey = os.environ['X4B_APIKEY']

#-------------------------------------------------------------------------------
# Paramètres globaux
#-------------------------------------------------------------------------------

# Définit le rythme d'interrogation de la file d'attente des tâches
polling_interval = 1 # en secondes

#-------------------------------------------------------------------------------
# APIs REST X4B Scenario
#-------------------------------------------------------------------------------

def publication_catalogue(postedCatalogTaskDefinitions, namespace,
        removePreviousTasks=None):
    """Publie un catalogue de tâches."""
    
    url = f'{server_url}/taskcatalog/api/catalog-task-definitions/{namespace}'
    query_params = dict(
        removePreviousTasks=removePreviousTasks,
    )
    headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'bearer {apikey}',
    }
    data = json.dumps(postedCatalogTaskDefinitions)
    r = requests.post(url, headers=headers, data=data, params=query_params)
    if r.status_code >= 400:
        raise RuntimeError(f'[{r.status_code}] {r.text}')

#-------------------------------------------------------------------------------

def tache_suivante(catalogTaskDefinitionNamespace,
        catalogTaskDefinitionName=None):
    """Récupère la prochaine tâche à exécuter."""
    
    url = f'{server_url}/polling/api/namespaces' \
      + f'/{catalogTaskDefinitionNamespace}/task-instances/poll'
    query_params = dict(
        catalogTaskDefinitionName=catalogTaskDefinitionName,
    )
    headers = {
        'Authorization': f'bearer {apikey}',
    }
    r = requests.post(url, headers=headers, params=query_params)
    if r.status_code >= 400:
        raise RuntimeError(f'[{r.status_code}] {r.text}')
    if r.status_code == 200:
        return r.json()

#-------------------------------------------------------------------------------

def maj_status(taskStatus):
    """Met à jour le statut d'une tâche."""

    url = f'{server_url}/taskstatus/api/task-statuses'
    headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'bearer {apikey}',
    }
    data = json.dumps(taskStatus)
    r = requests.post(url, headers=headers, data=data)
    if r.status_code >= 400:
        raise RuntimeError(f'[{r.status_code}] {r.text}')

#-------------------------------------------------------------------------------
# Worker code
#-------------------------------------------------------------------------------

def clean_dict(d):
    """Supprime certaines clés du dictionnaire fourni."""
    return {k: v for k, v in d.items() \
            if not (k.endswith('#type') or k.endswith('#subtype'))}

#-------------------------------------------------------------------------------

def post_task_status(task_instance_id, status, msg, outputs=None):
    """Publie le status d'une tâche.

    Le paramètre "status" peut prendre les valeurs 'InProgress', 'Error', ou
    'Completed'. Cette fonction envoie le status donné à X4B Scenario, où la
    tâche actuellement en cours d'exécution sera mise à jour, avec le status
    indiqué par la couleur de la pastille dna sle cockpit.

    """
    
    # Création de l'objet TaskStatus
    task_status = {
        'taskInstanceId':  task_instance_id,
        'status': status,
        'message': msg,
        'outputValues': outputs,
    }
    
    # Publication du status
    try:
        maj_status(task_status)
    except RuntimeError as e:
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'{dt} worker: échec de la publication du status')
        print(e)
        return

    # Return the data in case we want to use it or print it
    return task_status

#-------------------------------------------------------------------------------

class Notification():
    """Notification object.

    This object implements a communication mechanism to allow the python
    code that implements a task to send notifications to XC Scenario. An
    instance of this class is passed to each user function, so that the
    function can invoke the "notify" method.
    """
    
    def __init__(self, task_instance_id, module_name):
        self.task_instance_id = task_instance_id
        self.module_name = module_name
        self.isError = False

    def notify(self, status, msg, outputs=None, progressPercentage=None):
        """Send a task status to XC Scenario.
        
        The given message will be displayed by XC Scenario in the 
        "Message" section of the task's screen in the cockpit.
        """

        self.isError = (status == 'Error')
        
        task_status = post_task_status(self.task_instance_id, status, msg, outputs=outputs)
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'{dt} worker: task status (notification) posted')
        print(json.dumps(task_status, indent=4))

#-------------------------------------------------------------------------------
# work - periodically poll the task queue, retrieve tasks, do the actual work 
#-------------------------------------------------------------------------------

def do_work(mod, namespace, autocomplete=True):
    """Periodically poll the task queue, retrieve tasks, do the actual work.

    This is the heart of the worker's logic. The code extracts tasks
    from the task queue, and calls the corresponding function from the
    user module (if found). If the user function raises an exception,
    the code will notify XC Scenario by posting an 'InError' status; if
    it completes normally, without errors, and if the autocomplete flag
    is activated, the worker code will post the 'Completed' status.
"""
    
    while True:
        # Récupère dans la file d'attente la prochaine tâche à exécuter.
        # L'instance de tâche que l'on récupère ici inclut le nom de la
        # fonction à exécuter ainsi que les valeurs des paramètres d'entrée.
        ti = tache_suivante(namespace)
            
        # When the queue is empty, there's no exception raised, 'ti' is None
        if ti is None:
            dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f'{dt} worker[{namespace}]: task queue is empty')
            sleep(polling_interval)
            continue

        # Get the task for execution from the user's module
        task_name = ti['catalogTaskDefinitionName']
        if task_name not in mod.__dict__:
            # This is a mismatch between the published catalog, used to create
            # a scenario definition, and the python module that's supposed to
            # implement the task. The catalog has advertised a task, but it
            # can't be found in the module. Log the error.
            print('-'*60)
            dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            namespace = ti['catalogTaskDefinitionNamespace']
            msg = f'{dt} worker[{namespace}]: unknown task: {namespace}/{task_name}'
            print(msg)

            # From the XC Scenario point of view, the task that we just
            # extracted from the task queue needs to be flagged as 'Error',
            # since we couldn't execute it.
            post_task_status(ti['id'], 'Error', msg)
                
            # Back to the loop
            sleep(polling_interval)
            continue

        # We found the task code, log it.
        print('-'*60)
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'{dt} worker[{namespace}]: calling task "{task_name}"')
        print(json.dumps(ti, indent=4))

        # Remove "#type" from the input data
        inputs = clean_dict(ti['inputData'])

        # Prepare the notification mechanism, so that user functions can call
        # notifier.notify() if needed.
        notifier = Notification(ti['id'], mod.__name__)
        
        # Invoke the task_name function from the user module (use module name),
        # pass the input data, and retrieve a dictionary of output data
        # (outputValues)
        excep = None
        try:
            outputValues = mod.__dict__[task_name](notifier, **inputs)
        except Exception as e:
            excep = e
        
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'{dt} worker[{namespace}]: task {task_name} returned')

        # Si une exception a été levée dans le code utilisateur, on publie un
        # statut d'erreur dans X4B Scenario
        if excep is not None:
            print(excep)
            msg = 'Exception levée par la tâche utilisateur'
            post_task_status(ti['id'], 'Error', msg)
            
        # Notify 'Completed' state only if we have autocomplete enabled
        if excep is None and not notifier.isError and autocomplete:
            post_task_status(ti['id'], 'Completed', '', outputs=outputValues)

        # Temps d'attente avant de ré-interroger la file des tâches
        sleep(polling_interval) 

#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    # Check cmd line args
    if len(sys.argv) not in [2, 3]:
        print(f"""\
Usage: {sys.argv[0]} <namespace> [ <autocomplete true/false> ]

This code assumes there's a python module, with the same name as the namespace,
that can be found through python's standard import mechanisms, such as the
PYTHONPATH variable.""")
        exit(-1)

    # The worker will publish 'Completed' status for every task that finishes
    # normally (without having thrown any exceptions), unless explicitly
    # requested here with autocomplete == 'false'
    autocomplete = True
    if len(sys.argv) == 3:
        s = sys.argv[2].lower()
        if s not in ['true', 'false']:
            print(f'"{sys.argv[2]}" unrecognized boolean value')
            exit(-1)
        autocomplete = (s != 'false')

    # The namespace is also the user module name
    namespace = sys.argv[1]

    # Get the user module and publish its catalog
    mod = __import__(namespace)
    publication_catalogue(mod.task_definitions(), namespace)

    # Poll the task queue and call execution functions
    do_work(mod, namespace, autocomplete=autocomplete)

# End of worker.py
#-------------------------------------------------------------------------------
