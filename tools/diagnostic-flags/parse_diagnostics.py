#!/usr/bin/env python3
"""
Parse Clang Diagnostics Reference to extract flag relationships.

This script fetches the Clang diagnostics documentation and extracts
which flags imply (control) other flags.

Usage:
    python parse_diagnostics.py [--output diagnostics.json] [--url URL]
"""

import argparse
import json
import re
import ssl
import sys
from urllib.request import urlopen
from urllib.error import URLError
from html.parser import HTMLParser


class DiagnosticsParser(HTMLParser):
    """Parse the Clang diagnostics HTML to extract flag relationships."""

    def __init__(self):
        super().__init__()
        self.flags = {}  # flag_name -> {implies: [], implied_by: [], description: str}
        self.current_flag = None
        self.current_section = None
        self.in_heading = False
        self.in_paragraph = False
        self.capture_text = False
        self.text_buffer = ""
        self.heading_level = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # Detect heading tags (h3 for flags)
        if tag in ('h2', 'h3', 'h4'):
            self.in_heading = True
            self.heading_level = tag
            self.text_buffer = ""

        # Detect paragraph for "Also controls" text
        if tag == 'p':
            self.in_paragraph = True
            self.text_buffer = ""

    def handle_endtag(self, tag):
        if tag in ('h2', 'h3', 'h4') and self.in_heading:
            self.in_heading = False
            heading_text = self.text_buffer.strip()

            # Extract flag name from heading (format: "-Wflag-name¶")
            match = re.match(r'^(-W[a-zA-Z0-9+\-_#]+)', heading_text)
            if match:
                flag_name = match.group(1)
                self.current_flag = flag_name
                if flag_name not in self.flags:
                    self.flags[flag_name] = {
                        'implies': [],
                        'implied_by': [],
                        'description': '',
                        'is_error': False,
                        'is_default': False,
                        'some_default': False
                    }

        if tag == 'p' and self.in_paragraph:
            self.in_paragraph = False
            para_text = self.text_buffer.strip()

            if self.current_flag and para_text:
                # Check for "Controls" or "Also controls" pattern
                # The HTML uses anchor tags for flags, so the text looks like:
                # "Controls -Wflag1, -Wflag2, -Wflag3."
                # or "Also controls -Wflag1, -Wflag2."
                controls_match = re.search(
                    r'(?:Also )?[Cc]ontrols\s+(.+?)\.?$',
                    para_text
                )
                if controls_match:
                    controlled_flags_str = controls_match.group(1)
                    controlled_flags = re.findall(r'-W[a-zA-Z0-9+\-_#]+', controlled_flags_str)
                    for controlled in controlled_flags:
                        if controlled not in self.flags[self.current_flag]['implies']:
                            self.flags[self.current_flag]['implies'].append(controlled)

                # Check for "Synonym for" pattern
                synonym_match = re.search(r'Synonym for\s+\\?(-W[a-zA-Z0-9+\-_#]+)', para_text)
                if synonym_match:
                    synonym_flag = synonym_match.group(1)
                    if synonym_flag not in self.flags[self.current_flag]['implies']:
                        self.flags[self.current_flag]['implies'].append(synonym_flag)

                # Check if it's an error by default
                if 'error by default' in para_text.lower():
                    self.flags[self.current_flag]['is_error'] = True

                # Check if enabled by default - must be the flag itself, not just sub-flags
                # "This diagnostic is enabled by default" = the flag is on by default
                # "Some of the diagnostics controlled by this flag are enabled by default" = only sub-flags
                if 'This diagnostic is enabled by default' in para_text:
                    self.flags[self.current_flag]['is_default'] = True
                elif 'Some of the diagnostics controlled by this flag are enabled by default' in para_text:
                    self.flags[self.current_flag]['is_default'] = False
                    self.flags[self.current_flag]['some_default'] = True

    def handle_data(self, data):
        if self.in_heading or self.in_paragraph:
            self.text_buffer += data

    def build_implied_by(self):
        """Build reverse relationships (implied_by from implies)."""
        for flag_name, flag_data in self.flags.items():
            for implied_flag in flag_data['implies']:
                if implied_flag in self.flags:
                    if flag_name not in self.flags[implied_flag]['implied_by']:
                        self.flags[implied_flag]['implied_by'].append(flag_name)
                else:
                    # Create entry for referenced flag that wasn't parsed directly
                    self.flags[implied_flag] = {
                        'implies': [],
                        'implied_by': [flag_name],
                        'description': '',
                        'is_error': False,
                        'is_default': False,
                        'some_default': False
                    }


def fetch_documentation(url):
    """Fetch the diagnostics documentation HTML."""
    print(f"Fetching documentation from {url}...", file=sys.stderr)
    try:
        # Create SSL context that doesn't verify certificates (for macOS compatibility)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        with urlopen(url, timeout=30, context=ssl_context) as response:
            return response.read().decode('utf-8')
    except URLError as e:
        print(f"Error fetching documentation: {e}", file=sys.stderr)
        sys.exit(1)


def get_all_implies(flags, flag_name, visited=None):
    """Recursively get all flags implied by a given flag."""
    if visited is None:
        visited = set()

    if flag_name in visited:
        return set()

    visited.add(flag_name)
    result = set()

    if flag_name in flags:
        for implied in flags[flag_name]['implies']:
            result.add(implied)
            result.update(get_all_implies(flags, implied, visited))

    return result


def main():
    parser = argparse.ArgumentParser(
        description='Parse Clang Diagnostics Reference for flag relationships'
    )
    parser.add_argument(
        '--url',
        default='https://clang.llvm.org/docs/DiagnosticsReference.html',
        help='URL to the Clang diagnostics reference'
    )
    parser.add_argument(
        '--output', '-o',
        default='diagnostics.json',
        help='Output JSON file path'
    )
    parser.add_argument(
        '--include-transitive',
        action='store_true',
        help='Include transitive implications in output'
    )

    args = parser.parse_args()

    # Fetch and parse
    html_content = fetch_documentation(args.url)

    diagnostics_parser = DiagnosticsParser()
    diagnostics_parser.feed(html_content)
    diagnostics_parser.build_implied_by()

    flags = diagnostics_parser.flags

    # Optionally compute transitive closure
    if args.include_transitive:
        for flag_name in flags:
            all_implied = get_all_implies(flags, flag_name)
            flags[flag_name]['implies_transitive'] = sorted(list(all_implied))

    # Sort flags alphabetically
    sorted_flags = dict(sorted(flags.items()))

    # Create output structure
    output = {
        'source_url': args.url,
        'flag_count': len(sorted_flags),
        'flags': sorted_flags
    }

    # Write output
    with open(args.output, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Parsed {len(sorted_flags)} diagnostic flags", file=sys.stderr)
    print(f"Output written to {args.output}", file=sys.stderr)

    # Print some stats
    flags_with_implies = sum(1 for f in flags.values() if f['implies'])
    flags_with_implied_by = sum(1 for f in flags.values() if f['implied_by'])
    print(f"Flags that imply others: {flags_with_implies}", file=sys.stderr)
    print(f"Flags implied by others: {flags_with_implied_by}", file=sys.stderr)


if __name__ == '__main__':
    main()
