nose-launchable
===============

A nose plugin to interact with
`Launchable <https://www.launchableinc.com/>`__ API.

Install
-------

::

   $ pip install nose-launchable

Usage
-----

Reorder
~~~~~~~

::

   $ nosetests --launchable-reorder --launchable-build-number <build number>

Subset
~~~~~~

::

   $ nosetests --launchable-subset --launchable-build-number <build number> --launchable-subset-target <target percentage>

In addition to specifying the ``--launchable-reorder`` /
``--launchable-subset`` flag, you may need to set the following
environment variables in your environment. These values should be
provided from Launchable.

+-----------------------------------+-----------------------------------+
| Key                               | Description                       |
+===================================+===================================+
| LAUNCHABLE_BASE_URL               | (Optional) A Launchable API URL.  |
|                                   | Default is                        |
|                                   | ``https:                          |
|                                   | //api.mercury.launchableinc.com`` |
+-----------------------------------+-----------------------------------+
| LAUNCHABLE_BUILD_NUMBER           | (Optional) A CI/CD build number   |
+-----------------------------------+-----------------------------------+
| LAUNCHABLE_DEBUG                  | (Optional) Prints out debug logs  |
+-----------------------------------+-----------------------------------+
| LAUNCHABLE_TOKEN                  | (Required) A token to access      |
|                                   | Launchable API                    |
+-----------------------------------+-----------------------------------+

Development
-----------

Pull requests are always appreciated. If you want to see whether your
changes work as expected, run the following command to install the
plugin locally.

.. code:: bash

   $ python setup.py develop
