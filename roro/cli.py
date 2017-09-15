from __future__ import print_function
import os
import stat
import time
import itertools
import click
import datetime
import sys

from netrc import netrc
from tabulate import tabulate
from . import projects
from . import helpers as h
from .helpers import get_host_name, PY2
from .projects import Project, login as roro_login
from .path import Path

from firefly.client import FireflyError
from requests import ConnectionError

class PathType(click.ParamType):
    name = 'path'

    def convert(self, value, param, ctx):
        return Path(value)

class CatchAllExceptions(click.Group):
    def __call__(self, *args, **kwargs):
        try:
            return self.main(*args, **kwargs)
        except Exception as exc:
            click.echo('ERROR %s' % exc)

@click.group(cls=CatchAllExceptions)
def cli():
    pass

@cli.command()
@click.option('--email', prompt='Email address')
@click.option('--password', prompt=True, hide_input=True)
def login(email, password):
    """Login to rorodata platform.
    """
    netrc_file = create_netrc_if_not_exists()
    try:
        token = roro_login(email, password)
        rc = netrc()
        _fix_netrc(rc)
        with open(netrc_file, 'w') as f:
            host_name = get_host_name(projects.SERVER_URL)
            if PY2:
                email = email.encode('utf-8')
                token = token.encode('utf-8')
            rc.hosts[host_name] = (email, None, token)
            f.write(str(rc))
    except ConnectionError:
        click.echo('unable to connect to the server, try again later')
    except FireflyError as e:
        click.echo(e)

# this is here because of this issue
# https://github.com/python/cpython/pull/2491
# TODO: should be removed once it is fixed
def _fix_netrc(rc):
    for host in rc.hosts:
        login, _, password = rc.hosts[host]
        # should be safe as we use alphanumneric chars in token
        login = login.strip("'")
        password = password.strip("'")
        rc.hosts[host] = (login, _, password)

def create_netrc_if_not_exists():
    prefix = '.' if os.name != 'nt' else '_'
    netrc_file = os.path.join(os.path.expanduser('~'), prefix+'netrc')
    # theese flags works both on windows and linux according to this stackoverflow
    # https://stackoverflow.com/questions/27500067/chmod-issue-to-change-file-permission-using-python#27500153
    if not os.path.exists(netrc_file):
        with open(netrc_file, 'w'):
            pass
        os.chmod(netrc_file, stat.S_IREAD|stat.S_IWRITE)
    return netrc_file

@cli.command(name="projects")
def _projects():
    """Lists all the projects.
    """
    projects = Project.find_all()
    for p in projects:
        print(p.name)

@cli.command()
@click.argument('project')
def create(project):
    """Creates a new Project.
    """
    p = Project(project)
    p.create()
    print("Created project:", project)

@cli.command()
def deploy():
    """Pushes the local changes to the cloud and restarts all the services.
    """
    # TODO: validate credentials
    project = projects.current_project()
    response = project.deploy()
    click.echo(response)

@cli.command()
@click.argument('src', type=PathType())
@click.argument('dest', type=PathType())
def cp(src, dest):
    """Copy files to and from volumes to you local disk.

    Example:

        $ roro cp volume:/dataset.txt ./dataset.txt

        downloads the file dataset.txt from the server

        $ roro cp ./dataset.txt volume:/dataset.txt

        uploads dataset.txt to the server
    """
    if src.is_volume() is dest.is_volume():
        raise Exception('One of the arguments has to be a volume, other a local path')
    project = projects.current_project()
    project.copy(src, dest)

@cli.command()
@click.option('-a', '--all', default=False, is_flag=True)
def ps(all):
    """Shows all the processes running in this project.
    """
    project = projects.current_project()
    jobs = project.ps(all=all)
    rows = []
    for job in jobs:
        start = h.parse_time(job['start_time'])
        end = h.parse_time(job['end_time'])
        total_time = (end - start)
        total_time = datetime.timedelta(total_time.days, total_time.seconds)
        command = " ".join(job["details"]["command"])
        rows.append([job['jobid'], job['status'], h.datestr(start), str(total_time), job['instance_type'], h.truncate(command, 50)])
    print(tabulate(rows, headers=['JOBID', 'STATUS', 'WHEN', 'TIME', 'INSTANCE TYPE', 'CMD'], disable_numparse=True))

@cli.command(name='ps:restart')
@click.argument('name')
def ps_restart(name):
    """Restarts the service specified by name.
    """
    pass

@cli.command()
def config():
    """Lists all config vars of this project.
    """
    project = projects.current_project()
    config = project.get_config()
    print("=== {} Config Vars".format(project.name))
    for k, v in config.items():
        print("{}: {}".format(k, v))

@cli.command(name='config:set')
@click.argument('vars', nargs=-1)
def env_set(vars):
    """Sets one or more the config vars.
    """
    project = projects.current_project()

    d = {}
    for var in vars:
        if "=" in var:
            k, v = var.split("=", 1)
            d[k] = v
        else:
            d[var] = ""

    project.set_config(d)
    print("Updated config vars")

