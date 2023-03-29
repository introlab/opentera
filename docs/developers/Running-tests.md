# Unit Tests
OpenTera aims to deploy robust and tested releases. To do so, unit tests are designed to test the various components of
the system, such as [database models](Database-Structure) and various [APIs](../services/teraserver/api/API).

Tests are based on [PyTest](https://www.pytest.org) and [unittest](https://docs.python.org/3/library/unittest.html) and
are located in the [tests folder](https://github.com/introlab/opentera/tree/main/teraserver/python/tests) of the project.

While it's hard to develop tests that cover every situation, effort is being put into each new features and releases to
ensure that features are tested before being deployed on a production server.

## Self-contained environment
Unit tests are designed to run even if the server itself is not running. By creating a local 
[Flask](https://flask.palletsprojects.com) component to serve the OpenTera API and using a local 
[SqlLite database](https://www.sqlite.org), tests are self-contained and do no interact with an actual OpenTera server
instance. However, a [redis](https://redis.io/) server is still required to run the tests.

More specifically, each test class setups a new database, ensuring that changes made by the tests functions do not 
have a larger scope than the class itself, which helps prevent unwanted cross-interactions and tests in another class
that would fail because the database data changed. 

## Creating unit tests
Developers are encouraged to develop unit tests while expanding OpenTera core service (and also in their own services,
even if this is beyond the scope of this documentation).

A few guidelines need to be followed while doing so:

1. Each class needs to be self-contained and not depends on external components. If testing API features, the test class
should inherits from the related base test class (such as `BaseUserAPITest` for the user API tests).

2. Each test function should ensure that the changed data in the database is set back to its initial
value after performing the test. If, for example, a test deleted some object in the database, they should be recreated
to prevent following tests in the same class to fail. Remember that the data is persistent for the class only - it is
not recreated automatically after each test.
   
3. Always ensure to run the full tests after adding new features or modifying existing ones. Some changes can have 
unexpected impacts on other parts of the project, considering the large codebase of the OpenTera server.

## Running unit tests
While developing features, it is recommended to run (and update) manual tests once in a while to ensure the quality of
the modifications. An automatic testing feature is also automated on GitHub.

### Manual testing
Tests can be manually run simply by running the `pytest` command in a python console, followed by the path containing
the tests to be executed. It is possible to run all the tests with the base `tests` path. 

If using [PyCharm IDE](https://www.jetbrains.com/pycharm/), tests can be simply run with the contextual menu (displayed
by right-clicking on a test folder) and selecting the `Run pytest in...` option.

### Automatic testing on pull requests
GitHub automation is used to run all the tests on every pull request (and changes made to it). If a pull request does
not successfully run the tests, it will not be merged.
