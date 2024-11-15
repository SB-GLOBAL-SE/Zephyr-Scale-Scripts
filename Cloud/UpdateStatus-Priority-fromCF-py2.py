import requests
import sys
import json


# In order to run the script, configure the bearer_token, otherStatuses, and otherPriorities below. Then run the python command with version 2.7 as the interpreter.
# EX: python2.7 UpdateStatus-Priority-fromCF-py2.py <projectKeys to migrate (1 or multiple)>
# EX: python2.7 UpdateStatus-Priority-fromCF-py2.py ZULU
# EX: python2.7 UpdateStatus-Priority-fromCF-py2.py ZULU APPS OPS


#### REPLACE ME WITH ZEPHYR SCALE BEARER TOKEN #######
bearer_token = "<>"

######### REPLACE ME WITH NEW ZEPHYR SCALE TEST CASE STATUSES.  Draft, Depricated and Approved are default values. 
otherStatuses = set(["Review"])

######### REPLACE ME WITH NEW ZEPHYR SCALE PRIORITY STATUSES.  High, Normal, and Low are default values. 
otherPriorities = set(["Critical"])

#Global value, do NOT change! 
base_url = "https://api.zephyrscale.smartbear.com/v2"

#This adds the otherStatuses specified above to the input project, and creates a key value pair mapping of all the available test case statuses, and status ids
def test_case_status(projectkey):

    url = '{}/statuses'.format(base_url)

    params = {
        "statusType": "TEST_CASE",
        "projectKey": projectkey
    }

    headers = {
        'Authorization': 'Bearer {}'.format(bearer_token),
        'Content-Type': 'application/json'
    }

    try:
        # First request to get existing statuses
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            response_data = response.json()
            name_id_kvp = {item['name']: item['id'] for item in response_data['values']}

            #Loop through otherStatuses to create them
            for name in otherStatuses:
                payload = {
                    "projectKey": projectkey,
                    "name": name,
                    "type": "TEST_CASE",
                    "color": "#0052cc"
                }
                
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                
                if response.status_code == 201:
                    new_status = response.json()
                    status_id = new_status.get("id")
                    # Append the new status to name_id_kvp
                    name_id_kvp[name] = status_id 
                # Handle the case where the status already exists
                elif response.status_code == 400 and "A status of this type with this name already exists" in response.json().get("message", ""):
                    print("Status value already exists: {}".format(name))
                    # Do nothing, as we don't want to log this specific error
                else:
                    print("Failed to create status: {}".format(name))
                    print("Error: Received status code {}".format(response.status_code))
                    print(response.content.decode())
            return name_id_kvp
        else:
            print("Error: Received status code {}".format(response.status_code))
            print(response.content.decode())
    except requests.exceptions.RequestException as e:
        print("Request failed: {}".format(e))

#This adds the otherPriority specified above to the input project, and creates a key value pair mapping of all the available test case priorities, and priority ids
def test_case_priority(projectkey):


    url = '{}/priorities?projectKey={}'.format(base_url, projectkey)

    headers = {
        'Authorization': 'Bearer {}'.format(bearer_token),
        'Content-Type': 'application/json'
    }

    priority_id_kvp = {}

    try:
        # First request to get existing priorities
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            response_data = response.json()
            priority_id_kvp = {item['name']: item['id'] for item in response_data['values']}

            #Loop through otherPriorities to create them
            for name in otherPriorities:
                payload = {
                    "projectKey": projectkey,
                    "name": name,
                    "color": "#EC3536"
                }
                
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                
                if response.status_code == 201:
                    new_priority = response.json()
                    priority_id = new_priority.get("id")
                    # Append the new priority to priority_id_kvp
                    priority_id_kvp[name] = priority_id
                
                # Handle the case where the priority already exists
                elif response.status_code == 400 and "A priority with this name already exists" in response.json().get("message", ""):
                    # Do nothing, as we don't want to log this specific error
                    print("Priority value already exists: {}".format(name))

                else:
                    print("Failed to create priority: {}".format(name))
                    print("Error: Received status code {}".format(response.status_code))
                    print(response.content.decode())
            return priority_id_kvp
        else:
            print("Failed to retrieve existing priorities")
            print("Error: Received status code {}".format(response.status_code))
            print(response.content.decode())

    except requests.exceptions.RequestException as e:
        print("Request failed: {}".format(e))

