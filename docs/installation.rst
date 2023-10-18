============
Installation
============

Requirements
------------

* ``pytest >= 7.0.0``
* ``pytest-html >= 4.0.0``
* ``pytest-metadata >= 3.0.0``
* ``pyyaml >= 5.3.1``
* ``selenium >= 4.11.0``


Installing pytest-selenium-auto
-------------------------------

.. code-block:: bash

  $ pip install pytest-selenium-auto


WARNING /!\
-----------

| **pytest-selenium-auto** and **playwright** are incompatible
| as both plugins use the ``--browser`` command-line option.

If you need to work with both plugins, you should install them in separate python virtual environments.

Same warning applies for any other plugin that might use the ``--browser`` command-line option as well.


Support for older pytest-html versions
--------------------------------------

If ``pytest-html <= 3.2.0``

.. code-block:: bash

  $ pip install pytest-selenium-auto==1.2.0
