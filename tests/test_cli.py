import responses

from roro import cli
from roro import projects
from roro.cli import create_netrc_if_not_exists
from netrc import netrc

from click.testing import CliRunner

runner = CliRunner()
projects.SERVER_URL = 'https://127.0.0.1:8080'

def mock_get_root():
    responses.add(
        responses.GET, projects.SERVER_URL,
        json={}, status=200
    )

def setup_function(function):
    create_netrc_if_not_exists()

def teardown_function(function):
    netrc_file = create_netrc_if_not_exists()
    rc = netrc()
    cli._fix_netrc(rc)
    if rc.hosts.get(projects.SERVER_URL):
        rc.hosts.pop(projects.SERVER_URL)
    with open(netrc_file, 'w') as f:
        f.write(str(rc))

@responses.activate
def test_login():
    mock_get_root()
    responses.add(
        responses.POST, projects.SERVER_URL+'/login',
        json='auth_token', status=200
    )
    runner.invoke(cli.login, input='user@test.com\ntest\n')
    # check wether the netrc file has user@test.com
    rc = netrc()
    # this assert is a little off because of the issue mentioned
    # in roro/cli.py#44
    assert rc.hosts[projects.SERVER_URL] == (
        "'user@test.com'", None, "'auth_token'"
    )


@responses.activate
def test_bad_login():
    mock_get_root()
    error_message = {"error": "InvalidCredentials: Please check your credentials"}
    responses.add(
        responses.POST, projects.SERVER_URL+'/login',
        json=error_message, status=500
    )
    runner.invoke(cli.login, input='bad_user@test.com\ntest\n')
    rc = netrc()
    assert rc.hosts.get(projects.SERVER_URL) is None

@responses.activate
def test_deploy():
    mock_get_root()
    responses.add(
        responses.POST, projects.SERVER_URL+'/deploy',
        json='your project has bee deployed', status=200
    )
    result = runner.invoke(cli.deploy)
    assert result.output == 'your project has bee deployed\n'

@responses.activate
def test_bad_deploy():
    mock_get_root()
    responses.add(
        responses.POST, projects.SERVER_URL+'/deploy',
        json={'error': 'Failed to build docker image'}, status=500
    )
    result = runner.invoke(cli.deploy)
    print(result.exception.args)
    assert result.exception.args == ('Failed to build docker image',)
