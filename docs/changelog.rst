=========
Changelog
=========


1.3.1
=====

** Bug fix**

* Plugin crash on Windows OS caused by UnicodeEncodeError when saving some webpage souces.

**Changes**

* Can save full-page screenshots for Chromium-based browsers.

It is based on experimental *Chrome DevTools Protocol* code.


1.3.0
=====

**New feature**

* Possibility to log web page sources.

**Changes**

* Replacement of deprecated code.
* ``--show-attributes`` option has been renamed to ``--log-attributes``.


1.2.1
=====

**Bug fix**

* Pytest crashes when executing tests not using this plugin (not using the ``--browser`` option).


1.2.0
=====

**New features**

* Possibility to log WebElement attributes alongside screenshots.
* External CSS file can be added to the report.
* Comments can be added to manually logged screenshots.
* Some command-line and INI file options can be overloaded with pytest markers.

**Change**

* The custom test execution summary was removed because it displayed incorrect information

**Bug fix**

* HTML characters aren't escaped in logs of exception stack traces.

**Limitation**

* Since pytest-html 4.0.0, the CSS needs to be externally added with the ``--css`` command-line option.


1.1.0
=====

**New features**

* Support for user-provided browser options and capabilities.
* The report displays screenshot thumbnails.

**Improvement**

* Support for Chromium browser.


1.0.1
=====

**Bug fix**

* The plugin crashes with parametrized tests using the ``@pytest.mark.parametrize`` decorator.


1.0.0
=====

**Initial release**

**Limitations**

* No support for user-provided browser options or capabilities.
* No support for Chromium browser.
