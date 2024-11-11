import unittest
import json
import logging
import datetime
import random
from jira import JIRA
import os
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import Timeout, RequestException

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='combined_script.log',
                    filemode='a')
logger = logging.getLogger(__name__)

# Constants
USERNAME = ""
#Replace with the Jira username
PASSWORD = ""
#Replace with the Jira Password token
HOST = ""
#Replace with the Jira base URL
PROJECT_KEY = ""
#Replace with the project key we want to submit the automation results to in Zephyr Scale
GLOBAL_TIMEOUT = 20


class TestCase(object):
    def __init__(self, key=None, name=None):
        self.key = key
        self.name = name

def test_case(**kwargs):
    def decorator(func):
        func.test_case = TestCase(**kwargs)
        return func
    return decorator

class Calculator(object):
    def sum(self, a, b):
        return a + b

class CalculatorSumTest(unittest.TestCase):
    @test_case(key="")
    # Repalce key with the test case key from the test case in Zephyr Scale
    #Ex: "MIGB-T10270
    def test_sumTwoNumbersAndPass(self):
        calculator = Calculator()
        self.assertEqual(3, calculator.sum(3, 2))

    @test_case(key="")
    # Repalce key with the test case key from the test case in Zephyr Scale
    #Ex: "MIGB-T10271
    def test_sumTwoNumbersAndFail(self):
        calculator = Calculator()
        self.assertNotEqual(2, calculator.sum(3, 2))

class JSONTestResult(unittest.TestResult):
    def __init__(self):
        super().__init__()
        self.executions = []

    def addSuccess(self, test):
        self._add_execution(test, "Pass")

    def addFailure(self, test, err):
        self._add_execution(test, "Fail")

    def _add_execution(self, test, result):
        execution = {
            "status": result,
            "executionTime": random.randint(60000, 300000),  # Random time between 1-5 minutes
            "actualStartDate": datetime.datetime.now().isoformat(),
            "actualEndDate": (datetime.datetime.now() + datetime.timedelta(minutes=5)).isoformat(),
        }
        
        if hasattr(test, '_testMethodName'):
            test_method = getattr(test, test._testMethodName)
            if hasattr(test_method, 'test_case'):
                test_case = test_method.test_case
                if hasattr(test_case, 'key'):
                    execution["testCaseKey"] = test_case.key
        
        if result == "Fail":
            jira_issue_key = self._create_jira_bug(test)
            execution.update({
                "comment": "The test has failed on some automation tool procedure.",
                "issueLinks": [jira_issue_key],
            })
                
        
        self.executions.append(execution)

    def _create_jira_bug(self, test):
        # Use the constants defined at the top of the file
        jira_url = HOST
        jira_username = USERNAME
        jira_api_token = PASSWORD

        jira = JIRA(server=jira_url, basic_auth=(jira_username, jira_api_token))

        issue_dict = {
            'project': {'key': PROJECT_KEY},
            'summary': f'Automated Test Failure: {test._testMethodName}',
            'description': f'The automated test {test._testMethodName} has failed.',
            'issuetype': {'name': 'Bug'},
        }

        new_issue = jira.create_issue(fields=issue_dict)
        return new_issue.key
    

def run_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(CalculatorSumTest)
    result = JSONTestResult()
    suite.run(result)

    with open('zephyrscale_result.json', 'w') as f:
        json.dump(result.executions, f, indent=2)

    logger.info("Test results written to zephyrscale_result.json")

def send_results():
    session = requests.Session()
    session.auth = (USERNAME, PASSWORD)

    # Create test run
    post_url = f"{HOST}/rest/atm/1.0/testrun"
    payload = {
        "projectKey": PROJECT_KEY,
        "name": "Automated Test Run"
    }
    headers = {'Content-Type': 'application/json'}

    try:
        response = session.post(post_url, json=payload, headers=headers, timeout=GLOBAL_TIMEOUT)
        response.raise_for_status()
        result = response.json()
        logger.info(f"Test run created successfully. Test run key: {result.get('key')}")
        cycle_key = result.get('key')

        # Load and send test results
        with open('zephyrscale_result.json', 'r') as f:
            payload_data = json.load(f)

        testresults_url = f"{HOST}/rest/atm/1.0/testrun/{cycle_key}/testresults"
        response = session.post(testresults_url, json=payload_data, headers=headers, timeout=GLOBAL_TIMEOUT)
        response.raise_for_status()
        result = response.json()
        logger.info(f"Test results added successfully. Response: {result}")

    except Timeout:
        logger.error(f"Request timed out after {GLOBAL_TIMEOUT} seconds")
    except RequestException as e:
        logger.error(f"An error occurred while sending the request: {str(e)}")
    except json.JSONDecodeError:
        logger.error("Failed to parse the response as JSON")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
    finally:
        session.close()

if __name__ == '__main__':
    run_tests()
    send_results()