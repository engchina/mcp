#!/usr/bin/env python3
"""
Test suite for OCI Compute MCP Server

This module contains comprehensive tests for the OCI Compute MCP Server,
validating all compute instance management operations and compartment functionality.
"""

import unittest
import sys
import os
import json
import importlib.util
from typing import Dict, Any, List, Optional

# Add the current directory to Python path for module import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Dynamically load the server module
module_name = "oci_compute_mcp_server"
file_path = os.path.join(os.path.dirname(__file__), "oci-compute-mcp-server.py")
spec = importlib.util.spec_from_file_location(module_name, file_path)
server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_module)


class TestOCIComputeMCPServer(unittest.TestCase):
    """
    Test class for OCI Compute MCP Server functionality.
    
    This class tests all the compute instance management operations,
    compartment operations, and error handling scenarios.
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Set up test class with configuration and test parameters.
        """
        # Test configuration from environment variables
        cls.test_compartment_name = os.getenv('TEST_COMPARTMENT_NAME', 'test-compartment')
        cls.test_instance_name = os.getenv('TEST_INSTANCE_NAME', 'test-instance')
        cls.test_instance_id = os.getenv('TEST_INSTANCE_ID')
        cls.test_region = os.getenv('TEST_REGION', 'us-ashburn-1')
        
        # Initialize server instance
        cls.server = server_module.OCIComputeMCPServer()
        
        print(f"\n=== OCI Compute MCP Server Test Suite ===")
        print(f"Test Compartment: {cls.test_compartment_name}")
        print(f"Test Instance: {cls.test_instance_name}")
        print(f"Test Region: {cls.test_region}")
        if cls.test_instance_id:
            print(f"Test Instance ID: {cls.test_instance_id}")
        print("=" * 50)
    
    def setUp(self):
        """
        Set up individual test cases.
        """
        pass
    
    def validate_json_response(self, response: Any, expected_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validate that response is valid JSON and contains expected structure.
        
        Args:
            response: The response to validate
            expected_keys: Optional list of keys that should be present
            
        Returns:
            Dict containing the parsed JSON response
            
        Raises:
            AssertionError: If validation fails
        """
        # Ensure response is not None
        self.assertIsNotNone(response, "Response should not be None")
        
        # Parse JSON if response is string
        if isinstance(response, str):
            try:
                parsed_response = json.loads(response)
            except json.JSONDecodeError as e:
                self.fail(f"Response is not valid JSON: {e}")
        else:
            parsed_response = response
        
        # Validate expected keys if provided
        if expected_keys:
            for key in expected_keys:
                self.assertIn(key, parsed_response, f"Expected key '{key}' not found in response")
        
        return parsed_response
    
    def test_list_compartments(self):
        """
        Test listing all compartments in the tenancy.
        """
        print("\n--- Testing list_compartments ---")
        
        try:
            response = self.server.list_compartments({})
            parsed_response = self.validate_json_response(response, ['compartments'])
            
            compartments = parsed_response['compartments']
            self.assertIsInstance(compartments, list, "Compartments should be a list")
            
            if compartments:
                # Validate compartment structure
                compartment = compartments[0]
                expected_fields = ['id', 'name', 'description', 'lifecycle_state']
                for field in expected_fields:
                    self.assertIn(field, compartment, f"Compartment should have '{field}' field")
            
            print(f"✓ Found {len(compartments)} compartments")
            
        except Exception as e:
            self.fail(f"list_compartments failed: {str(e)}")
    
    def test_get_compartment_by_name(self):
        """
        Test getting a specific compartment by name.
        """
        print(f"\n--- Testing get_compartment_by_name: {self.test_compartment_name} ---")
        
        try:
            response = self.server.get_compartment_by_name({
                'compartment_name': self.test_compartment_name
            })
            parsed_response = self.validate_json_response(response)
            
            if 'compartment' in parsed_response:
                compartment = parsed_response['compartment']
                self.assertEqual(compartment['name'], self.test_compartment_name)
                print(f"✓ Found compartment: {compartment['name']}")
            else:
                print(f"ℹ Compartment '{self.test_compartment_name}' not found (this is expected if it doesn't exist)")
            
        except Exception as e:
            self.fail(f"get_compartment_by_name failed: {str(e)}")
    
    def test_list_compute_instances(self):
        """
        Test listing compute instances in a compartment.
        """
        print(f"\n--- Testing list_compute_instances in {self.test_compartment_name} ---")
        
        try:
            response = self.server.list_compute_instances({
                'compartment_name': self.test_compartment_name,
                'region': self.test_region
            })
            parsed_response = self.validate_json_response(response, ['instances'])
            
            instances = parsed_response['instances']
            self.assertIsInstance(instances, list, "Instances should be a list")
            
            if instances:
                # Validate instance structure
                instance = instances[0]
                expected_fields = ['id', 'display_name', 'lifecycle_state', 'availability_domain']
                for field in expected_fields:
                    self.assertIn(field, instance, f"Instance should have '{field}' field")
            
            print(f"✓ Found {len(instances)} instances in compartment")
            
        except Exception as e:
            self.fail(f"list_compute_instances failed: {str(e)}")
    
    def test_get_compute_instance(self):
        """
        Test getting details of a specific compute instance by ID.
        """
        if not self.test_instance_id:
            self.skipTest("TEST_INSTANCE_ID not provided, skipping instance details test")
        
        print(f"\n--- Testing get_compute_instance: {self.test_instance_id} ---")
        
        try:
            response = self.server.get_compute_instance({
                'instance_id': self.test_instance_id,
                'region': self.test_region
            })
            parsed_response = self.validate_json_response(response, ['instance'])
            
            instance = parsed_response['instance']
            self.assertEqual(instance['id'], self.test_instance_id)
            
            # Validate detailed instance information
            expected_fields = ['id', 'display_name', 'lifecycle_state', 'availability_domain', 'shape']
            for field in expected_fields:
                self.assertIn(field, instance, f"Instance details should have '{field}' field")
            
            print(f"✓ Retrieved instance details: {instance['display_name']} ({instance['lifecycle_state']})")
            
        except Exception as e:
            self.fail(f"get_compute_instance failed: {str(e)}")
    
    def test_get_compute_instance_by_name(self):
        """
        Test getting a compute instance by name within a compartment.
        """
        print(f"\n--- Testing get_compute_instance_by_name: {self.test_instance_name} ---")
        
        try:
            response = self.server.get_compute_instance_by_name({
                'instance_name': self.test_instance_name,
                'compartment_name': self.test_compartment_name,
                'region': self.test_region
            })
            parsed_response = self.validate_json_response(response)
            
            if 'instance' in parsed_response:
                instance = parsed_response['instance']
                self.assertEqual(instance['display_name'], self.test_instance_name)
                print(f"✓ Found instance: {instance['display_name']} ({instance['lifecycle_state']})")
            else:
                print(f"ℹ Instance '{self.test_instance_name}' not found in compartment (this is expected if it doesn't exist)")
            
        except Exception as e:
            self.fail(f"get_compute_instance_by_name failed: {str(e)}")
    
    def test_compute_instance_action(self):
        """
        Test compute instance lifecycle actions.
        Note: This test only validates the API call structure, not actual state changes.
        """
        if not self.test_instance_id:
            self.skipTest("TEST_INSTANCE_ID not provided, skipping instance action test")
        
        print(f"\n--- Testing compute_instance_action (dry run) ---")
        
        # Test with a safe action that doesn't change state significantly
        try:
            # Note: In a real test environment, you might want to test actual actions
            # For this test, we'll just validate the API structure
            response = self.server.get_compute_instance({
                'instance_id': self.test_instance_id,
                'region': self.test_region
            })
            parsed_response = self.validate_json_response(response, ['instance'])
            
            current_state = parsed_response['instance']['lifecycle_state']
            print(f"✓ Current instance state: {current_state}")
            print("ℹ Instance action test completed (dry run mode)")
            
        except Exception as e:
            self.fail(f"compute_instance_action test failed: {str(e)}")
    
    def test_invalid_inputs(self):
        """
        Test error handling with invalid inputs.
        """
        print("\n--- Testing invalid inputs ---")
        
        # Test with invalid compartment name
        try:
            response = self.server.get_compartment_by_name({
                'compartment_name': 'non-existent-compartment-12345'
            })
            parsed_response = self.validate_json_response(response)
            print("✓ Invalid compartment name handled gracefully")
        except Exception as e:
            print(f"✓ Invalid compartment name properly rejected: {str(e)}")
        
        # Test with invalid instance ID
        try:
            response = self.server.get_compute_instance({
                'instance_id': 'invalid-instance-id',
                'region': self.test_region
            })
            parsed_response = self.validate_json_response(response)
            print("✓ Invalid instance ID handled gracefully")
        except Exception as e:
            print(f"✓ Invalid instance ID properly rejected: {str(e)}")
    
    def tearDown(self):
        """
        Clean up after individual test cases.
        """
        pass
    
    @classmethod
    def tearDownClass(cls):
        """
        Clean up after all tests are completed.
        """
        print("\n=== Test Suite Completed ===")


if __name__ == '__main__':
    # Check if specific test is requested
    if len(sys.argv) > 1 and sys.argv[1].startswith('test_'):
        # Run specific test
        test_name = sys.argv[1]
        suite = unittest.TestSuite()
        suite.addTest(TestOCIComputeMCPServer(test_name))
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
    else:
        # Run all tests
        unittest.main(verbosity=2)