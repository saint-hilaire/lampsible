# Lampsible Contributing Guidelines

Thank you for your interest in Lampsible. This document will help to make it easier
for you to contribute code.

## Setting up your development environment

Something like this should work:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

## Branching guidelines

All code changes are made through pull requests via the latest develop branch, currently `dev/v2`.
Though not strictly required, it would be a big help if you name your topic branch
something like `feature/gh-9-some-github-issue` or `bugfix/gh-10-other-github-issue`,
and include that branch name into the header line of your commit message, something like this:
```bash
feature/gh-9-some-github-issue

- Implement the feature like this or that.
```


## Unit tests

If possible, please include unit tests for your changes. If you simply add it to
_test/test_lampsible.py_, that should probably be fine.

However, unit tests are a bit tricky in Lampsible. To run the tests, you need to
provide an actual host on which Lampsible can install whatever it is you're trying to test.
And as a word of caution, will install public facing web apps with insecure passwords!
For this reason, unit tests are optional - if you omit this, I'll take care of it myself.
At any rate, the easiest way to run the tests is to do something like this:

```
export LAMPSIBLE_REMOTE=realuser@your-real-server.com
# These 2 aren't super important, if you omit them, the
# Laravel tests will simply be skipped.
export LAMPSIBLE_LARAVEL_NAME=my-laravel-app
export LAMPSIBLE_LARAVEL_PATH=/path/to/my-laravel-app-2.0.tar.gz
python -m unittest
```

Lampsible will install various things onto the host specified by `LAMPSIBLE_REMOTE`, so beware!
This server should be insensitive in that regard. Also, Lampsible will set insecure passwords
on that server, so again, beware! You should tear down that server after running tests.

Also, if you run the whole test suite, at some point, the test
will "fail" on the "Ansible side" because of some edge case
related to Composer packages, caused by a non empty
`composer_working_directory`. This is not really a problem.
Lampsible is not intended to install Drupal, WordPress, etc, alongside
each other on the same host. So to really run these tests, you
should run them one at a time
( `python -m unittest test.test_lampsible.TestLampsible.test_wordpress`, etc. ),
and rebuild the server after each test case.

The nature of Ansible automations - it requires some real remote server -
poses a unique challenge with regards to unit tests. However,
in spite of this little drawback, these tests are still quite convenient
when you change the code but want to make sure nothing breaks.
