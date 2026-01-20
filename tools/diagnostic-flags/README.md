# Clang Diagnostic Flags Explorer

An interactive tool to explore relationships between Clang diagnostic (warning) flags.

## Features

- **Search**: Filter flags by name
- **Direct implications**: See which flags a given flag directly controls
- **Reverse lookup**: See which flags imply a given flag
- **Transitive closure**: Toggle to see all transitively implied flags
- **Flag metadata**: See if a flag is enabled by default or treated as an error

## Usage

### 1. Generate the data

Run the parser to fetch and parse the Clang diagnostics documentation:

```bash
python3 parse_diagnostics.py
```

Options:
- `--url URL`: Custom URL for the diagnostics reference (default: https://clang.llvm.org/docs/DiagnosticsReference.html)
- `--output FILE`: Output JSON file path (default: diagnostics.json)
- `--include-transitive`: Pre-compute transitive implications (recommended)

Example:
```bash
python3 parse_diagnostics.py --include-transitive --output diagnostics.json
```

### 2. Start the web interface

Serve the files with any HTTP server:

```bash
python3 -m http.server 8080
```

Then open http://localhost:8080 in your browser.

## Files

- `parse_diagnostics.py` - Python script to fetch and parse the Clang documentation
- `index.html` - Interactive web interface
- `diagnostics.json` - Generated data file (created by running the parser)

## Data Source

Data is parsed from the [Clang Diagnostics Reference](https://clang.llvm.org/docs/DiagnosticsReference.html).
