.. Rorodata Platform documentation master file, created by
   sphinx-quickstart on Thu Aug 24 14:44:49 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Rorodata Platform
=================

Rorodata is a cloud platform that lets data science teams prototype, build and deploy machine learning applications faster by abstrcting away the non data science activities and streamlining the data science activities.

In a nutshell, the platform takes care of:

* provisioning hardware instances on demand
* managing software environments
* running scripts, services and notebooks and managing their URL endpoints
* scheduling periodic tasks
* managing data volumes
* managing multiple versions of machine learning models

Quick Start
-----------

The rorodata platform is modeled around projects. Each project is independent unit of work with its own code, data, services and machine learning models.

The primary interface to work with the rorodata platform is using a command-line tool called ``roro``. It can be installed using pip::

	$ pip install roro

It is suggested to use Python 3 when installing the client.

You can verify the version of the client, using::

	$ roro version
	roro, version 0.1.6

Once installed, make sure you log in to the platform using::

	$ roro login
	Email address: anand@rorodata.com
	Password:
	Login successful.

It is prompt for your email and password. If you don't already have an account, please sign up at http://www.rorodata.com/.

The list of available projects can be found using::

	$ roro projects
	hello-world
	credit-risk

And you can create a new project using::

	$ roro create my-new-project
	Created project: my-new-project

You can find the available commands using::

	$ roro --help

And help about any particular command using::

	$ roro <command-name> --help

Project Organization
^^^^^^^^^^^^^^^^^^^^

Each project in the rorodata platform contains a special file named ``roro.yml``. It specifies project-name, the runtime, the services to run and the periodic tasks.

Sample organization of a project looks something like this::

	credit-risk/
	├── predict.py
	├── requirements.txt
	├── roro.yml
	└── train.py

The `roro.yml` file looks something like this::

	project: credit-risk
	runtime: python3

	services:
	  - name: default
	    function: predict.predict

The field ``project`` indicates the name of the project. Project name is unique. The field ``runtime`` indicates the software runtime to use. The default runtime is ``python3``. The available runtimes are described later in this section.

The field ``services`` indicates the services to run. The file format of the ``roro.yml`` file is described in detail in section below.

Deploying the Project
^^^^^^^^^^^^^^^^^^^^^

Once the code and the ``roro.yml`` file are ready, you can deploy the project using the deploy command. ::

	$ roro deploy
	Deploying project credit-risk. This may take a few moments ...
	Building docker image... done.
	Updating scheduled jobs... done.
	Restarted one service.
	  default: https://credit-risk.rorocloud.io/

	Deployed version 5 of credit-risk project.

Please remember that the deploy command must the run from the project directory, the directory where the ``roro.yml`` file is present.

The deploy command all the contents of the project directory and submit it to the platform. The platform looks at the roro.yml file and creates a new docker image with the latest code using the specified runtime as the base image and installing any python packages specified in the ``requirements.txt`` file, if present.

After creating the docker image, it continues to run the specified services and expose them at an URL end point. The service with name `default` is considered special and that service will be exposed at ``https://<project-name>.rorocloud.io/`` and all other services will be exposed as ``https://<project-name>--<service-name>.rorocloud.io/``.

Running Scripts
^^^^^^^^^^^^^^^

The ``roro run`` command is used run any script on the rorodata platform.

	$ roro run python training.py
	Started new job 4fa27081

That starts a new job and that runs on the platform. You can look at the logs of the job using the ``roro logs`` command, which contains the all logs printed by the script.::

	$ roro logs 4fa27081
	starting the job
	training decision tree model...
	training complete.
	the model is saved to /volumes/data/model.pkl

Please remember that it uses the code that is last deployed. If you have any changes to the code that you want to run, you need to deploy before running the script.

Running notebooks
^^^^^^^^^^^^^^^^^

Notebooks can be run using the ``roro run:notebook`` command. ::

	$ roro run:notebook
	starting the job
	Jupyter notebook is available at:
	https://517832f3.rorocloud.io/?token=rorocloud

	The jupyter notebook server can be stopped using:
	    roro stop 517832f3

It starts a new notebook in the project's software environment created using the previous deploy and provides a URL endpoint to access it.

Please remember that the notebook server continues to run until it is stopped.

Reference
---------

.. toctree::
   :maxdepth: 3

   cli
   cron
   models
