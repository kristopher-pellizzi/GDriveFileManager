import os
import sys
import argparse as ap
import yaml
import logging
from typing import Any, Dict

if __name__ == '__main__':
    # Required to add the main src code into the module finding paths list
    sys.path.append(os.path.abspath(os.path.join(sys.path[0], '..', 'src')))

from tester import *

def run_tests(tests, exec_list):
    test_results = dict()

    if exec_list is not None:
        tests=dict(filter(lambda x: x[0] in exec_list, tests.items()))

    logger = logging.getLogger(__name__)

    for name,test in tests.items():
        logger.debug(f"Running test {name}")
        res = test.run()
        logger.debug(f"Test {name} completed")
        test_results[name] = res

    return test_results


def parse_args(tests: Dict[str, Any]):
    parser = ap.ArgumentParser()

    parser.add_argument("--test", "-t",
        action="append",
        default=None,
        help="This argument may be used multiple times in order to specify a list of tests to be executed. If not provided, all tests will be executed",
        choices=tests.keys(),
        dest='tests'
    )

    parser.add_argument("--config-path", "-c",
        help = "Path of the YAML config file that contains the set of parameters to launch each test",
        default = os.path.abspath(os.path.join(sys.path[0], 'config.yaml')),
        dest = "config_path"                    
    )

    parser.add_argument("--log-level", "-l",
        help = "Log level that indicates tests verbosity",
        choices = ['debug', 'info', 'warning', 'error'],
        default = 'info',
        dest = "log_level"                    
    )

    return parser.parse_args()


def fix_paths(config):
    logger = logging.getLogger(__name__)
    path_separator = "/"

    if not isinstance(config, dict):
        logger.debug(f"{config} is not an instance of dict")
        return
    
    for k,v in config.items():
        if isinstance(v, dict):
            fix_paths(v)
        elif isinstance(v, str) and path_separator in v:
            logger.debug(f"Detected path {v} for key {k}. Fixing path")
            path_segments = v.split(path_separator)
            fixed_path = os.path.abspath(os.path.join(sys.path[0], *path_segments))
            logger.debug(f"Fixed path: {fixed_path}")
            config[k] = fixed_path


def parse_config(f):
    config = yaml.safe_load(f)

    if 'tests' not in config:
        return dict()

    ret = config['tests']
    fix_paths(ret)

    return ret


def init_tests(tests, config):
    logger = logging.getLogger(__name__)
    ret = dict()

    for test, cls in tests.items():
        if test not in config or config[test] is None:
            logger.debug(f"No arguments found in the config file for test '{test}'. Default arguments will be used")
            ret[test] = cls()
        else:
            # Filter arguments in the config file which are not None (null in Yaml)
            kwargs = dict(filter(lambda x: x[1] is not None, config[test].items()))
            logger.debug(f"Arguments for test '{test}' read from config file: {kwargs.items()}")
            ret[test] = cls(**kwargs)

    return ret


def main():
    # Init dict with classes for each test
    tests = {
        'getfiles': GetFilesTester,
        'search': SearchTester,
        'get': GetFileTester,
        'download': DownloadTester,
        'update': UpdateTester,
        'create': CreateTester,
        'delete': DeleteTester
    }

    args = parse_args(tests)
    # Get root logger
    logger = logging.getLogger()

    log_level = args.log_level.lower()
    match log_level:
        case 'debug':
            log_level = logging.DEBUG
            # Reduce verbosity of urllib3 library
            logging.getLogger('urllib3').setLevel(logging.INFO)
        case 'info':
            log_level = logging.INFO
        case 'warning':
            log_level = logging.WARNING
        case 'error':
            log_level = logging.ERROR

    # If root logger is not configured yet, initialize it to the selected log-level
    if not logger.hasHandlers():
        h = logging.StreamHandler()
        f = logging.Formatter(fmt="{asctime} {name} [{levelname}]: {message}\n", style="{")
        h.setFormatter(f)
        logger.addHandler(h)
        logger.setLevel(log_level)
    
    # Start using module-level logger
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    exec_list = args.tests
    config_path = args.config_path

    if not os.path.exists(config_path):
        logger.warning(f"Path {config_path} does not exist. Default testers parameters will be used")
        config = dict()
    else:
        with open(config_path, "r") as f:
            config = parse_config(f)

    tests = init_tests(tests, config)

    test_results = run_tests(tests, exec_list) 

    for name,res in test_results.items():
        outcome = "succeded" if res else "failed"
        logger.info(f"Test {name} {outcome}")


if __name__ == '__main__':
    main()
    
