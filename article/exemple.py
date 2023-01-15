# exemple.py - un exemple de module utilisateur pour le worker Scenario

from time import sleep
    
#-------------------------------------------------------------------------------
# Fonctions de traitement
#-------------------------------------------------------------------------------

# Cette partie du module contient les fonctions métier qui sont à mises à
# disposition du concepteur de scenarios, pour être appelées par le worker.

def simple(x4b, arg):
    """Une fonction qui renvoiement simplement son argument."""
    print(f'[{__name__}] sbimple: arg={arg}')

    # Début traitement spécifique
    # Fin traitement spécifique
    
    msg = f'The argument received was "{arg}".'
    return {'msg': msg}

#-------------------------------------------------------------------------------

def double(x4b, str_in, nbr_in):
    """Une fonction qui illustre ."""
    print(f'[{__name__}] double: entrées: str_in={str_in}, nbr_in={nbr_in}')

    # Début traitement spécifique
    str_out = str_in + str_in
    try:
        nbr_out = str(2*int(nbr_in))
    except ValueError:
            msg = f"Incorrect value '{nbr_in}' for nbr_in, should be integer"
            x4b.notifie('Error', msg)
            return {}
    # Fin traitement spécifique

    return {'str_out': str_out, 'nbr_out': nbr_out}

#-------------------------------------------------------------------------------

def reporting_task(x4b, n, param):
    """A long-running task that periodically reports its progress."""
    print(f'[{__name__}] reporting_task: n={n}, param={param}')

    # Numeric parameters should always be tested
    try:
        n = int(n)
    except ValueError:
        msg = f'Incorrect value "{n}" for n, should be integer'
        x4b.notifie('Error', msg)
        return {}
    
    msg = f'Input "{param}": going to sleep for {n} seconds.'
    x4b.notifie('InProgress', msg, progressPercentage=str(0.0))

    for i in range(n):
        sleep(1)
        x4b.notifie('InProgress', str(i+1), progressPercentage=str((i+1)/n))

    msg = f'Waking up.'
    x4b.notifie('InProgress', msg)
    return {'result': f'Input "{param}", result is ok'}

#-------------------------------------------------------------------------------

def error_placeholder(x4b):
    """Send an error status"""
    print(f'[{__name__}] error_placeholder: FATAL error')
    msg = 'Task "error_placeholder" reports a fatal error.'
    x4b.notifie('Error', msg)
    return {}

#-------------------------------------------------------------------------------

def zero_division(x4b):
    """Force a python exception"""
    print(f'[{__name__}] zero_division: force a division by zero')
    return {'x': 1/0}

#-------------------------------------------------------------------------------
# Définition de tâches pour le catalogue
#-------------------------------------------------------------------------------

def task_definitions():
    """Return the array of XC Scenario task definition objects.
    
    This array must have one element for each task, i.e. for each function
    implemented in the Task implementations section above. Each element is a
    python version of the CatalogTaskDefinition JSON object defined in the REST
    API definition, see
    https://scenario.xcomponent.com/taskcatalog/swagger/ui/index, POST
    /api/catalog-task-definitions/{namespace} operation.

    """

    task_defs = []

    #---------------------------------------------------------------------------

    # simple - a simple task that echoes its input argument
    task = {
        'namespace': __name__,
        'name': 'simple',
    }
    task['inputs'] = [
        {
            'name': 'arg',
            'baseType': 'String',
        },
    ]
    task['outputs'] = [
        {
            'name': 'msg',
            'baseType': 'String',
        },
    ]
    task_defs.append(task)

    #---------------------------------------------------------------------------

    # double - immediate task
    task = {
        'namespace': __name__,
        'name': 'double',
    }
    task['inputs'] = [
        {
            'name': 'str_in',
            'baseType': 'String',
            'defaultValue': 'xyz (default)',
        },
        {
            'name': 'nbr_in',
            'baseType': 'Number',
            'defaultValue': '123',
        },
    ]
    task['outputs'] = [
        {
            'name': 'str_out',
            'baseType': 'String',
        },
        {
            'name': 'nbr_out',
            'baseType': 'Number',
        },
    ]
    task_defs.append(task)

    #---------------------------------------------------------------------------

    # reporting_task - a long-running task that reports its progress
    task = {
        'namespace': __name__,
        'name': 'reporting_task',
    }
    task['inputs'] = [
        {
            'name': 'n',
            'baseType': 'String',
        },
        {
            'name': 'param',
            'baseType': 'String',
        },
    ]
    task['outputs'] = [
        {
            'name': 'result',
            'baseType': 'String',
        },
    ]
    task_defs.append(task)

    #---------------------------------------------------------------------------

    # error_placeholder - force an error status
    task = {
        'namespace': __name__,
        'name': 'error_placeholder',
    }
    task_defs.append(task)

    #---------------------------------------------------------------------------

    # zero_division - force a python exception
    task = {
        'namespace': __name__,
        'name': 'zero_division',
    }
    task_defs.append(task)


    #---------------------------------------------------------------------------

    # Return the array of task definitions
    return task_defs

#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    print("Ce module n'a pas vocation à être exécuté directement.")
