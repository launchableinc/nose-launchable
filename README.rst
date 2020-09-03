nose-reorder
============

A nose plugin to reorder tests by likelihood of failure. This plugin
needs to access `Launbhable <https://www.launchableinc.com/>`__ API.

Install
-------

::

   $ pip install nose-reorder

Usage
-----

::

   $ nosetests --reorder

In addition to specifying the ``--reorder`` flag, you need to set the
following environment variables in your environment. These values should
be provided from Launchable.

+-----------------------------------+-----------------------------------+
| Key                               | Description                       |
+===================================+===================================+
| LAUNCH                            | AWS access key id to retrieve a   |
| ABLE_REORDERING_AWS_ACCESS_KEY_ID | request template file             |
+-----------------------------------+-----------------------------------+
| LAUNCHABLE                        | AWS secret access key to retrieve |
| _REORDERING_AWS_SECRET_ACCESS_KEY | a request template file           |
+-----------------------------------+-----------------------------------+
| LAUNCHABLE_REORDERING_API_TOKEN   | API token to access Launchable    |
|                                   | API                               |
+-----------------------------------+-----------------------------------+
| LAUNCHABLE_REORDERING_DIR_NAME    | Directory name storing a request  |
|                                   | template file                     |
+-----------------------------------+-----------------------------------+
| LAUNCHABLE_REORDERING_BASE_URL    | Launchable API URL                |
+-----------------------------------+-----------------------------------+
| LAUNCHABLE_REORDERING_ORG_NAME    | Launchable organization name      |
+-----------------------------------+-----------------------------------+
| LAU                               | Launchable workspace name         |
| NCHABLE_REORDERING_WORKSPACE_NAME |                                   |
+-----------------------------------+-----------------------------------+

Development
-----------

Pull requests are always appreciated. If you want to see whether your
changes work as expected, run the following command to install the
plugin locally.

.. code:: bash

   $ python setup.py develop
