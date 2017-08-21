import click

@click.group()
def cli():
    pass

@cli.command()
@click.option('--email', prompt='your email address')
@click.option('--password', prompt=True, hide_input=True)
def login(email, password):
    """Login to rorodata platform.
    """
    pass

@cli.command()
@click.argument('project')
def create(project):
    """Creates a new Project.
    """
    pass

@cli.command()
def deploy():
    """Pushes the local changes to the cloud and restarts all the services.
    """
    pass

@cli.command()
def ps():
    """Shows all the processes running in this project.
    """
    pass

@cli.command(name='ps:restart')
@click.argument('name')
def ps_restart(name):
    """Restarts the service specified by name.
    """
    pass

@cli.command()
def env():
    """Lists all environment variables associated with this project.
    """
    pass

@cli.command(name='env:set')
@click.argument('name')
@click.argument('value')
def env_set(name, value):
    """Lists all environment variables associated with this project.
    """
    pass

@cli.command(name='env:unset')
@click.argument('name')
@click.argument('value')
def env_unset(name, value):
    """Unsets an environment variable.
    """
    pass

@cli.command()
@click.argument('name')
def run(script):
    """Runs the given script in foreground.
    """
    pass

@cli.command(name='run:notebook')
def run_notebooke():
    """Runs a notebook.
    """
    pass

@cli.command()
def logs():
    """Shows all the logs of the project.
    """
    pass

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
    pass

@cli.command(name='volumes:new')
@click.argument('volume_name')
def create_volume(volume_name):
    """Creates a new volume.
    """
    pass

@cli.command(name='volumes:remove')
@click.argument('volume_name')
def remove_volume(volume_name):
    """Removes a new volume.
    """
    pass
