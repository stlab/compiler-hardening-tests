#!/usr/bin/env python3
"""
Analyze diagnostics.json for inconsistencies between parent flags and their sub-flags.

Performs TRANSITIVE analysis using the implies_transitive field.

Identifies cases where:
0. Parent flag has some_default=true but has NO sub-flags at all
1. Parent flag has some_default=true but none of its transitive sub-flags have is_default=true
2. Parent flag has some_default=false but at least one transitive sub-flag has is_default=true
"""

import json
from typing import Dict, List, Tuple

def load_diagnostics(filepath: str) -> Dict:
    """Load the diagnostics JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_inconsistencies(data: Dict) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
    Check for inconsistencies between parent flags and their sub-flags (transitive).
    
    Uses implies_transitive to check the full transitive closure of sub-flags.
    
    Returns:
        Tuple of (type1_issues, type2_issues, type0_issues)
        - type0_issues: Parent has some_default=true but has NO sub-flags at all
        - type1_issues: Parent has some_default=true but no transitive sub-flags have is_default=true
        - type2_issues: Parent has some_default=false but at least one transitive sub-flag has is_default=true
    """
    flags = data['flags']
    type0_issues = []
    type1_issues = []
    type2_issues = []
    
    for flag_name, flag_data in flags.items():
        implies = flag_data.get('implies', [])
        implies_transitive = flag_data.get('implies_transitive', [])
        parent_some_default = flag_data.get('some_default', False)
        
        # Type 0: Parent says some_default=true but has NO sub-flags at all
        if parent_some_default and not implies:
            type0_issues.append({
                'flag': flag_name,
                'parent_some_default': parent_some_default,
                'parent_is_default': flag_data.get('is_default', False),
                'has_implies': False,
                'has_implies_transitive': bool(implies_transitive)
            })
            continue
        
        # Only check remaining types for flags that have sub-flags
        if not implies:
            continue
        
        parent_some_default = flag_data.get('some_default', False)
        
        # Check each TRANSITIVE sub-flag's is_default status
        transitive_subflag_defaults = []
        for subflag_name in implies_transitive:
            if subflag_name in flags:
                subflag_is_default = flags[subflag_name].get('is_default', False)
                transitive_subflag_defaults.append({
                    'name': subflag_name,
                    'is_default': subflag_is_default
                })
            else:
                # Sub-flag not found in the data
                transitive_subflag_defaults.append({
                    'name': subflag_name,
                    'is_default': None,
                    'missing': True
                })
        
        # Also track direct implies for reporting
        direct_subflag_defaults = []
        for subflag_name in implies:
            if subflag_name in flags:
                direct_subflag_defaults.append({
                    'name': subflag_name,
                    'is_default': flags[subflag_name].get('is_default', False),
                    'some_default': flags[subflag_name].get('some_default', False)
                })
            else:
                direct_subflag_defaults.append({
                    'name': subflag_name,
                    'is_default': None,
                    'some_default': None,
                    'missing': True
                })
        
        any_transitive_subflag_default = any(sf['is_default'] for sf in transitive_subflag_defaults if sf['is_default'] is not None)
        all_transitive_subflags_non_default = all(not sf['is_default'] for sf in transitive_subflag_defaults if sf['is_default'] is not None)
        
        # Type 1: Parent says some_default=true but no transitive sub-flags are enabled by default
        if parent_some_default and all_transitive_subflags_non_default:
            # Find which transitive sub-flags are enabled by default for detailed reporting
            enabled_by_default = [sf for sf in transitive_subflag_defaults if sf.get('is_default')]
            
            type1_issues.append({
                'flag': flag_name,
                'parent_some_default': parent_some_default,
                'parent_is_default': flag_data.get('is_default', False),
                'direct_subflags': direct_subflag_defaults,
                'transitive_count': len(implies_transitive),
                'enabled_by_default_count': len(enabled_by_default)
            })
        
        # Type 2: Parent says some_default=false but at least one transitive sub-flag is enabled by default
        if not parent_some_default and any_transitive_subflag_default:
            # Find which transitive sub-flags are enabled by default
            enabled_by_default = [sf for sf in transitive_subflag_defaults if sf.get('is_default')]
            
            type2_issues.append({
                'flag': flag_name,
                'parent_some_default': parent_some_default,
                'parent_is_default': flag_data.get('is_default', False),
                'direct_subflags': direct_subflag_defaults,
                'transitive_count': len(implies_transitive),
                'enabled_by_default': enabled_by_default,
                'enabled_by_default_count': len(enabled_by_default)
            })
    
    return type0_issues, type1_issues, type2_issues

