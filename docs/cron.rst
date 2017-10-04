Scheduling Periodic Tasks
-------------------------

The rordata platform has support for scheduling periodic tasks. The periodic tasks are specifed in the `roro.yml` file in the project. Here is a sample ``roro.yml`` file with a periodic task::

	project: credit-risk
	runtime: python3

    tasks:
        - name: retrain
          command: python train.py
          when: every day at 10:00 AM

It is possible to specify multiple tasks per project. Each task contains a unique name, the command to run and the when to run the task. 

The ``when`` field is specified in a simple english-like format. The following are some examples::

	every day at 10:00 AM
	every day at 10:00 PM
	every day at 20:00
	every week on sunday at 10:00 AM
	every month on first day at 10:00 AM
	every month on day 2 at 10:00 AM

The scheduled tasks are updated after every deploy. To update the scheduled tasks for a project, you'll have to update them in the ``roro.yml`` file followed by running the ``roro deploy`` command.

At the scheduled time, the scheduled tasks will be run on the platform and they can be see using the ``roro ps`` command and logs of that can be seen using the ``roro logs`` command.
