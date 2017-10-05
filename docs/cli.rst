The Rorodata CLI
================

The primary interface to the rorodata platform is the command-line interface. 

The command-line client can be installed using::

	pip install roro-client

Make sure you have at least version 0.1.6 of the client. ::

	$ roro version
	roro, version 0.1.6

Once installed, make sure you log in to the platform using::

	$ roro login
	Email address: anand@rorodata.com
	Password:
	Login successful.

It is prompt for your email and password. If you don't already have an account, please sign up at http://www.rorodata.com/.

Most of the commands work in the context of a project and they must be executed from the project directory. These commands look at the ``roro.yml`` file to find the project name.

Projects
--------

The list of projects can be found using the ``roro projects`` command. ::

	$ roro projects
	hello-world
	credit-risk

New project can be created using::

	$ roro create my-new-project
	Created project: my-new-project

The project name is unique across the platform and a project name once used by any user can not be used by anyone else.

Support for deleting a project is in progress and will be available in future versions.

Deploy
------

The `roro deploy` command is used to deploy a project. Deploy is the only way to send any changes in the project to the platform, including code changes, changes to roro.yml to add/delete more services/periodic tasks. 

While deploy is just a single command, lot of things happen behind the scenes.

* all the files in the project directory are archived and send to the platform 
* A docker image is created with the specified runtime as base image and all the dependencies in the ``requirements.txt`` file installed, if present
* All the services specified in the ``roro.yml`` are (re)started and end points are created
* The scheduled tasks are updated

The deploy command prints the summary of changes and end points for each service in the project.

	$ roro deploy
	Deploying project credit-risk. This may take a few moments ...
	Building docker image... done.
	Updating scheduled jobs... done.
	Restarted one service.
	  default: https://credit-risk.rorocloud.io/

	Deployed version 5 of credit-risk project.

Scripts & Notebooks
-------------------

The ``roro run`` command is used to run any script, typically a python program in the rorodata platform. ::

	$ roro run python train.py
	Started new job 4fa27081

That starts a new job and that runs on the platform. You can look at the logs of the job using the ``roro logs`` command, which contains the all logs printed by the script.::

	$ roro logs 4fa27081
	starting the job
	training decision tree model...
	training complete.
	the model is saved to /volumes/data/model.pkl

Please remember that it uses the code that is last deployed. If you have any changes to the code that you want to run, you need to deploy before running the script.

Notebooks can be run using the ``roro run:notebook`` command. ::

	$ roro run:notebook
	starting the job
	Jupyter notebook is available at:
	https://517832f3.rorocloud.io/?token=rorocloud

	The jupyter notebook server can be stopped using:
	    roro stop 517832f3

It starts a new notebook in the project's software environment created using the previous deploy and provides a URL endpoint to access it.

Please remember that the notebook server continues to run until it is stopped.

Processes & Logs
----------------

The list of processes currently running in a project can be found using the ``roro ps`` command. ::

	$ roro ps
	JOBID     STATUS    WHEN           TIME     INSTANCE TYPE    CMD
	--------  --------  -------------  -------  ---------------  -------------------
	c19f745b  running   7 seconds ago  0:00:07  C1               python train.py
	137f3d2a  running   9 seconds ago  0:00:07  C1               [notebook]

A process can be stopped using ``roro stop`` command. ::

	$ roro stop 137f3d2a

The logs of any process can be seen using the ``roro logs`` command. ::

	$ roro logs c19f745b
	started training
	iteration 100 - accuracy 0.57
	iteration 200 - accuracy 0.65
	iteration 300 - accuracy 0.68
	iteration 400 - accuracy 0.69

The ``roro ps``	command shows only the active processes. To see all processes ever run in the project, call with ``-a`` flag. ::

	JOBID     STATUS    WHEN           TIME     INSTANCE TYPE  CMD
	--------  --------  -------------  -------  -------------  ---------------
	c19f745b  running   7 seconds ago  0:00:07  C1             python train.py
	137f3d2a  running   9 seconds ago  0:00:07  C1             [notebook]
	18cb1ce2  success   1 day ago      0:00:01  C1             python task.py
	d75e8553  success   1 day ago      0:00:01  C1             python task.py
	f95b01a1  success   2 days ago     0:00:02  C1             python task.py
	71fe89cc  success   2 days ago     0:00:02  C1             python task.py
	b46cbb8e  success   3 days ago     0:00:02  C1             python task.py
	dd75b3fb  success   3 days ago     0:00:02  C1             python task.py

Volumes
-------

The rorodata platform has built-in support for *volumes* for storing persistent data. By default, two volumes ``data`` and ``notebooks`` are created for every project when the project is created. The volumes used to store any input data, intermediate results, checkpoints and final results. 

Volumes can also be used for storing machine learning models, but the model management system provided by the rorodata platform offers much better capabilities. 

To ``roro volumes`` command can be used to list the volumes in a project. ::

	$ roro volumes
	data
	notebooks

New volumes can be created using the ``roro volumes:add`` command. ::

	$ roro volumes:add new-volume-name
	Volume new-volume-name added to the project credit-risk

To list files in a volume::

	$ roro volumes:ls notebooks
	credit-risk.ipynb

Files can copied to and from a volume. 

For example, to copy a local file to ``data`` volume::

	$ roro cp dataset.csv data:dataset.csv

Or the other way::

	$ roro cp data:dataset.csv dataset.csv

Config
------

The rorodata platform provides support for storing the project secrets like database urls, access and secret keys for various third-party services, etc.

The config variables are set in the environment of every process that is run in the project.

The ``roro config`` comamnd lists all the available config variables. ::

	$ roro config
	=== credit-risk Config Vars
	DATABSE_URL: postgres://yxulQ5Ib9:QOJoFJZwv5FYIM0y@db1.example.com

One or more config variables can be added using the ``roro config:set`` command. ::

	$ roro config:set X=1 Y=2
	Updated config vars

	$ roro config
	=== credit-risk Config Vars
	DATABSE_URL: postgres://yxulQ5Ib9:QOJoFJZwv5FYIM0y@db1.example.com
	X: 1
	Y: 2

The ``roro config:unset`` command is used to unset config vars. ::

	$ roro config:unset X
	Updated config vars

	$ roro config
	=== credit-risk Config Vars
	DATABSE_URL: postgres://yxulQ5Ib9:QOJoFJZwv5FYIM0y@db1.example.com
	Y: 2

Please remember that the services are not restarted after ``config:set`` or ``config:unset``. They may have to be restarted using the ``roro deploy`` command to use the new configuration.