#This moves the custom field values of squadStatus and squadPriority field to the default test case status, and priority, if none is available, it will use a defaut value.
def test_case(priority_id_kvp, name_id_kvp, projectkey):

    #Max results per iteration. It will still update all test cases within a project, just via batches.
    max_results = 100
    start_at = 0

    headers = {
        'Authorization': 'Bearer {}'.format(bearer_token),
        'Content-Type': 'application/json'
    }

    while True:
        url = '{}/testcases?projectKey={}&maxResults={}&startAt={}'.format(base_url, projectkey, max_results, start_at)
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                test_cases = response.json()

                # Check if there are test cases in the response
                if 'values' not in test_cases or not test_cases['values']:
                    print("No more test cases found.")
                    break

                # Loop through each test case in 'values'
                for test_case in test_cases['values']:
                    # GET Test case Key, ID, Name, Project ID and Project Link
                    test_case_key = test_case.get('key')
                    test_case_id = test_case.get('id')
                    test_case_name = test_case.get('name')
                    project_id = test_case.get('project', {}).get('id')
                    project_self = test_case.get('project', {}).get('self')

                    #GET folders
                    og_folder = test_case.get('folder') or {}
                    og_folder_id = og_folder.get("id")

                    #if Folder is None logic 
                    if og_folder_id is not None:
                        og_folder_id = int(og_folder_id)
                        og_folder_link = og_folder.get("self", None)
                        
                    else:
                        og_folder_id = None
                        og_folder_link = None

                    # GET default Scale priority, status, objective, precondition, component and labels owner values
                    og_squad_priority = test_case.get('priority', {})
                    og_squad_status = test_case.get('status', {})
                    og_objective = test_case.get('objective') or None
                    og_precondition = test_case.get('precondition') or None
                    og_labels = test_case.get('labels') or None
                    og_owner = test_case.get('owner') or None
                    og_component = test_case.get("component", {}) 

                    #If component does not equal None, get the values, else assign it to None
                    if og_component != None:
                        og_component_id = og_component.get("id")
                        og_component_link = og_component.get("self")
                    else: 
                        og_component_id = None
                        og_component_link = None

                    #If owner does not equal None, get the values, else assign it to none
                    if og_owner != None:
                        og_owner_id = og_owner.get("accountId")
                        og_owner_link=og_owner.get("self")
                    else:
                        og_owner_id = None
                        og_owner_link = None
 

                    # GET CF field values, if there is no value, replace with a default value, in this case None
                    cf_squad_status = test_case.get('customFields', {}).get('squadStatus') or None
                    cf_squad_priority = test_case.get('customFields', {}).get('squadPriority') or None
                    squad_components = test_case.get('customFields', {}).get('components') or None
                    squad_test_type_detail = test_case.get('customFields', {}).get('Test Type Detail') or None
                    squad_Automation_Status = test_case.get('customFields', {}).get('Automation Status') or None
                    squad_Test_Case_Coverage = test_case.get('customFields', {}).get('Test Case Coverage') or None
                    squad_Test_Type = test_case.get('customFields', {}).get('Test Type') or None
                    squad_module_library = test_case.get('customFields', {}).get('Module Library') or None
                    squad_test_CI = test_case.get('customFields', {}).get('Test CI') or None
                    squad_interface_touch_point = test_case.get('customFields', {}).get('Interface Touch Point/s') or None
                    squad_test_automation_tool = test_case.get('customFields', {}).get('Test Automation Tool') or None
                    squad_test_case_classification = test_case.get('customFields', {}).get('Test Case Classification') or None

                    # Extract original status ID and link 
                    og_Status_Id = og_squad_status.get("id")
                    og_Status_Link = og_squad_status.get('self')


                    # Status mapping for null values and values outside of the defined scope
                    status_mapping = {
                        "Elaborated": "Draft",
                        "In Progress": "Draft",
                        "Review": "Review",
                        "Test": "Approved",
                        "Done": "Approved",
                        "Abandoned": "Deprecated",
                        None: "Draft"
                    }


                    # Handle specific edge cases for Squad Status being None and default Status is not Draft
                    if name_id_kvp.get('Draft') != og_Status_Id and cf_squad_status is None:
                        newStatus_Id = og_Status_Id
                        newStatus_Link = og_Status_Link
                        print("Status is not Draft, and squadStatus is None. Retaining original status.")
                    else:
                        # Extract status and priority IDs based on custom mappings, default to "Draft" if cf_squad_status not found in mapping
                        squad_status = status_mapping.get(cf_squad_status, "Draft")
                        if squad_status in name_id_kvp:
                            newStatus_Id = name_id_kvp[squad_status]
                            newStatus_Link = '{}/statuses/{}'.format(base_url, newStatus_Id)
                        else:
                            # Fallback for undefined scenarios, assign to "Draft"
                            newStatus_Id = name_id_kvp["Draft"]
                            newStatus_Link = '{}/statuses/{}'.format(base_url, newStatus_Id)
                            print("Test Case has changed squadStatus, but not  Status.")


                    # Squad priority mapping
                    priority_mapping = {
                        "Medium": "Normal",
                        "Low": "Low",
                        "High": "High",
                        "Blocker": "Critical",
                        "Critical": "Critical",
                        None: "Normal"
                    }

                    og_priority_Id = og_squad_priority.get("id")
                    og_priority_Link = og_squad_priority.get('self')

                    # Handle specific edge cases for Squad priority being None and default priority is not normal
                    if priority_id_kvp.get('Normal') != og_priority_Id and cf_squad_priority is None:
                        newPriority_Id = og_priority_Id
                        newPriority_Link = og_priority_Link
                        print("Priority is not Normal, and squadPriority is None. Retaining original priority.")
                    else:
                        # Extract priority based on custom mappings, default to "Normal" if cf_squad_priority not found in mapping
                        squad_priority = priority_mapping.get(cf_squad_priority, "Normal")  
                        if squad_priority in priority_id_kvp:
                            newPriority_Id = priority_id_kvp[squad_priority]
                            newPriority_Link = '{}/priorities/{}'.format(base_url, newPriority_Id)
                        else:
                            # Fallback for undefined scenarios, assign to "Normal"
                            newPriority_Id = priority_id_kvp["Normal"]
                            newPriority_Link = '{}/priorities/{}'.format(base_url, newPriority_Id)
                            print("Test Case has changed squadPriority, but not Priority.")


                    
                    if not test_case_key:
                        print("Key not found for a test case. Skipping.")
                        continue

                    update_url = '{}/testcases/{}'.format(base_url, test_case_key)
                    
                    payload = {
                        "id": test_case_id,
                        "key": test_case_key,
                        "name": test_case_name,
                        "project": {
                            "id": project_id,
                            "self": project_self
                        },
                        "precondition": og_precondition,
                        "objective": og_objective,
                        "labels":og_labels,
                        "component": {
                            "id": og_component_id,
                            "self": og_component_link
                        },
                        "priority": {
                            "id": newPriority_Id,
                            "self": newPriority_Link
                        },
                        "status": {
                            "id": newStatus_Id,
                            "self": newStatus_Link
                        },
                        "folder": {
                            "id": og_folder_id,
                            "self": og_folder_link
                        },
                        "owner": {
                            "self": og_owner_link,
                            "accountId": og_owner_id
                        },
                        "customFields": {
                            "squadStatus": cf_squad_status,
                            "squadPriority": cf_squad_priority,
                            "components": squad_components,
                            "Test Type Detail": squad_test_type_detail,
                            "Automation Status": squad_Automation_Status,
                            "Test Case Coverage": squad_Test_Case_Coverage,
                            "Test Type": squad_Test_Type, 
                            "Module Library": squad_module_library,
                            "Test CI": squad_test_CI,
                            "Interface Touch Point/s": squad_interface_touch_point,
                            "Test Automation Tool": squad_test_automation_tool,
                            "Test Case Classification": squad_test_case_classification
                    }
                    }

                    print("Updating test case: {}".format(test_case_key))

                    #if no folder, remove it from payload
                    if og_folder_id is None:
                        payload.pop("folder", None)

                    #if no owner, remove it from payload
                    if og_owner is None:
                        payload.pop("owner", None)

                    #if no component, remove it from payload
                    if og_component is None:
                        payload.pop("component", None)


                    # Send the PUT request to update the test case
                    try:
                        response = requests.put(update_url, headers=headers, data=json.dumps(payload))

                        if response.status_code == 200:
                            print("Successfully updated test case: {}".format(test_case_key))
                        else:
                            print("Error updating test case {}: Received status code {}".format(test_case_key, response.status_code))
                            print(response.content.decode())
                    except requests.exceptions.RequestException as e:
                        print("Request failed for test case {}: {}".format(test_case_key, e))
                
                # Move to the next batch of test cases
                start_at += max_results
            else:
                print("Error: Received status code {}".format(response.status_code))
                print(response.content.decode())
                break
        except requests.exceptions.RequestException as e:
            print("Request failed: {}".format(e))
            break

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python2.7 python.py <projectKey1> <projectKey2> ...")
        sys.exit(1)

    project_keys = sys.argv[1:]

    for project_key in project_keys:
        print("Starting migration for project key: {}".format(project_key))
        priority_id_kvp = test_case_priority(project_key)
        name_id_kvp = test_case_status(project_key)
        
        if priority_id_kvp and name_id_kvp:
            test_case(priority_id_kvp, name_id_kvp, project_key)
        else:
            print("Skipping project key: {} due to missing data.".format(project_key))
