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

**Bugfix**

* Custom test execution summary displayed incorrect information
* HTML characters aren't escaped in logs of exception stack traces.


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