@cli.command(name='config:unset')
@click.argument('names', nargs=-1)
def env_unset(names):
    """Unsets one or more config vars.
    """
    project = projects.current_project()
    project.unset_config(names)
    print("Updated config vars")

@cli.command(context_settings={"allow_interspersed_args": False})
@click.argument('command', nargs=-1)
def run(command):
    """Runs the given script in foreground.
    """
    project = projects.current_project()
    job = project.run(command)
    print("Started new job", job["jobid"])

@cli.command(name='run:notebook', context_settings={"allow_interspersed_args": False})
def run_notebook():
    """Runs a notebook.
    """
    project = projects.current_project()
    job = project.run_notebook()
    _logs(project, job["jobid"], follow=True, end_marker="-" * 40)

@cli.command()
@click.argument('jobid')
def stop(jobid):
    """Stops a service with reference to jobid
    """
    project = projects.current_project()
    project.stop(jobid)

@cli.command()
@click.argument('jobid')
@click.option('-s', '--show-timestamp', default=False, is_flag=True)
@click.option('-f', '--follow', default=False, is_flag=True)
def logs(jobid, show_timestamp, follow):
    """Shows all the logs of the project.
    """
    project = projects.current_project()
    _logs(project, jobid, follow, show_timestamp)

def _logs(project, job_id, follow=False, show_timestamp=False, end_marker=None):
    """Shows the logs of job_id.
    """
    def get_logs(job_id, follow=False):
        if follow:
            seen = 0
            while True:
                logs = project.logs(job_id)
                for log in logs[seen:]:
                    yield log
                seen = len(logs)
                job = project.ps(job_id)
                if job['status'] in ['success', 'cancelled', 'failed']:
                    break
                time.sleep(0.5)
        else:
            logs = project.logs(job_id)
            for log in logs:
                yield log


    logs = get_logs(job_id, follow)
    if end_marker:
        logs = itertools.takewhile(lambda log: not log['message'].startswith(end_marker), logs)

    _display_logs(logs, show_timestamp=show_timestamp)

def _display_logs(logs, show_timestamp=False):
    def parse_time(timestamp):
        t = datetime.datetime.fromtimestamp(timestamp//1000)
        return t.isoformat()

    if show_timestamp:
        log_pattern = "[{timestamp}] {message}"
    else:
        log_pattern = "{message}"

    for line in logs:
        line['timestamp'] = parse_time(line['timestamp'])
        click.echo(log_pattern.format(**line))

@cli.command()
@click.argument('project')
def project_logs(project):
    """Shows all the logs of the process with name <project> the project.
    """
    pass

@cli.command()
def volumes():
    """Lists all the volumes.
    """
    project = projects.current_project()
    volumes = project.list_volumes()
    if not volumes:
        click.echo('No volumes are attached to {}'.format(project.name))
    for volume in  project.list_volumes():
        click.echo(volume)

@cli.command(name='volumes:add')
@click.argument('volume_name')
def create_volume(volume_name):
    """Creates a new volume.
    """
    project = projects.current_project()
    volume = project.add_volume(volume_name)
    click.echo('Volume {} added to the project {}'.format(volume, project.name))

@cli.command(name='volumes:remove')
@click.argument('volume_name')
def remove_volume(volume_name):
    """Removes a new volume.
    """
    pass

@cli.command(name='volumes:ls')
@click.argument('path')
def ls_volume(path):
    """Lists you files in a volume.

    Example:

        \b
        roro volume:ls <volume_name>
        lists all files in volume "volume_name"

        \b
        roro volume:ls <volume_name:dir>
        lists all filies at directory "dir" in volume "volume"
    """
    path = path+':' if ':' not in path else path
    path = Path(path)
    project = projects.current_project()
    stat = project.ls(path)
    rows = [[item['mode'], item['size'], item['name']] for item in stat]
    click.echo(tabulate(rows, tablefmt='plain'))

@cli.command()
def models():
    project = projects.current_project()
    for repo in project.list_model_repositories():
        print(repo.name)

@cli.command(name="models:log")
@click.argument('name', required=False)
@click.option('-a', '--all', default=False, is_flag=True, help="Show all fields")
def models_log(name=None, all=False):
    project = projects.current_project()
    images = project.get_model_activity(repo=name)
    for im in images:
        if all:
            print(im)
        else:
            print(im.get_summary())

@cli.command(name="models:show")
@click.argument('modelref')
def models_show(modelref):
    project = projects.current_project()

    model = modelref
    tag = None
    version = None

    if ":" in modelref:
        model, version_or_tag = modelref.split(":", 1)
        if version_or_tag.isnumeric():
            version = int(version_or_tag)
        else:
            tag = version_or_tag

    repo = project.get_model_repository(model)
    image = repo and repo.get_model_image(version=version, tag=tag)
    if not image:
        click.echo("Invalid model reference {!r}".format(model))
        sys.exit(1)

    print(image)

def main_dev():
    projects.SERVER_URL = "http://api.local.rorodata.com:8080/"
    cli()
