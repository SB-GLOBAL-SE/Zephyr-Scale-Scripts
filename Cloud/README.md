# Script Documentation

## Table of Contents

1. [Overview](#overview)
2. [`CreateCustomStatus-Priority.py`](#CreateCustomStatus-Prioritypy)
   - [Purpose](#purpose)
   - [Script Details](#script-details)
   - [Usage](#usage)
   - [Example](#example)
3. [`Custom-Fields2.7.py`](#`BulkUpdateTestExecution-Excelpy)
   - [Purpose](#purpose)
   - [Script Details](#script-details)
   - [Usage](#usage)
   - [Example](#example)
4. [`Custom-Status-Priority-Fields2.7.py`](#Custom-Status-Priority-Fields2.7py)
   - [Purpose](#purpose)
   - [Script Details](#script-details)
   - [Usage](#usage)
   - [Example](#example)
5. ['## `Get_Execution_and_Step_Info.py`](#Get_Execution_and_Step_Infopy)
   - [Purpose](#purpose)
   - [Script Details](#script-details)
   - [Usage](#usage)
   - [Example](#example)

   ---

## Overview

This project contains a number of key scripts. Below are detailed explanations of each script, including their purposes, usage, and example commands.

---

## `CreateCustomStatus-Priority.py`

### Purpose

`CreateCustomStatus-Priority.py` is a Python script designed to automate creation of two seperate process: 
1. Create custom test case statuses.
2. Create custom test case priorities.

### Script Details

- **Execution**: The script runs a python file using one script input parameters: project key.

### Usage

To execute the `CreateCustomStatus-Priority.py` script, navigate to the project directory and use the following command:

```bash
python  CreateCustomStatuses.py <projectKeys to migrate (1 or multiple)> 
```

### Example

```bash
python  CreateCustomStatus-Priority.py Zulu
python  CreateCustomStatus-Priority.py Zulu KILO
```

### Notes

- Ensure that the `CreateCustomStatus-Priority.py` script has been modified to include your jira instance specific values, and we are updating the correct objects in the configuration.
- Python 2.7 is used to run this script.

---

## `Custom-Fields2.7.py`

### Purpose

`Custom-Fields2.7.py` is a Python script designed to create custom fields.  


### Script Details

- **Execution**: The script runs a python file using one script input parameter: project ID.

### Usage

To execute the `Custom-Fields2.7.py` script, navigate to the project directory and use the following command:

```bash
python Custom-Fields2.7.py  <projectID> 
```

### Example

```bash
python Custom-Fields2.7.py  10169
```

### Notes

- This is a private API. The private api can change without notifying anyone so the script may break.
- Ensure that the `Custom-Fields2.7.py` script has been modified to include your jira instance specific values, and we are updating the correct objects in the configuration.
- Python 2.7 is used to run this script.
- `custom_fields.json` is required to be in the same directory as the script.

---

## `Custom-Status-Priority-Fields2.7.py`

### Purpose

`Custom-Status-Priority-Fields2.7.py` is a Python script designed to automate the creation of three seperate process: 
1. Create custom test case statuses.
2. Create custom test case priorities.
3. Create custom test case fields. 


### Script Details

- **Execution**: The script runs a python file using two script input parameters: project key, and project id.

### Usage

To execute the `Custom-Status-Priority-Fields2.7.py` script, navigate to the project directory and use the following command:

```bash
python Custom-Status-Priority-Fields2.7.py <projectKey> <projectID> 
```

### Example

```bash
python Custom-Status-Priority-Fields2.7.py ZULU 10169
```

### Notes

- Ensure that the `Custom-Status-Priority-Fields2.7.py` script has been modified to include your jira instance specific values, and we are updating the correct objects in the configuration.
- Python 2.7 is used to run this script.


---
## `Get_Execution_and_Step_Info.py`

### Purpose

`Get_Execution_and_Step_Info.py` is a Python script designed to automate the retrieval of test executions and dynamically resolve human-readable status names for each step using the Zephyr Scale Cloud API.

The script performs the following:
1. Retrieves all test executions for a given test case key.
2. Retrieves all test steps for each execution.
3. Follows the `status.self` URL for each step to fetch and print the corresponding status name.

### Script Details

- **Execution**: The script runs a python file using two hardcoded parameters: bearer token and test case key.

### Usage

To execute the `Get_Execution_and_Step_Info.py` script, navigate to the project directory and use the following command:

```bash
python Get_Execution_and_Step_Info.py
```

### Example

```bash
python Get_Execution_and_Step_Info.py
```

### Notes

- Ensure that the `Get_Execution_and_Step_Info.py` script has been modified to include your Zephyr Scale API `BEARER_TOKEN` and `TEST_CASE_KEY`.
- The script dynamically sends a GET request to each step's `status.self` URL to retrieve the final status label (e.g. "Pass", "Fail", "In Progress").
- Python 3.x is required to run this script.

---
