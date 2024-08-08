# Script Documentation

## Table of Contents

1. [Overview](#overview)
2. [`BulkUpdateTE.py`](#BulkUpdateTEpy)
   - [Purpose](#purpose)
   - [Script Details](#script-details)
   - [Usage](#usage)
   - [Example](#example)
3. [`GetAllAssignableUsers.py`](#GetAllAssignableUserspy)
   - [Purpose](#purpose-1)
   - [Script Details](#script-details-1)
   - [Usage](#usage-1)
   - [Example](#example-1)

---

## Overview

This project contains two key scripts: `BulkUpdateTE.py` and `GetAllAssignableUsers.py`. Below are detailed explanations of each script, including their purposes, usage, and example commands.

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


