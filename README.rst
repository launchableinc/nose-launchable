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

::

   $ nosetests --launchable --launchable-build-number <build number>

In addition to specifying the ``--launchable`` flag, you need to set the
following environment variables in your environment. These values should
be provided from Launchable.

======================= ================================
Key                     Description
======================= ================================
LAUNCHABLE_TOKEN        A token to access Launchable API
LAUNCHABLE_BUILD_NUMBER A CI/CD build number
LAUNCHABLE_DEBUG        Prints out debug logs
======================= ================================

Development
-----------

Pull requests are always appreciated. If you want to see whether your
changes work as expected, run the following command to install the
plugin locally.

.. code:: bash

   $ python setup.py develop