def print_report(type0_issues: List[Dict], type1_issues: List[Dict], type2_issues: List[Dict]):
    """Print a formatted report of the issues found."""
    print("=" * 80)
    print("INCONSISTENCY ANALYSIS REPORT (TRANSITIVE)")
    print("=" * 80)
    print()
    
    print(f"Total Type 0 issues: {len(type0_issues)}")
    print(f"Total Type 1 issues: {len(type1_issues)}")
    print(f"Total Type 2 issues: {len(type2_issues)}")
    print()
    
    if type0_issues:
        print("=" * 80)
        print("TYPE 0: Parent has some_default=true but has NO sub-flags at all")
        print("=" * 80)
        print()
        
        for i, issue in enumerate(type0_issues, 1):
            print(f"{i}. Flag: {issue['flag']}")
            print(f"   Parent some_default: {issue['parent_some_default']}")
            print(f"   Parent is_default: {issue['parent_is_default']}")
            print(f"   Has implies: {issue['has_implies']}")
            print(f"   Has implies_transitive: {issue['has_implies_transitive']}")
            print()
    
    if type1_issues:
        print("=" * 80)
        print("TYPE 1: Parent has some_default=true but NO transitive sub-flags")
        print("        have is_default=true")
        print("=" * 80)
        print()
        
        for i, issue in enumerate(type1_issues, 1):
            print(f"{i}. Flag: {issue['flag']}")
            print(f"   Parent some_default: {issue['parent_some_default']}")
            print(f"   Parent is_default: {issue['parent_is_default']}")
            print(f"   Transitive sub-flags: {issue['transitive_count']}")
            print(f"   Enabled by default (transitive): {issue['enabled_by_default_count']}")
            print(f"   Direct sub-flags ({len(issue['direct_subflags'])}):")
            for sf in issue['direct_subflags']:
                if sf.get('missing'):
                    print(f"      - {sf['name']}: [MISSING FROM DATA]")
                else:
                    some_marker = " (some_default=true)" if sf.get('some_default') else ""
                    print(f"      - {sf['name']}: is_default={sf['is_default']}{some_marker}")
            print()
    
    if type2_issues:
        print("=" * 80)
        print("TYPE 2: Parent has some_default=false but at least one transitive")
        print("        sub-flag has is_default=true")
        print("=" * 80)
        print()
        
        for i, issue in enumerate(type2_issues, 1):
            print(f"{i}. Flag: {issue['flag']}")
            print(f"   Parent some_default: {issue['parent_some_default']}")
            print(f"   Parent is_default: {issue['parent_is_default']}")
            print(f"   Transitive sub-flags: {issue['transitive_count']}")
            print(f"   Enabled by default (transitive): {issue['enabled_by_default_count']}")
            print(f"   Direct sub-flags ({len(issue['direct_subflags'])}):")
            for sf in issue['direct_subflags']:
                if sf.get('missing'):
                    print(f"      - {sf['name']}: [MISSING FROM DATA]")
                else:
                    some_marker = " (some_default=true)" if sf.get('some_default') else ""
                    print(f"      - {sf['name']}: is_default={sf['is_default']}{some_marker}")
            
            # Show some examples of flags that are enabled by default
            if issue['enabled_by_default']:
                print(f"   Examples of transitive sub-flags enabled by default (showing up to 10):")
                for sf in issue['enabled_by_default'][:10]:
                    if not sf.get('missing'):
                        print(f"      - {sf['name']}")
                if len(issue['enabled_by_default']) > 10:
                    print(f"      ... and {len(issue['enabled_by_default']) - 10} more")
            print()
    
    if not type0_issues and not type1_issues and not type2_issues:
        print("No inconsistencies found!")

def main():
    filepath = 'tools/diagnostic-flags/diagnostics.json'
    
    print("Loading diagnostics.json...")
    data = load_diagnostics(filepath)
    print(f"Loaded {data.get('flag_count', 'unknown')} flags")
    print()
    
    print("Analyzing for inconsistencies...")
    type0_issues, type1_issues, type2_issues = check_inconsistencies(data)
    print()
    
    print_report(type0_issues, type1_issues, type2_issues)

if __name__ == '__main__':
    main()
