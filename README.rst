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

Subset
~~~~~~

::

   $ nosetests --launchable-subset --launchable-build-number <build number> --launchable-subset-options <Launchable CLI subset options>

You need to specify ``--launchable-subset-options`` flag and give it
Launchable CLI subset command options. For example, if you want to
create a fixed time-based subset it looks like
``--launchable-subset-options '--time 600'``.

For more information on the CLI options, please visit `the CLI
documentation
page <https://docs.launchableinc.com/resources/cli-reference#subset>`__.

Record only
~~~~~~~~~~~

::

   $ nosetests --launchable-record-only --launchable-build-number <build number>

In addition, you may need to set the following environment variables in
your environment. These values should be provided from Launchable.

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

Pull requests are always appreciated. Below are some tips on developing
nose-launchable plugin.

Install nose-launchable locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to see whether your changes work as expected, run the
following command to install the plugin locally.

.. code:: bash

   $ python setup.py install

Release nose-launchable
~~~~~~~~~~~~~~~~~~~~~~~

1. (Optional) Run ``./scripts/bump_up.sh``
2. Run ``./scripts/bump_up.sh`` and update nose_launchable/version.py
