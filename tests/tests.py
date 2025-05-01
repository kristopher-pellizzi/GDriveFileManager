import os
import sys
import argparse as ap
from typing import Any, Dict

if __name__ == '__main__':
    # Required to add the main src code into the module finding paths list
    sys.path.append(os.path.abspath(os.path.join(sys.path[0], '..', 'src')))

from tester import *

def run_tests(tests, exec_list):
    test_results = dict()

    if exec_list is not None:
        tests=dict(filter(lambda x: x[0] in exec_list, tests.items()))

    for name,test in tests.items():
        print()
        print(f"Running test {name}")
        res = test.run()
        print(f"Test {name} completed")
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

    return parser.parse_args()


def main():
    tests = {
        'getfiles': GetFilesTester(),
        'search': SearchTester(),
        'get': GetFileTester(),
        'download': DownloadTester(),
        'update': UpdateTester(),
        'create': CreateTester(),
        'delete': DeleteTester()
    }

    args = parse_args(tests)

    exec_list = args.tests

    test_results = run_tests(tests, exec_list) 

    print()
    for name,res in test_results.items():
        outcome = "succeded" if res else "failed"
        print(f"Test {name} {outcome}")


if __name__ == '__main__':
    main()
    
