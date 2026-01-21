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
from typing import Dict, List, Tuple, Set
import re

def load_diagnostics(filepath: str) -> Dict:
    """Load the diagnostics JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def flag_to_url(flag_name: str) -> str:
    """
    Convert a flag name to its documentation URL.
    
    Args:
        flag_name: The flag name (e.g., "-Wdynamic-exception-spec" or "-Wc++14-compat")
    
    Returns:
        Full URL to the Clang diagnostics documentation for this flag
    """
    # Base URL for Clang diagnostics reference
    base_url = "https://clang.llvm.org/docs/DiagnosticsReference.html"
    
    # Convert flag name to URL fragment
    # Remove leading "-", replace "++" with "-", then lowercase
    # Example: "-Wc++14-compat" -> "wc-14-compat"
    # Handle special case: if replacing ++ with - creates --, collapse to single -
    fragment = flag_name.lstrip('-').replace('++', '-').replace('--', '-').lower()
    
    return f"{base_url}#{fragment}"

def flag_link(flag_name: str) -> str:
    """Create a markdown link for a flag."""
    return f"[`{flag_name}`]({flag_to_url(flag_name)})"

def check_inconsistencies(data: Dict) -> Tuple[List[Dict], List[Dict], List[Dict], List[Dict]]:
    """
    Check for inconsistencies between parent flags and their sub-flags (transitive).
    
    Uses implies_transitive to check the full transitive closure of sub-flags.
    
    Returns:
        Tuple of (type0_issues, type1_issues, type2_issues, type3_issues)
        - type0_issues: Parent has some_default=true but has NO sub-flags at all
        - type1_issues: Parent has some_default=true but no transitive sub-flags have is_default=true (excluding Type 0 flags)
        - type2_issues: Parent has some_default=false AND is_default=false but at least one transitive sub-flag has is_default=true
        - type3_issues: Parent has is_default=true but NOT all transitive sub-flags have is_default=true
    """
    flags = data['flags']
    type0_issues = []
    type1_issues = []
    type2_issues = []
    type3_issues = []
    
    # First pass: identify Type 0 flags (some_default=true but no children)
    # We'll treat these as if they have is_default=true for Type 1 analysis
    type0_flags = set()
    
    for flag_name, flag_data in flags.items():
        implies = flag_data.get('implies', [])
        parent_some_default = flag_data.get('some_default', False)
        
        # Type 0: Parent says some_default=true but has NO sub-flags at all
        if parent_some_default and not implies:
            type0_flags.add(flag_name)
    
    # Second pass: check for inconsistencies
    for flag_name, flag_data in flags.items():
        implies = flag_data.get('implies', [])
        implies_transitive = flag_data.get('implies_transitive', [])
        parent_some_default = flag_data.get('some_default', False)
        
        # Record Type 0 issues for reporting
        if flag_name in type0_flags:
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
        # Note: is_error, has_no_effect, and Type 0 flags count as enabled by default
        transitive_subflag_defaults = []
        for subflag_name in implies_transitive:
            if subflag_name in flags:
                subflag_is_default = flags[subflag_name].get('is_default', False)
                subflag_is_error = flags[subflag_name].get('is_error', False)
                subflag_has_no_effect = flags[subflag_name].get('has_no_effect', False)
                subflag_is_type0 = subflag_name in type0_flags
                # Treat error by default, has_no_effect, and Type 0 as enabled by default
                is_enabled = subflag_is_default or subflag_is_error or subflag_has_no_effect or subflag_is_type0
                transitive_subflag_defaults.append({
                    'name': subflag_name,
                    'is_default': is_enabled,
                    'is_error': subflag_is_error,
                    'has_no_effect': subflag_has_no_effect,
                    'is_type0': subflag_is_type0
                })
            else:
                # Sub-flag not found in the data
                transitive_subflag_defaults.append({
                    'name': subflag_name,
                    'is_default': None,
                    'is_error': False,
                    'has_no_effect': False,
                    'is_type0': False,
                    'missing': True
                })
        
        # Also track direct implies for reporting
        direct_subflag_defaults = []
        for subflag_name in implies:
            if subflag_name in flags:
                subflag_is_default = flags[subflag_name].get('is_default', False)
                subflag_is_error = flags[subflag_name].get('is_error', False)
                subflag_has_no_effect = flags[subflag_name].get('has_no_effect', False)
                subflag_is_type0 = subflag_name in type0_flags
                # Treat error by default, has_no_effect, and Type 0 as enabled by default
                is_enabled = subflag_is_default or subflag_is_error or subflag_has_no_effect or subflag_is_type0
                direct_subflag_defaults.append({
                    'name': subflag_name,
                    'is_default': is_enabled,
                    'is_error': subflag_is_error,
                    'has_no_effect': subflag_has_no_effect,
                    'is_type0': subflag_is_type0,
                    'some_default': flags[subflag_name].get('some_default', False)
                })
            else:
                direct_subflag_defaults.append({
                    'name': subflag_name,
                    'is_default': None,
                    'is_error': False,
                    'has_no_effect': False,
                    'is_type0': False,
                    'some_default': None,
                    'missing': True
                })
        
        any_transitive_subflag_default = any(sf['is_default'] for sf in transitive_subflag_defaults if sf['is_default'] is not None)
        all_transitive_subflags_non_default = all(not sf['is_default'] for sf in transitive_subflag_defaults if sf['is_default'] is not None)
        all_transitive_subflags_default = all(sf['is_default'] for sf in transitive_subflag_defaults if sf['is_default'] is not None)
        
        # Treat error by default as enabled by default
        parent_is_default = flag_data.get('is_default', False) or flag_data.get('is_error', False)
        parent_is_error = flag_data.get('is_error', False)
        
        # Type 1: Parent says some_default=true but no transitive sub-flags are enabled by default
        if parent_some_default and all_transitive_subflags_non_default:
            # Find which transitive sub-flags are enabled by default for detailed reporting
            enabled_by_default = [sf for sf in transitive_subflag_defaults if sf.get('is_default')]
            
            type1_issues.append({
                'flag': flag_name,
                'parent_some_default': parent_some_default,
                'parent_is_default': parent_is_default,
                'parent_is_error': parent_is_error,
                'direct_subflags': direct_subflag_defaults,
                'transitive_count': len(implies_transitive),
                'enabled_by_default_count': len(enabled_by_default)
            })
        
        # Type 2: Parent says some_default=false AND is_default=false but at least one transitive sub-flag is enabled by default
        # Skip if parent is_default=true (that's Type 3)
        # For Type 2, we check for ACTUAL enabled flags (excluding has_no_effect)
        # has_no_effect flags don't produce warnings/errors, so they shouldn't count for Type 2
        if not parent_some_default and not parent_is_default:
            # Find truly enabled flags (excluding has_no_effect and Type 0)
            truly_enabled = [sf for sf in transitive_subflag_defaults 
                           if sf.get('is_default') and not sf.get('has_no_effect') and not sf.get('is_type0')]
            
            if truly_enabled:
                # Find which transitive sub-flags are enabled by default (for display)
                enabled_by_default = [sf for sf in transitive_subflag_defaults if sf.get('is_default')]
                
                type2_issues.append({
                    'flag': flag_name,
                    'parent_some_default': parent_some_default,
                    'parent_is_default': parent_is_default,
                    'parent_is_error': parent_is_error,
                    'direct_subflags': direct_subflag_defaults,
                    'transitive_count': len(implies_transitive),
                    'enabled_by_default': enabled_by_default,
                    'enabled_by_default_count': len(enabled_by_default),
                    'truly_enabled_count': len(truly_enabled)
                })
        
        # Type 3: Parent is_default=true but NOT all transitive sub-flags have is_default=true
        # If parent is enabled by default, ALL sub-flags should be marked as enabled by default
        if parent_is_default and not all_transitive_subflags_default:
            # Find which transitive sub-flags are NOT enabled by default
            not_enabled_by_default = [sf for sf in transitive_subflag_defaults if not sf.get('is_default') and sf.get('is_default') is not None]
            
            type3_issues.append({
                'flag': flag_name,
                'parent_some_default': parent_some_default,
                'parent_is_default': parent_is_default,
                'parent_is_error': parent_is_error,
                'direct_subflags': direct_subflag_defaults,
                'transitive_count': len(implies_transitive),
                'not_enabled_by_default': not_enabled_by_default,
                'not_enabled_by_default_count': len(not_enabled_by_default)
            })
    
    return type0_issues, type1_issues, type2_issues, type3_issues

def build_flag_hierarchy(issue: Dict, data: Dict, highlight_enabled: bool = False) -> str:
    """
    Build a visual hierarchy of flags showing parent -> children relationships.
    
    Args:
        issue: The issue dictionary containing flag information
        data: The full diagnostics data
        highlight_enabled: If True, highlight flags that are enabled by default (for Type 2)
    
    Returns:
        Markdown formatted hierarchy string
    """
    flags = data['flags']
    flag_name = issue['flag']
    
    lines = []
    lines.append(f"**{flag_link(flag_name)}**")
    lines.append(f"- `some_default`: {issue['parent_some_default']}")
    parent_is_error = issue.get('parent_is_error', False)
    if parent_is_error:
        lines.append(f"- `is_default`: {issue['parent_is_default']} (error by default)")
    else:
        lines.append(f"- `is_default`: {issue['parent_is_default']}")
    
    if issue['direct_subflags']:
        lines.append(f"- **Direct sub-flags** ({len(issue['direct_subflags'])}):")
        for sf in issue['direct_subflags']:
            if sf.get('missing'):
                lines.append(f"  - {flag_link(sf['name'])} ❌ *[MISSING FROM DATA]*")
            else:
                # Determine if this flag should be highlighted
                is_enabled = sf.get('is_default', False)
                is_error = sf.get('is_error', False)
                has_no_effect = sf.get('has_no_effect', False)
                is_type0 = sf.get('is_type0', False)
                has_some_default = sf.get('some_default', False)
                
                markers = []
                if is_enabled and highlight_enabled:
                    if is_error:
                        markers.append("✅ **enabled by default (error)**")
                    elif has_no_effect:
                        markers.append("✅ **enabled by default (no effect)**")
                    elif is_type0:
                        markers.append("✅ **enabled by default (Type 0)**")
                    else:
                        markers.append("✅ **enabled by default**")
                elif is_enabled:
                    if is_error:
                        markers.append("enabled by default (error)")
                    elif has_no_effect:
                        markers.append("enabled by default (no effect)")
                    elif is_type0:
                        markers.append("enabled by default (Type 0)")
                    else:
                        markers.append("enabled by default")
                
                if has_some_default:
                    markers.append("`some_default=true`")
                
                marker_str = f" — {', '.join(markers)}" if markers else ""
                lines.append(f"  - {flag_link(sf['name'])}{marker_str}")
    
    return "\n".join(lines)

def generate_markdown_report(type0_issues: List[Dict], type1_issues: List[Dict], 
                            type2_issues: List[Dict], type3_issues: List[Dict], 
                            data: Dict, output_file: str):
    """Generate a markdown report of the issues found."""
    lines = []
    
    # Header
    lines.append("# Diagnostics.json Inconsistency Analysis Report")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    total_issues = len(type0_issues) + len(type1_issues) + len(type2_issues) + len(type3_issues)
    lines.append(f"Analysis of `tools/diagnostic-flags/diagnostics.json` using **transitive analysis** "
                 f"revealed **{total_issues} total inconsistencies**:")
    lines.append("")
    lines.append(f"- **{len(type0_issues)} Type 0 issues**: Parent flag marked as `some_default=true` but has **NO sub-flags at all**")
    lines.append(f"- **{len(type1_issues)} Type 1 issues**: Parent flag marked as `some_default=true` but NO transitive sub-flags have `is_default=true` (excluding Type 0 flags which are treated as enabled)")
    lines.append(f"- **{len(type2_issues)} Type 2 issues**: Parent flag marked as `some_default=false` AND `is_default=false` but at least one transitive sub-flag has `is_default=true` (excluding `has_no_effect` flags)")
    lines.append(f"- **{len(type3_issues)} Type 3 issues**: Parent flag marked as `is_default=true` or `is_error=true` but NOT all transitive sub-flags are enabled (note: `has_no_effect` and Type 0 flags are treated as enabled)")
    lines.append("")
    
    # Documentation reference
    lines.append("## Documentation Reference")
    lines.append("")
    lines.append("All flag links in this report point to the official [Clang Diagnostics Reference](https://clang.llvm.org/docs/DiagnosticsReference.html).")
    lines.append("")
    
    # Methodology
    lines.append("## Methodology")
    lines.append("")
    lines.append("This analysis uses the `implies_transitive` field in the JSON, which contains the full transitive closure of all sub-flags.")
    lines.append("")
    
    # Type 0 Issues
    if type0_issues:
        lines.append("---")
        lines.append("")
        lines.append("## Type 0 Issues: Claims of Default Sub-flags with NO Sub-flags")
        lines.append("")
        lines.append(f"**Count: {len(type0_issues)}**")
        lines.append("")
        lines.append("These flags claim to have some sub-flags enabled by default (`some_default=true`), "
                     "but they have **no sub-flags at all** (empty `implies` list).")
        lines.append("")
        
        for i, issue in enumerate(type0_issues, 1):
            lines.append(f"### {i}. {flag_link(issue['flag'])}")
            lines.append("")
            lines.append(f"- `some_default`: {issue['parent_some_default']}")
            lines.append(f"- `is_default`: {issue['parent_is_default']}")
            lines.append(f"- `implies`: *(empty)*")
            lines.append("")
    
    # Type 1 Issues
    if type1_issues:
        lines.append("---")
        lines.append("")
        lines.append("## Type 1 Issues: False Claims of Default Sub-flags")
        lines.append("")
        lines.append(f"**Count: {len(type1_issues)}**")
        lines.append("")
        lines.append("These flags claim to have some sub-flags enabled by default (`some_default=true`), "
                     "but when checking the full transitive closure, **none** of their transitive sub-flags "
                     "are actually enabled by default. Note: Type 0 flags (flags with `some_default=true` but no children) "
                     "are treated as enabled by default, so they don't cause Type 1 issues.")
        lines.append("")
        
        for i, issue in enumerate(type1_issues, 1):
            lines.append(f"### {i}. {flag_link(issue['flag'])}")
            lines.append("")
            lines.append(f"**Transitive sub-flags count**: {issue['transitive_count']} (0 enabled by default)")
            lines.append("")
            lines.append("#### Flag Hierarchy")
            lines.append("")
            lines.append(build_flag_hierarchy(issue, data, highlight_enabled=False))
            lines.append("")
    
    # Type 2 Issues
    if type2_issues:
        lines.append("---")
        lines.append("")
        lines.append("## Type 2 Issues: Missing Claims of Default Sub-flags")
        lines.append("")
        lines.append(f"**Count: {len(type2_issues)}**")
        lines.append("")
        lines.append("These flags have BOTH `some_default=false` AND `is_default=false`, "
                     "but when checking the full transitive closure, at least one of their transitive "
                     "sub-flags IS actually enabled by default. "
                     "Note: For Type 2 analysis, `has_no_effect` flags are NOT counted as enabled, since they "
                     "don't produce warnings/errors and thus don't affect correctness. "
                     "Flags that are enabled by default are marked with ✅.")
        lines.append("")
        
        for i, issue in enumerate(type2_issues, 1):
            lines.append(f"### {i}. {flag_link(issue['flag'])}")
            lines.append("")
            lines.append(f"**Transitive sub-flags count**: {issue['transitive_count']} "
                        f"({issue['enabled_by_default_count']} enabled by default)")
            lines.append("")
            lines.append("#### Flag Hierarchy")
            lines.append("")
            lines.append(build_flag_hierarchy(issue, data, highlight_enabled=True))
            lines.append("")
            
            # Show examples of enabled flags if they're not direct children
            if issue['enabled_by_default']:
                # Get names of direct children
                direct_names = {sf['name'] for sf in issue['direct_subflags']}
                # Find enabled flags that are not direct children
                indirect_enabled = [sf for sf in issue['enabled_by_default'] 
                                   if sf['name'] not in direct_names and not sf.get('missing')]
                
                if indirect_enabled:
                    lines.append(f"**Transitive (indirect) sub-flags enabled by default** "
                               f"(showing up to 10 of {len(indirect_enabled)}):")
                    lines.append("")
                    for sf in indirect_enabled[:10]:
                        lines.append(f"- {flag_link(sf['name'])}")
                    lines.append("")
    
    # Type 3 Issues
    if type3_issues:
        lines.append("---")
        lines.append("")
        lines.append("## Type 3 Issues: Parent Enabled by Default but Not All Sub-flags")
        lines.append("")
        lines.append(f"**Count: {len(type3_issues)}**")
        lines.append("")
        lines.append("These flags have `is_default=true` (or `is_error=true`, which counts as enabled), "
                     "which means they are enabled by default. "
                     "This logically implies that ALL of their sub-flags should also be marked as "
                     "`is_default=true`, `is_error=true`, `has_no_effect=true`, or be Type 0 flags, but some sub-flags are NOT marked as enabled by default. "
                     "Flags that are NOT enabled by default are marked with ❌. "
                     "Note: Flags with no effect and Type 0 flags are treated as enabled since they don't affect program behavior or imply enablement.")
        lines.append("")
        
        for i, issue in enumerate(type3_issues, 1):
            lines.append(f"### {i}. {flag_link(issue['flag'])}")
            lines.append("")
            lines.append(f"**Transitive sub-flags count**: {issue['transitive_count']} "
                        f"({issue['not_enabled_by_default_count']} NOT enabled by default)")
            lines.append("")
            lines.append("#### Flag Hierarchy")
            lines.append("")
            
            # Build hierarchy with inverted highlighting (highlight NOT enabled)
            flag_name = issue['flag']
            lines.append(f"**{flag_link(flag_name)}**")
            lines.append(f"- `some_default`: {issue['parent_some_default']}")
            parent_is_error = issue.get('parent_is_error', False)
            if parent_is_error:
                lines.append(f"- `is_default`: {issue['parent_is_default']} ← **Parent is error by default (counts as enabled)**")
            else:
                lines.append(f"- `is_default`: {issue['parent_is_default']} ← **Parent is enabled by default**")
            
            if issue['direct_subflags']:
                lines.append(f"- **Direct sub-flags** ({len(issue['direct_subflags'])}):")
                for sf in issue['direct_subflags']:
                    if sf.get('missing'):
                        lines.append(f"  - {flag_link(sf['name'])} ❌ *[MISSING FROM DATA]*")
                    else:
                        is_enabled = sf.get('is_default', False)
                        is_error = sf.get('is_error', False)
                        has_no_effect = sf.get('has_no_effect', False)
                        is_type0 = sf.get('is_type0', False)
                        has_some_default = sf.get('some_default', False)
                        
                        markers = []
                        if not is_enabled:
                            markers.append("❌ **NOT enabled by default**")
                        elif is_enabled:
                            if is_error:
                                markers.append("✅ enabled by default (error)")
                            elif has_no_effect:
                                markers.append("✅ enabled by default (no effect)")
                            elif is_type0:
                                markers.append("✅ enabled by default (Type 0)")
                            else:
                                markers.append("✅ enabled by default")
                        
                        if has_some_default:
                            markers.append("`some_default=true`")
                        
                        marker_str = f" — {', '.join(markers)}" if markers else ""
                        lines.append(f"  - {flag_link(sf['name'])}{marker_str}")
            lines.append("")
            
            # Show examples of NOT enabled flags if they're not direct children
            if issue['not_enabled_by_default']:
                # Get names of direct children
                direct_names = {sf['name'] for sf in issue['direct_subflags']}
                # Find NOT enabled flags that are not direct children
                indirect_not_enabled = [sf for sf in issue['not_enabled_by_default'] 
                                       if sf['name'] not in direct_names and not sf.get('missing')]
                
                if indirect_not_enabled:
                    lines.append(f"**Transitive (indirect) sub-flags NOT enabled by default** "
                               f"(showing up to 10 of {len(indirect_not_enabled)}):")
                    lines.append("")
                    for sf in indirect_not_enabled[:10]:
                        lines.append(f"- {flag_link(sf['name'])}")
                    lines.append("")
    
    if not type0_issues and not type1_issues and not type2_issues and not type3_issues:
        lines.append("## Result")
        lines.append("")
        lines.append("✅ No inconsistencies found!")
        lines.append("")
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"Report written to: {output_file}")

def main():
    filepath = 'tools/diagnostic-flags/diagnostics.json'
    output_file = 'tools/inconsistency-analysis/inconsistency_report.md'
    
    print("Loading diagnostics.json...")
    data = load_diagnostics(filepath)
    print(f"Loaded {data.get('flag_count', 'unknown')} flags")
    print()
    
    print("Analyzing for inconsistencies...")
    type0_issues, type1_issues, type2_issues, type3_issues = check_inconsistencies(data)
    print()
    
    print(f"Found {len(type0_issues)} Type 0 issues")
    print(f"Found {len(type1_issues)} Type 1 issues")
    print(f"Found {len(type2_issues)} Type 2 issues")
    print(f"Found {len(type3_issues)} Type 3 issues")
    print()
    
    print("Generating markdown report...")
    generate_markdown_report(type0_issues, type1_issues, type2_issues, type3_issues, data, output_file)

if __name__ == '__main__':
    main()
