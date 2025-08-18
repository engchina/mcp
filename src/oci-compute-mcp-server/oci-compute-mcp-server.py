"""
Copyright (c) 2025, Oracle and/or its affiliates.
Licensed under the Universal Permissive License v1.0 as shown at http://oss.oracle.com/licenses/upl.

OCI Compute Instance MCP Server
- List compute instances in compartments
- Get detailed information about specific instances
- Perform instance lifecycle actions (START, STOP, RESET)
"""

import os
import json
import oci
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP(
    "oci-compute",
    host="0.0.0.0",
    port=8000,
)

# Get OCI configuration
profile_name = os.getenv("PROFILE_NAME", "DEFAULT")
config = oci.config.from_file(profile_name=profile_name)

# Get tenancy ID and region ID
tenancy_id = os.getenv("TENANCY_ID_OVERRIDE", config['tenancy'])
region_id = os.getenv("REGION_ID_OVERRIDE", config['region'])

# Initialize OCI clients with region override
regional_config = config.copy()
regional_config['region'] = region_id
identity_client = oci.identity.IdentityClient(regional_config)
compute_client = oci.core.ComputeClient(regional_config)
search_client = oci.resource_search.ResourceSearchClient(regional_config)


def get_all_compartments():
    """Internal function to get all compartments with pagination support"""
    all_compartments = []
    
    # Use pagination to get all compartments
    page = None
    while True:
        if page:
            response = identity_client.list_compartments(
                compartment_id=tenancy_id,
                compartment_id_in_subtree=True,
                access_level="ACCESSIBLE",
                lifecycle_state="ACTIVE",
                page=page
            )
        else:
            response = identity_client.list_compartments(
                compartment_id=tenancy_id,
                compartment_id_in_subtree=True,
                access_level="ACCESSIBLE",
                lifecycle_state="ACTIVE"
            )
        
        all_compartments.extend(response.data)
        
        # Check if there are more pages
        if not hasattr(response, 'next_page') or not response.next_page:
            break
        page = response.next_page
    
    # Add root compartment
    all_compartments.append(identity_client.get_compartment(compartment_id=tenancy_id).data)
    
    return all_compartments


def get_compartment_by_name(compartment_name: str):
    """Internal function to get compartment by name"""
    compartments = get_all_compartments()

    # Search for the compartment by name
    for compartment in compartments:
        if compartment.name.lower() == compartment_name.lower():
            return compartment

    return None


@mcp.tool()
def list_compartments() -> str:
    """List all compartments in the tenancy with pagination support"""
    try:
        compartments = get_all_compartments()
        
        result = []
        for comp in compartments:
            result.append({
                "id": comp.id,
                "name": comp.name,
                "description": comp.description,
                "lifecycle_state": comp.lifecycle_state,
                "time_created": str(comp.time_created)
            })
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to list compartments: {str(e)}"})


@mcp.tool()
def list_compute_instances(compartment_name: str, region: str = None) -> str:
    """List all compute instances in a given compartment name"""
    try:

        compartment = get_compartment_by_name(compartment_name)
        if not compartment:
            return json.dumps({
                "error": f"Compartment '{compartment_name}' not found. Use list_compartments() to see available compartments."
            })

        # Use regional client if region is specified
        if region:
            temp_config = config.copy()
            temp_config["region"] = region
            regional_compute_client = oci.core.ComputeClient(temp_config)
            instances = regional_compute_client.list_instances(compartment_id=compartment.id).data
        else:
            instances = compute_client.list_instances(compartment_id=compartment.id).data
        
        result = []
        for instance in instances:
            result.append({
                "id": instance.id,
                "display_name": instance.display_name,
                "lifecycle_state": instance.lifecycle_state,
                "availability_domain": instance.availability_domain,
                "shape": instance.shape,
                "time_created": str(instance.time_created),
                "compartment_id": instance.compartment_id
            })
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to list compute instances: {str(e)}"})


