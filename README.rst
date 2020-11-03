========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/python-gavel-db/badge/?style=flat
    :target: https://readthedocs.org/projects/python-gaveldb
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.org/MGlauer/python-gavel-db.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/MGlauer/python-gavel-db

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/MGlauer/python-gavel-db?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/MGlauer/python-gavel-db

.. |requires| image:: https://requires.io/github/MGlauer/python-gavel-db/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/MGlauer/python-gavel-db/requirements/?branch=master

.. |codecov| image:: https://codecov.io/gh/MGlauer/python-gavel-db/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/MGlauer/python-gavel-db

.. |version| image:: https://img.shields.io/pypi/v/gavel-db.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/gavel-db

.. |wheel| image:: https://img.shields.io/pypi/wheel/gavel-db.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/gavel-db

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/gavel-db.svg
    :alt: Supported versions
    :target: https://pypi.org/project/gavel-db

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/gavel-db.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/gavel-db

.. |commits-since| image:: https://img.shields.io/github/commits-since/MGlauer/python-gavel-db/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/MGlauer/python-gavel-db/compare/v0.0.0...master



.. end-badges

A database extension for gavel

Installation
============

::

    pip install gavel-db

You can also install the in-development version with::

    pip install https://github.com/MGlauer/python-gavel-db/archive/master.zip


Documentation
=============


https://python-gaveldb.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
