# psax.py

from subprocess import run

r = run(['ps', 'ax'], stdout=PIPE, stderr=STDOUT)
if r.returncode != 0:
    print(f'ps returned: {r.returncode}')
print(r.stdout)
