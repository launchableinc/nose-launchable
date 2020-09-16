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

==================================== ==================================
Key                                  Description
==================================== ==================================
LAUNCHABLE_REORDERING_API_TOKEN      API token to access Launchable API
LAUNCHABLE_REORDERING_BASE_URL       Launchable API URL
LAUNCHABLE_REORDERING_ORG_NAME       Launchable organization name
LAUNCHABLE_REORDERING_WORKSPACE_NAME Launchable workspace name
LAUNCHABLE_REORDERING_TARGET_NAME    Launchable target model name
==================================== ==================================

Development
-----------

Pull requests are always appreciated. If you want to see whether your
changes work as expected, run the following command to install the
plugin locally.

.. code:: bash

   $ python setup.py develop
