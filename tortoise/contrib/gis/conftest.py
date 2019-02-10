from tortoise.contrib.test import finalizer, env_initializer


def pytest_runtest_setup(item):
    env_initializer()


def pytest_runtest_teardown(item, nextitem):
    finalizer()
