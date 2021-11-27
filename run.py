import subprocess
from database.db_init import MySQLInit


if __name__ == '__main__':
    # MySQLInit()
    servers = [
        # ["pipenv", "run", "python", "url_server.py"],
        # ["pipenv", "run", "python", "url_client_manual.py"],
        ["pipenv", "run", "python", "scheduled_task.py"],
        # ["pipenv", "run", "gunicorn", "-c", "hproxy/config/gunicorn.py", "--worker-class", "sanic.worker.GunicornWorker", 'hproxy.server:app'],
    ]

    procs = []

    for server in servers:
        print('run.py执行for server in servers： %s' % server)
        proc = subprocess.Popen(server)
        procs.append(proc)

    for proc in procs:
        proc.wait()
        print('run.py执行for proc in procs： %s' % proc)
        if proc.poll():
            exit(0)
