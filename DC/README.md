# Script Documentation

## Table of Contents

1. [Overview](#overview)
2. [`BulkUpdateTE.py`](#BulkUpdateTEpy)
   - [Purpose](#purpose)
   - [Script Details](#script-details)
   - [Usage](#usage)
   - [Example](#example)
3. [`BulkUpdateTE-Excel.py`](#BulkUpdateTE-Excelpy)
   - [Purpose](#purpose)
   - [Script Details](#script-details)
   - [Usage](#usage)
   - [Example](#example)
4. [`BulkUpdateTC.py`](#BulkUpdateTCpy)
   - [Purpose](#purpose)
   - [Script Details](#script-details)
   - [Usage](#usage)
   - [Example](#example)
5. [`BulkUpdateTC-Excel.py`](#BulkUpdateTC-Excelpy)
   - [Purpose](#purpose)
   - [Script Details](#script-details)
   - [Usage](#usage)
   - [Example](#example)
6. [`GetAllAssignableUsers.py`](#GetAllAssignableUserspy)
   - [Purpose](#purpose-1)
   - [Script Details](#script-details-1)
   - [Usage](#usage-1)
   - [Example](#example-1)
7. [`MigrateAllExecutionStatus-SquadtoScale.py`](#MigrateAllExecutionStatus-SquadtoScalepy)
   - [Purpose](#purpose-1)
   - [Script Details](#script-details-1)
   - [Usage](#usage-1)
   - [Example](#example-1)
8. [`unitTests_publishResultsZephyrScale_autoCreatedDefect.py`](#unitTests_publishResultsZephyrScale_autoCreatedDefectpy)
   - [Purpose](#purpose-1)
   - [Script Details](#script-details-1)
   - [Usage](#usage-1)
   - [Example](#example-1)
9. [`CreateTestCycle-Excel.py`](#CreateTestCycle-Excelpy)
   - [Purpose](#purpose)
   - [Script Details](#script-details)
   - [Usage](#usage)
   - [Example](#example)

---

## Overview

This project contains a number of key scripts. Below are detailed explanations of each script, including their purposes, usage, and example commands.

---

## `BulkUpdateTE.py`

### Purpose

`BulkUpdateTE.py` is a Python script designed to automate bulk update of two seperate process: 
1. Determining what executions are contained within a sprit (test cycle)
2. Updating a specific value across all executions in a sprint.

### Script Details

- **Execution**: The script runs a python file using four script input parameters: username, password, base url and cycle key.

### Usage

To execute the `BulkUpdateTE.py` script, navigate to the project directory and use the following command:

```bash
python `BulkUpdateTE.py` 
```

### Example

```bash
python BulkUpdateTE.py 
```

### Notes

- Ensure that the `BulkUpdateTE.py` script has been modified to include your jira instance specific values, and we are updating the correct objects in the executions.
- Python 3.x is required to run this script.

---

## `BulkUpdateTE-Excel.py`

### Purpose

`BulkUpdateTE-Excel.py` is a Python script designed to automate bulk update of two seperate process: 
1. Determining what executions are contained within a sprit (test cycle)
2. Updating a specific value across all executions in a sprint.

### Script Details

- **Execution**: The script runs a python file using four script input parameters: username, password, base url and cycle key.

### Usage

To execute the `BulkUpdateTE-Excel.py` script, navigate to the project directory and use the following command:

```bash
python `BulkUpdateTE-Excel.py` 
```

### Example

```bash
python BulkUpdateTE.py 
```

### Notes

- Ensure that the `BulkUpdateTE-Excel.py` script has been modified to include your jira instance specific values, and we are updating the correct objects in the executions.
- Python 3.x is required to run this script.
- csv is required to be in the same directory as the script. 

---

## `BulkUpdateTC.py`

### Purpose

`BulkUpdateTC.py` is a Python script designed to automate bulk update of test cases via API: 

### Script Details

- **Execution**: The script runs a python file using four script input parameters: username, password, base url and test case key.

### Usage

To execute the `BulkUpdateTC.py` script, navigate to the project directory and use the following command:

```bash
python `BulkUpdateTC.py` 
```

### Example

```bash
python BulkUpdateTC.py 
```

### Notes

- Ensure that the `BulkUpdateTC.py` script has been modified to include your jira instance specific values, and we are updating the correct objects in the executions.
- Python 3.x is required to run this script.


---


## `BulkUpdateTC-Excel.py`

### Purpose

`BulkUpdateTC-Excel.py` is a Python script designed to automate bulk update of two seperate process: 
1. Determining what executions are contained within a sprit (test cycle)
2. Updating a specific value across all executions in a sprint.

### Script Details

- **Execution**: The script runs a python file using three script input parameters: username, password, base url, the test case keys are pulled from excel.

### Usage

To execute the `BulkUpdateTC-Excel.py` script, navigate to the project directory and use the following command:

```bash
python `BulkUpdateTC-Excel.py` 
```

### Example

```bash
python BulkUpdateTC-Excel.py 
```

### Notes

- Ensure that the `BulkUpdateTC-Excel.py` script has been modified to include your jira instance specific values, and we are updating the correct objects in the executions.
- Python 3.x is required to run this script.
- csv is required to be in the same directory as the script. 

## `GetAllAssignableUsers.py`

### Purpose

`GetAllAssignableUsers.py` is a Python script that runs a specified query to determine what users are available in a given Jira project.

### Script Details

- **Execution**: The script runs a python file using four command-line input parameters: username, password, base url, and projectKey. 

### Usage

To run the `GetAllAssignableUsers.py` script, use the following command:

```bash
python GetAllAssignableUsers.py <username> <password> <instance_url> <projectKey>")
```

### Example

```bash
python GetAllAssignableUsers.py matt password https://jira.com OPS
```

### Notes

- Ensure that the `GetAllAssignableUsers.py` script has been modified to include your jira instance specific values, and we are using the correct command-line parameters.
- Python 3.x is required to run this script.

---

## `MigrateAllExecutionStatus-SquadtoScale-SquadtoScale.py`

### Purpose

`MigrateAllExecutionStatus-SquadtoScale.py` is a Python script that runs a specified query to migrate Zephyr Squad execution statuses, including custom statuses, to the associated Zephyr Scale projects.

### Script Details

- **Execution**: The script runs a python file using four command-line input parameters: username, password, projectKey, and instance. 

### Usage

To run the `MigrateAllExecutionStatus-SquadtoScale.py` script, use the following command:

```bash
python MigrateAllExecutionStatus-SquadtoScale.py <username> <password> <project_key>  <instance_url>
```

### Example

```bash
python MigrateAllExecutionStatus-SquadtoScale.py matt password https://jira.com OPS
```

### Notes

- Ensure that the `MigrateAllExecutionStatus-SquadtoScale.py` script has been modified to include your jira instance specific values, and we are using the correct command-line parameters.
- Python 3.x is required to run this script.


---

## `unitTests_publishResultsZephyrScale_autoCreatedDefect.py`

### Purpose

`unitTests_publishResultsZephyrScale_autoCreatedDefect.py` is a Python script that executes a simple unit tests, if failure Jira defect is created and linked in execution results. Then execution results are published to Zephyr Scale.

### Script Details

- **Execution**: The script runs a python file using 5 input parameters: username, password, projectKey, instance, and test case key (in the unit tests). 

### Usage

To run the `unitTests_publishResultsZephyrScale_autoCreatedDefect.py` script, use the following command: python3 unitTests_publishResultsZephyrScale_autoCreatedDefect.py

### Example

```bash
python3 unitTests_publishResultsZephyrScale_autoCreatedDefect.py
```

### Notes

- Ensure that the `unitTests_publishResultsZephyrScale_autoCreatedDefect.py` script has been modified to include your jira instance specific values, and we are using the correct input parameters.
- Python 3.x is required to run this script.
- The test case key is required to be in the unit tests.

---


## `CreateTestCycle-Excel.py`

### Purpose

`CreateTestCycle-Excel` is a Python script designed to automate the creation of test cases, driven from an excel spreadsheet


### Script Details

- **Execution**: The script runs a python file using four script input parameters: username, password, base url, host.

### Usage

To execute the `CreateTestCycle-Excel` script, navigate to the project directory and use the following command:

```bash
python `CreateTestCycle-Excel.py` 
```

### Example

```bash
python CreateTestCycle-Excel.py 
```

### Notes

- Ensure that the `CreateTestCycle-Excel` script has been modified to include your jira instance specific values, and we are updating the correct objects in the executions.
- Python 3.x is required to run this script.
- inputlfileTestCycle.csv is required to be in the same directory as the script. 

