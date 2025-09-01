#!/usr/bin/env python3
"""
Test script to verify max_results functionality in PACS queries
"""

import requests
import json
import time

def test_max_results():
    """Test PACS query with different max_results values"""
    
    base_url = "http://localhost:5055"
    
    # Test different max_results values
    test_limits = [1, 3, 5, 10, 25]
    
    print("Testing PACS query max_results functionality...")
    print("=" * 50)
    
    for limit in test_limits:
        print(f"\nTesting with max_results = {limit}")
        
        # Prepare query data
        query_data = {
            "pacs_config_id": None,  # Use default PACS
            "max_results": limit,
            "patient_name": "",  # Search all patients
            "patient_id": "",
            "accession_number": "",
            "study_uid": "",
            "series_uid": "",
            "days_ago": 0
        }
        
        try:
            # Send query to PACS
            response = requests.post(
                f"{base_url}/api/pacs/query",
                json=query_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data['success']:
                    results = data['results']
                    query_info = data['query_info']
                    
                    print(f"  Requested limit: {limit}")
                    print(f"  Actual results returned: {len(results)}")
                    print(f"  Max results requested: {query_info.get('max_results_requested', 'N/A')}")
                    print(f"  Total results found: {query_info.get('total_results', 'N/A')}")
                    
                    # Check if limit is working
                    if len(results) <= limit:
                        print(f"  ✓ Limit working correctly")
                    else:
                        print(f"  ✗ Limit not working - returned {len(results)} > {limit}")
                    
                    # Show first few results
                    if results:
                        print(f"  Sample results:")
                        for i, result in enumerate(results[:3]):
                            print(f"    {i+1}. {result.get('patient_name', 'N/A')} - {result.get('accession_number', 'N/A')}")
                        if len(results) > 3:
                            print(f"    ... and {len(results) - 3} more")
                else:
                    print(f"  ✗ Query failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"  ✗ HTTP error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Request failed: {e}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        # Small delay between tests
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("Max results testing completed!")

if __name__ == "__main__":
    test_max_results()
