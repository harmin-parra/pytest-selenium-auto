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

Accepted values: ``firefox``, ``chrome``, ``chromium``, ``edge`` or ``safari``

Optional options via command line
---------------------------------

* **screenshots**

The strategy of screenshot gathering.

Accepted values:

* ``all``:    Screenshot for each intercepted webdriver event.

* ``last``:   Screenshot of the last step of each test.

* ``failed``: Screenshot of the last step of each ``failed``, ``xfailed`` and ``xpassed`` test.

* ``manual``: Screenshots aren't logged automatically. They can still be logged manually.

* ``none``:   Screenshots are completely disabled.


Default value: ``all``

----

* **headless**

Whether to run the browser in headless mode.

Accepted values: ``True`` or ``False``

Default value: ``False``


Optional options via pytest.ini file
------------------------------------

* **maximize_window**

Whether to maximize the browser window.

Accepted values: ``True`` or ``False``

Default value: ``False``

----

* **driver_config**

JSON or YAML file path containing the driver configuration to use.

Accepted file extensions: 

``.json`` for JSON files

``.yaml`` or ``.yml`` for YAML files.

----

* **driver_firefox**

File path of the Firefox driver to use.

Takes precedence over the driver path mentioned in the JSON configuration file.

----

* **driver_chrome**

File path of the Chrome driver to use.

Takes precedence over the driver path mentioned in the JSON configuration file.

----

* **driver_chromium**

File path of the Chromium driver to use.

Takes precedence over the driver path mentioned in the JSON configuration file.

----

* **driver_edge**

File path of the Edge driver to use.

Takes precedence over the driver path mentioned in the JSON configuration file.

----

* **driver_safari**

File path of the Safari driver to use.

Takes precedence over the driver path mentioned in the JSON configuration file.

----

* **description_tag**

The HTML tag for the test description (test docstring).

Accepted values: ``h1``, ``h2``, ``h3``, ``p`` or ``pre``

Default value: ``h2``

----

* **separator_display**

Whether to display a horizontal line between the description and the screenshots.

Accepted values: ``True`` or ``False``

Default value: ``False``

----

* **separator_color**

The color of the horizontal line. Value can be set in any valid format accepted by CSS (Hexadecimal, RGB or predefined color name). 

Default value: ``gray``

----

* **separator_height**

The height of the horizontal line.

Default value: ``5px``

----

* **thumbnail_width**

The width of screenshot thumbnails. Value can be set in any valid format accepted by CSS (px, %, etc).

Default value: ``300px``


Screenshot gathering
====================

The screenshot gathering strategies are:

* ``all``:    Screenshot for each intercepted webdriver event.

* ``last``:   Screenshot of the last step of each test.

* ``failed``: Screenshot of the last step of each ``failed``, ``xfailed`` and ``xpassed`` test.

* ``manual``: Screenshot aren't logged automatically. They can still be logged manually.

* ``none``:   Screenshots are completely disabled.

The function scoped ``webdriver`` fixture provides a method named ``manual_screenshot`` that allows logging screenshots manually (``webdriver.manual_screenshot()``).

Manual logs will only appear in the HTML report when the screenshot gathering strategy is ``manual``.

In ``manual`` mode, screenshot of the last step of ``failed``, ``xfailed`` and ``xpassed`` tests are automatically logged as well.


Example
=======

The plugin provides a function scoped ``webdriver`` fixture.

**pytest-selenium-auto** needs to be executed in conjunction of **pytest-html** plugin. Therefore, the ``--html`` option also needs to be provided.

Command-line invocation
-----------------------

.. code-block:: bash

  pytest --html=report/report.html --browser=chrome --screenshots=all --headless

Sample ``pytest.ini`` file
--------------------------

.. code-block::

  maximize_window=True
  driver_firefox = /path/to/driver
  driver_config=/path/to/conf.yml

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


Sample YAML file configurations
===============================

* Simple YAML configuration:

.. code-block:: yaml

  capabilities:
      acceptInsecureCerts: true
      proxy:
          proxyType: manual
          httpProxy: localhost:8080
          sslProxy: localhost:8080
  window:
      headless: false
      maximize: false
      position:
          x: 10
          y: 10
      size:
          width: 600
          height: 600
  browsers:
      firefox:
          options:
              binary: /usr/bin/firefox
          service:
              driver_path: /usr/local/bin/geckodriver
              log_output: logs/geckodriver.log
      chrome:
          options:
              binary_location: /usr/bin/google-chrome
          service:
              driver_path: /usr/local/bin/chromedriver
              log_output: logs/chromedriver.log
      chromium:
          options:
              binary_location: /usr/bin/chromium
          service:
              driver_path: /usr/local/bin/chromedriver
              log_output: logs/chromiumdriver.log
      edge:
          options:
              binary_location: /opt/microsoft/msedge/msedge
          service:
              driver_path: /usr/local/bin/msedgedriver
              log_output: logs/edgedriver.log

* Complete YAML configuration:

