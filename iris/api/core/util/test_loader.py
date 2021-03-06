# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import logging
import os
import sys

from iris.api.core.util.core_helper import IrisCore


logger = logging.getLogger(__name__)


def get_tests_from_text_file(arg):
    test_list = []
    test_packages = []

    if os.path.isfile(arg):
        logger.debug('"%s" found. Proceeding ...' % arg)
        with open(arg, 'r') as f:
            test_paths_list = [line.strip() for line in f]
        if len(test_paths_list) == 0:
            logger.error('"%s" does not contain any valid test paths. Exiting program ...' % str(arg))
            return test_list, test_packages
        logger.debug('Tests found in the test suite file:\n\n%s\n' % '\n'.join(map(str, test_paths_list)))
        logger.debug('Validating test paths ...')
        for test_path in test_paths_list:
            if os.path.isfile(test_path):
                logger.debug('"%s" is a valid test path. Proceeding ...' % test_path)
                test_list.append(os.path.splitext(os.path.basename(test_path))[0])
                test_packages.append(os.path.dirname(test_path))
            else:
                logger.warning('"%s" is not a valid test path. Skipping ...' % test_path)

        if len(test_list) == 0:
            logger.error('"%s" does not contain any valid test paths. Exiting program ...' % str(arg))
            return test_list, test_packages
    else:
        logger.error('Could not locate "%s" . Exiting program ...', str(arg))
        return test_list, test_packages
    logger.debug('List of tests to execute: [%s]' % ', '.join(map(str, test_list)))
    return test_list, test_packages


def get_tests_from_list(app):
    test_list = []
    test_packages = []

    for name in app.args.test.split(','):
        if '.py' in name:
            name = name.split('.py')[0]
        name = name.strip()
        for package in app.master_test_list:
            for test in app.master_test_list[package]:
                if name == test['name']:
                    test_list.append(name)
                    if package not in test_packages:
                        test_packages.append(package)
        if name not in test_list:
            logger.warning('Could not locate test: %s' % name)

    if len(test_list) == 0:
        logger.error('No tests to run. Exiting program ...')
    return test_list, test_packages


def get_tests_from_directory(app):
    return app.all_tests, app.all_packages


def get_tests_from_package(app):
    test_list = []
    test_packages = [str(item).strip() for item in app.args.directory.split(',')]
    for package in test_packages:
        try:
            if app.master_test_list[package]:
                for test in app.master_test_list[package]:
                    test_list.append(test["name"])
        except KeyError:
            logger.warning('Could not locate %s' % package)
    if len(test_list) == 0:
        logger.debug('No tests associated with package(s): %s' % test_packages)
    return test_list, test_packages


def get_tests_from_object(obj):
    test_list = []
    test_packages = []
    for package in obj:
        for test in obj[package]:
            test_list.append(test['name'])
            module = os.path.dirname(test['module'])
        if module not in test_packages:
            test_packages.append(module)
    return test_list, test_packages


def sorted_walk(directory, topdown=True, onerror=None):

    names = os.listdir(directory)
    names.sort()
    dirs, nondirs = [], []

    for name in names:
        if os.path.isdir(os.path.join(directory, name)):
            dirs.append(name)
        else:
            nondirs.append(name)

    if topdown:
        yield directory, dirs, nondirs
    for name in dirs:
        path = os.path.join(directory, name)
        if not os.path.islink(path):
            for x in sorted_walk(path, topdown, onerror):
                yield x
    if not topdown:
        yield directory, dirs, nondirs


def scan_all_tests(arg):
    test_list = []
    test_packages = []

    if os.path.isdir(arg):
        tests_directory = arg
    else:
        tests_directory = os.path.join(IrisCore.get_module_dir(), 'iris', 'tests')

    logger.debug('Path %s found. Checking content ...', tests_directory)

    for dir_path, sub_dirs, all_files in sorted_walk(tests_directory):
        for current_file in all_files:
            if current_file.endswith('.py') and not current_file.startswith('__'):
                test_list.append(os.path.splitext(current_file)[0])
                if dir_path not in test_packages:
                    test_packages.append(dir_path)

    if len(test_list) == 0:
        logger.error('Directory %s does not contain test files. Exiting program ...' % tests_directory)
        return test_list, test_packages
    else:
        logger.debug('Test packages: %s', test_packages)
        logger.debug('List of all tests found: [%s]' % ', '.join(map(str, test_list)))
        for package in test_packages:
            sys.path.append(package)
        return test_list, test_packages


def remove_excluded_tests(app):
    if app.args.exclude:
        exclude_list = [str(item).strip() for item in app.args.exclude.split(',')]
        logger.debug('Processing exclude list: %s' % ''.join(exclude_list))

        test_list = []
        for item in exclude_list:
            try:
                for test in app.master_test_list[item]:
                    test_list.append(test["name"])
            except KeyError:
                logger.debug('Could not find package: %s' % item)

        exclude_list += test_list
        for item in exclude_list:
            try:
                app.test_list.remove(item)
            except ValueError:
                logger.debug('Excluded item not found in test list: %s' % item)


def load_tests(app):
    """Test loading

    Test loading is done by providing a list of test names separated by comma, a path to a file containing a custom list
    of tests or a directory. The provided list of test names can be with or without .py extension.

    The path to the file that contains the list of tests should have .txt extension. The full path is needed. For
    example: '/Users/user_name/full_path/test_suite.txt'. The content of the file should be a simple line-delimited list
    of test paths (full path required including file extensions).
    """

    temp_test_list_1 = []
    temp_test_packages_1 = []
    temp_test_list_2 = []
    temp_test_packages_2 = []

    if app.args.rerun:
        path = os.path.join(app.args.workdir, 'runs', 'last_fail.txt')
        app.args.test = path
        logger.info('Re-running failed tests from previous run.')

    if app.args.test:
        if app.args.test.endswith('.txt'):
            logger.debug('Loading tests from text file: %s' % app.args.test)
            temp_test_list_1, temp_test_packages_1 = get_tests_from_text_file(app.args.test)
        else:
            logger.debug('Loading tests from list.')
            temp_test_list_1, temp_test_packages_1 = get_tests_from_list(app)

    if app.args.directory:
        if not os.path.exists(app.args.directory):
            logger.debug('Loading tests from packages.')
            temp_test_list_2, temp_test_packages_2 = get_tests_from_package(app)
        elif not app.args.test:
            logger.debug('Loading tests from directory: %s' % app.args.directory)
            temp_test_list_2, temp_test_packages_2 = get_tests_from_directory(app)

    app.test_list = temp_test_list_1 + temp_test_list_2
    app.test_packages = temp_test_packages_1 + temp_test_packages_2

    remove_excluded_tests(app)

    logger.debug('Found tests: %s' % ''.join(app.test_list))
    logger.debug('Found packages: %s' % ''.join(app.test_packages))

    if len(app.test_list) == 0:
        logger.error('Specified tests not found, aborting run.')
        app.finish(code=1)
