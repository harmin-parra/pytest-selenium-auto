========
Features
========

The events being intercepted are:

* ``after_navigate_to``
* ``after_navigate_back``
* ``after_navigate_forward``
* ``click``
* ``after_change_value_of``

----

Docstring of tests are also included in the report, as mean to provide a long description of tests.

Therefore, you are highly encouraged to document your tests with docstrings.

=====
Usage
=====

Options
=======

Required options via command line
---------------------------------

* **browser**
 
The browser to use.

Accepted values: ``firefox``, ``chrome``, ``edge`` or ``safari``

Optional options via command line
---------------------------------

* **screenshots**

The strategy of screenshot gathering.

Accepted values:

* ``all``:    Screenshot for each intercepted webdriver event.

* ``last``:   Screenshot of the last step of each test.

* ``failed``: Screenshot of the last step of each ``failed``, ``xfailed`` and ``xpassed`` test.

* ``none``:   Disables automatic screenshot gathering.

Default value: ``all``

Optional options via pytest.ini file
------------------------------------

* **maximize_window**

Whether to maximize the browser window.

Accepted values: ``True`` or ``False``

Default value: ``False``

----

* **description_tag**

The HTML tag for the test description (test docstring).

Accepted values: ``h1``, ``h2``, ``h3``, ``p`` or ``pre``

Default value: ``h2``

----

* **separator_display**

Whether to display a horizontal line between the description and the screenshots.

Accepted values: ``True`` or ``False``

Default value: ``True``

----

* **separator_color**

The color of the horizontal line. Value can be set in any valid format accepted by CSS (Hexadecimal, RGB or predefined color name). 

Default value: ``gray``

----

* **separator_height**

The height of the horizontal line.

Default value: ``5px``


Example
=======

The plugin provides a function scoped ``webdriver`` fixture.

**pytest-selenium-auto** needs to be executed in conjunction of **pytest-html** plugin. Therefore, the ``--html`` option also needs to be provided.

Command-line invocation
-----------------------

.. code-block:: bash

  pytest --html=report/report.html --browser=chrome --screenshots=all

Sample code
-----------

.. code-block:: python

  def test_sample(webdriver):
      """
      My first awesome test
      We do a lot of awesome stuff here
    
      check it out
      """

      webdriver.get("https://www.selenium.dev/selenium/web/web-form.html")
      webdriver.find_element(By.NAME, 'my-text').send_keys('login')
      webdriver.find_element(By.NAME, 'my-password').send_keys('password')

Sample report
-------------

.. image:: example.png
