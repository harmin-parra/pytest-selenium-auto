=========
Changelog
=========

1.2.0
-----

**New features**

* Possibility to log WebElement attributes alongside screenshots.
* External CSS file can be added to the report.
* Comments can be added to manually logged screenshots.
* Some command-line and INI file options can be overloaded with pytest markers.

**Change**

* The custom test execution summary was removed because it displayed incorrect information

**Bugfix**

* HTML characters aren't escaped in logs of exception stack traces.

**Limitation**

* Since pytest-html 4.0.0, the CSS sheet needs to be externally added with the `--css` command-line option.


1.1.0
-----

**New features**

* Support for user-provided browser options and capabilities.
* The report displays screenshot thumbnails.

**Improvement**

* Support for Chromium browser.


1.0.1
-----

**Bugfix**

* The plugin crashes with parametrized tests using the ``@pytest.mark.parametrize`` decorator.


1.0.0
-----

**Initial release**

**Limitations**

* No support for user-provided browser options or capabilities.
* No support for Chromium browser.