.. code-block:: yaml

  capabilities:
      acceptInsecureCerts: true
      pageLoadStrategy: normal, eager or none
      timeouts:
          script: 30000
          pageLoad: 300000
          implicit: 0
      proxy:
          proxyType: pac, direct, autodetect, system or manual
          proxyAutoconfigUrl: url
          httpProxy: localhost:3128
          noProxy: localhost
          sslProxy: localhost:3128
          socksProxy: localhost:3128
          socksVersion: 0
  window:
      headless: false
      maximize: true
      position:
          x: 10
          y: 10
      rect:
          x: 10
          y: 10
          width: 200
          height: 200
      size:
          width: 200
          height: 200
  browsers:
      firefox:
          options:
              binary: /path/to/browser
              arguments:
                 -  arg1
                 -  arg2
              preferences:
                  pref1: value1
                  pref2: value2
          addons:
             -  /path/to/addon1
             -  /path/to/addon2
          profile:
              directory: /path/to/profile/directory or empty for null value
              preferences:
                  pref1: value1
                  pref2: value2
              extensions:
                 -  /path/to/extension1
                 -  /path/to/extension2
          service:
              driver_path: /path/to/driver
              log_output: /path/to/log
              port: 0
              args:
                 -  arg1
                 -  arg2
      chrome:
          options:
              binary_location: /path/to/browser
              arguments:
                 -  arg1
                 -  arg2
              extensions:
                 -  /path/to/extension1
                 -  /path/to/extension2
          service:
              driver_path: /path/to/driver
              log_output: /path/to/log
              port: 0
              args:
                 -  arg1
                 -  arg2
      edge:
          options:
              binary_location: /path/to/browser
              arguments:
                 -  arg1
                 -  arg2
              extensions:
                 -  /path/to/extension1
                 -  /path/to/extension2
          service:
              driver_path: /path/to/driver
              log_output: /path/to/log
              port: 0
              args:
                 -  arg1
                 -  arg2


Sample JSON file configurations
===============================

* Simple JSON configuration:

.. code-block:: JSON

  {
      "capabilities": {
          "acceptInsecureCerts": true,
          "proxy": {
              "proxyType": "manual",
              "httpProxy": "localhost:8080",
              "sslProxy" : "localhost:8080"
          }
      },    
      "window": {
          "headless": false,
          "maximize": false,
          "position": {
              "x": 10,
              "y": 10
          },
          "size": {
            "width": 600,
            "height": 600
          }
      },
      "browsers": {    
          "firefox": {
              "options": {
                  "binary": "/usr/bin/firefox"
              },
              "service":{
                  "driver_path": "/usr/local/bin/geckodriver",
                  "log_output": "logs/geckodriver.log"
              }
          },
          "chrome": {
              "options": {
                  "binary_location": "/usr/bin/google-chrome"
              },
              "service": {
                  "driver_path": "/usr/local/bin/chromedriver",
                  "log_output": "logs/chromedriver.log"
              }  
          },
          "chromium": {
              "options": {
                  "binary_location": "/usr/bin/chromium"
              },
              "service": {
                  "driver_path": "/usr/local/bin/chromedriver",
                  "log_output": "logs/chromiumdriver.log"
              }
          },
          "edge": {
              "options": {
                  "binary_location": "/opt/microsoft/msedge/msedge"
              },
              "service": {
                  "driver_path": "/usr/local/bin/msedgedriver",
                  "log_output": "logs/edgedriver.log"
              }
          }
      }
  }

* Complete JSON configuration:

.. code-block:: JSON

  {
      "capabilities": {
          "acceptInsecureCerts": true,
          "pageLoadStrategy": "normal, eager or none",
          "timeouts": {
              "script": 30000,
              "pageLoad": 300000,
              "implicit": 0
          },
          "proxy": {
              "proxyType": "pac, direct, autodetect, system or manual",
              "proxyAutoconfigUrl": "url",
              "httpProxy": "localhost:3128",
              "noProxy": "localhost",
              "sslProxy": "localhost:3128",
              "socksProxy": "localhost:3128",
              "socksVersion": 0
          }
      },
      "window": {
          "headless": false,
          "maximize": true,
          "position": {
              "x": 10,
              "y": 10
          },
          "rect": {
              "x": 10,
              "y": 10,
              "width": 200,
              "height": 200
          },
          "size": {
              "width": 200,
              "height": 200
          }
      },    
      "browsers": {
          "firefox": {
              "options": {
                  "binary": "/path/to/browser",
                  "arguments": [
                      "arg1",
                      "arg2"
                  ],
                  "preferences": {
                      "pref1": "value1",
                      "pref2": "value2"
                  }
              },
              "addons": [
                "/path/to/addon1",
                "/path/to/addon2"
              ],
              "profile":{
                  "directory": "/path/to/profile/directory" or null,
                  "preferences": {
                      "pref1": "value1",
                      "pref2": "value2"
                  },
                  "extensions": [
                      "/path/to/extension1",
                      "/path/to/extension2"
                  ]
              },
              "service":{
                  "driver_path": "/path/to/driver",
                  "log_output": "/path/to/log",
                  "port": 0,
                  "args": [
                      "arg1",
                      "arg2"
                  ]
              }
          },
          "chrome": {
              "options": {
                  "binary_location": "/path/to/browser",
                  "arguments": [
                      "arg1",
                      "arg2"
                  ],
                  "extensions": [
                      "/path/to/extension1",
                      "/path/to/extension2"
                  ]
              },
              "service": {
                  "driver_path": "/path/to/driver",
                  "log_output": "/path/to/log",
                  "port": 0,
                  "args": [
                      "arg1",
                      "arg2"
                  ]
              }
          },
          "edge": {
              "options": {
                  "binary_location": "/path/to/browser",
                  "arguments": [
                      "arg1",
                      "arg2"
                  ],
                  "extensions": [
                      "/path/to/extension1",
                      "/path/to/extension2"
                  ]
              },
              "service": {
                  "driver_path": "/path/to/driver",
                  "log_output": "/path/to/log",
                  "port": 0,
                  "args": [
                      "arg1",
                      "arg2"
                  ]
              }
          }
      }
  }


Sample report
=============

.. image:: example.png