@mcp.tool()
def get_compute_instance(instance_id: str, region: str = None) -> str:
    """Get detailed information about a specific compute instance by ID"""
    try:
        # Use regional client if region is specified
        if region:
            temp_config = config.copy()
            temp_config["region"] = region
            regional_compute_client = oci.core.ComputeClient(temp_config)
            instance = regional_compute_client.get_instance(instance_id).data
        else:
            instance = compute_client.get_instance(instance_id).data
        
        result = {
            "id": instance.id,
            "display_name": instance.display_name,
            "lifecycle_state": instance.lifecycle_state,
            "availability_domain": instance.availability_domain,
            "shape": instance.shape,
            "shape_config": {
                "ocpus": instance.shape_config.ocpus if instance.shape_config else None,
                "memory_in_gbs": instance.shape_config.memory_in_gbs if instance.shape_config else None
            } if instance.shape_config else None,
            "time_created": str(instance.time_created),
            "compartment_id": instance.compartment_id,
            "region": instance.region,
            "fault_domain": instance.fault_domain,
            "image_id": instance.image_id,
            "launch_mode": instance.launch_mode,
            "launch_options": {
                "boot_volume_type": instance.launch_options.boot_volume_type if instance.launch_options else None,
                "firmware": instance.launch_options.firmware if instance.launch_options else None,
                "network_type": instance.launch_options.network_type if instance.launch_options else None
            } if instance.launch_options else None,
            "metadata": instance.metadata,
            "extended_metadata": instance.extended_metadata
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to get compute instance: {str(e)}"})


@mcp.tool()
def get_compute_instance_by_name(instance_name: str, compartment_name: str, region: str = None) -> str:
    """Get compute instance by display name within a specific compartment"""
    try:
        compartment = get_compartment_by_name(compartment_name)
        if not compartment:
            return json.dumps({
                "error": f"Compartment '{compartment_name}' not found. Use list_compartments() to see available compartments."
            })
        
        # Use regional client if region is specified
        if region:
            temp_config = config.copy()
            temp_config["region"] = region
            regional_compute_client = oci.core.ComputeClient(temp_config)
            instances = regional_compute_client.list_instances(compartment_id=compartment.id).data
        else:
            instances = compute_client.list_instances(compartment_id=compartment.id).data
        
        for instance in instances:
            if instance.display_name.lower() == instance_name.lower():
                return get_compute_instance(instance.id, region)
        
        return json.dumps({
            "error": f"Instance '{instance_name}' not found in compartment '{compartment_name}'"
        })
            
    except Exception as e:
        return json.dumps({"error": f"Failed to get compute instance by name: {str(e)}"})


@mcp.tool()
def compute_instance_action(instance_id: str, action: str, region: str = None) -> str:
    """Perform lifecycle action on a compute instance. Actions: START, STOP, RESET"""
    try:
        # Extract region from instance_id if not provided
        if not region:
            try:
                region = instance_id.split('.')[3]
            except IndexError:
                return json.dumps({"error": "Invalid instance_id format. Cannot extract region."})

        # Create a regional compute client
        temp_config = config.copy()
        temp_config["region"] = region
        regional_compute_client = oci.core.ComputeClient(temp_config)

        # Validate action
        valid_actions = ["START", "STOP", "RESET"]
        action = action.upper()
        if action not in valid_actions:
            return json.dumps({
                "error": f"Invalid action '{action}'. Valid actions are: {', '.join(valid_actions)}"
            })
        
        # Get current instance state
        instance = regional_compute_client.get_instance(instance_id).data
        current_state = instance.lifecycle_state
        
        result = {
            "instance_id": instance_id,
            "instance_name": instance.display_name,
            "action_requested": action,
            "previous_state": current_state
        }
        
        # Perform the action
        if action == "START":
            if current_state == "STOPPED":
                response = regional_compute_client.instance_action(instance_id, "START")
                result["status"] = "Action initiated"
                result["message"] = "Instance start initiated"
            else:
                result["status"] = "No action needed"
                result["message"] = f"Instance is already in state: {current_state}"
                
        elif action == "STOP":
            if current_state == "RUNNING":
                response = regional_compute_client.instance_action(instance_id, "STOP")
                result["status"] = "Action initiated"
                result["message"] = "Instance stop initiated"
            else:
                result["status"] = "No action needed"
                result["message"] = f"Instance is already in state: {current_state}"
                
        elif action == "RESET":
            if current_state in ["RUNNING", "STOPPED"]:
                # Reset = Stop + Start
                if current_state == "RUNNING":
                    regional_compute_client.instance_action(instance_id, "STOP")
                    result["message"] = "Instance reset initiated (stop then start)"
                else:
                    result["message"] = "Instance start initiated (was already stopped)"
                
                # Note: In practice, you might want to wait for the stop to complete
                # before starting, but for this example we'll just initiate the start
                regional_compute_client.instance_action(instance_id, "START")
                result["status"] = "Action initiated"
            else:
                result["status"] = "Cannot reset"
                result["message"] = f"Cannot reset instance in state: {current_state}"
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to perform instance action: {str(e)}"})


if __name__ == "__main__":
    # mcp.run(transport="stdio")
    mcp.run(transport="streamable-http")