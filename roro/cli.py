from __future__ import print_function
import time
import itertools
import click
import datetime
import sys

from tabulate import tabulate
from . import config
from . import projects
from . import helpers as h
from .projects import Project
from . import auth
from .path import Path
from . import __version__
from .client import RoroClient

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
        except FireflyError as e:
            if e.args and e.args[0] == "Forbidden":
                click.echo("Unauthorized. Please login and try again.")
                sys.exit(2)
            else:
                click.echo('ERROR %s' % e)
                sys.exit(3)
        except Exception as exc:
            click.echo('ERROR %s' % exc)
            sys.exit(3)

@click.group(cls=CatchAllExceptions)
@click.version_option(version=__version__)
def cli():
    pass

@cli.command()
@click.option('--email', prompt='Email address')
@click.option('--password', prompt=True, hide_input=True)
def login(email, password):
    """Login to rorodata platform.
    """
    try:
        auth.login(email, password)
        click.echo("Login successful.")
    except ConnectionError:
        click.echo('unable to connect to the server, try again later')
    except FireflyError as e:
        click.echo(e)
        raise

@cli.command()
def version():
    """Prints the version of roro client."""
    cli.main(args=['--version'])

@cli.command()
def whoami():
    """prints the details of current user.
    """
    client = RoroClient(config.SERVER_URL)
    user = client.whoami()
    if user:
        click.echo(user['email'])
    else:
        click.echo("You are not logged in yet.")
        sys.exit(1)

@cli.command(name="projects")
def _projects():
    """Lists all the projects.
    """
    projects = Project.find_all()
    for p in projects:
        print(p.name)

@cli.command()
@click.argument('project')
@click.option('--repo-url', help="Initialize the project with a git repo", default=None)
def create(project, repo_url=None):
    """Creates a new Project.
    """
    p = Project(project)
    if repo_url:
        task = p.create(repo_url=repo_url)
        click.echo("Waiting for the project to get created...")
        response = task.wait()
        click.echo(response)
    else:
        p.create()
        click.echo("Created project:", project)

@cli.command(name="projects:delete")
@click.argument('name')
def project_delete(name):
    """Deletes a project
    """
    p = Project(name)
    p.delete()
    click.echo("Project {} deleted successfully.".format(name))

@cli.command()
def deploy():
    """Pushes the local changes to the cloud and restarts all the services.
    """
    # TODO: validate credentials
    project = projects.current_project()
    task = project.deploy(async=True)
    response = task.wait()
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

@cli.command(name="config")
def _config():
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
@click.option('-s', '--instance-size',
    help="size of the instance to run the job on")
@click.argument('command', nargs=-1)
def run(command, instance_size=None):
    """Runs the given script in foreground.
    """
    project = projects.current_project()
    job = project.run(command, instance_size=instance_size)
    print("Started new job", job["jobid"])

@cli.command(name='run:notebook', context_settings={"allow_interspersed_args": False})
@click.option('-s', '--instance-size',
    help="size of the instance to run the job on")
def run_notebook(instance_size=None):
    """Runs a notebook.
    """
    project = projects.current_project()
    job = project.run_notebook(instance_size=instance_size)
    _logs(project, job["jobid"], follow=True, end_marker="-" * 40)

@cli.command()
@click.argument('jobid')
def stop(jobid):
    """Stops a job by service name or job id.
    """
    project = projects.current_project()
    project.stop(jobid)

@cli.command()
@click.argument('service_name')
def start(service_name):
    """Starts the service specified by the given name.
    """
    project = projects.current_project()
    project.start_service(service_name)

@cli.command()
@click.argument('service_name')
def restart(service_name):
    """Restarts the service specified by the given name.
    """
    project = projects.current_project()
    project.restart_service(service_name)

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
    config.SERVER_URL = "http://api.local.rorodata.com:8080/"
    cli()
