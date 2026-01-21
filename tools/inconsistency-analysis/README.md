# Inconsistency Analysis Tool

This tool analyzes the `diagnostics.json` file for inconsistencies between parent warning flags and their sub-flags in Clang's diagnostic system.

## Files

- **`analyze_inconsistencies.py`** - Python script that performs the analysis
- **`inconsistency_report.md`** - Generated report with links to official Clang documentation

## What It Does

The script performs **transitive analysis** using the `implies_transitive` field to identify four types of inconsistencies.

**Synonym Handling:** The analysis properly handles flag synonyms (aliases). When a flag is marked as a synonym (e.g., `-Wdeprecated-writable-strings` is a synonym for `-Wc++11-compat-deprecated-writable-strings`), it inherits all properties (`is_default`, `some_default`, `is_error`) from its canonical form. This ensures that synonyms are treated consistently with their canonical flags.

**Error-by-Default Treatment:** Flags marked as `is_error=true` (error by default) are treated as enabled by default for the consistency analysis. This is logical because if a diagnostic is an error by default, it is definitely enabled. For example, `-Wreturn-mismatch` is an error by default, so it counts as enabled when checking if its parent flag `-Wreturn-type` has all sub-flags enabled.

**No-Effect Flags:** Flags marked as `has_no_effect=true` (flags that have no effect on program behavior) are treated differently depending on the analysis type:
- **Type 1 & Type 3**: Treated as enabled (to avoid false positives)
- **Type 2**: Treated as disabled (since they can't cause warnings/errors)

This dual treatment reflects the semantic meaning: a "no effect" flag satisfies a parent's claim that sub-flags exist, but doesn't require the parent to claim `some_default=true` since it produces no actual warnings. For example, `-Wignored-pragma-optimize` has no effect, so its parent `-Wignored-pragmas` correctly doesn't need to set `some_default=true`.

**Type 0 Flag Treatment:** Type 0 flags (flags with `some_default=true` but no children) are treated as if they have `is_default=true` when checking Type 1 and Type 3 issues. This is a reasonable assumption since if a flag claims "some sub-flags are enabled" but has no children, it likely means the flag itself is enabled. This eliminates redundant reporting where a parent would be flagged as Type 1 solely because it has Type 0 children. For example, `-Wc++14-compat` is no longer a Type 1 issue because its sub-flag `-Wpre-c++26-compat` is a Type 0 flag and is treated as enabled.

### Type 0: Claims of Default Sub-flags with NO Sub-flags
Parent flag marked as `some_default=true` but has **NO sub-flags at all** (empty `implies` list). This is logically impossible.

### Type 1: False Claims of Default Sub-flags
Parent flag marked as `some_default=true` but **none** of its transitive sub-flags have `is_default=true`. Note: Type 0 flags (flags with `some_default=true` but no children) are treated as if they have `is_default=true` for this analysis, since it's reasonable to assume they would be enabled. This eliminates redundant reporting between Type 0 and Type 1.

### Type 2: Missing Claims of Default Sub-flags
Parent flag marked as `some_default=false` **AND** `is_default=false` but at least one transitive sub-flag **is** enabled by default (`is_default=true`). Note: For Type 2 analysis, `has_no_effect` flags are NOT counted as enabled, since they don't produce warnings/errors and shouldn't affect the parent's `some_default` claim.

### Type 3: Parent Enabled by Default but Not All Sub-flags
Parent flag marked as `is_default=true` or `is_error=true`, which means it's enabled by default. This logically implies that **ALL** of its sub-flags should also be marked as `is_default=true` or `is_error=true`, but some are not.

## Usage

Run the analysis script from the project root:

```bash
python tools/inconsistency-analysis/analyze_inconsistencies.py
```

This will generate/update `inconsistency_report.md` with:
- Links to the [Clang Diagnostics Reference](https://clang.llvm.org/docs/DiagnosticsReference.html) for each flag
- Flag hierarchies showing parent → children relationships
- Highlighted (✅) flags that are enabled by default in Type 2 issues
- Transitive (indirect) sub-flags when applicable

## Requirements

- Python 3.6+
- No additional dependencies required

## Understanding the Output

The report uses markdown formatting with:

- **Flag links**: Every flag name is a clickable link to its documentation
- **Flag hierarchies**: Shows the parent flag and its direct sub-flags
- **Enabled markers**: ✅ indicates a flag is enabled by default
- **Metadata**: Shows `some_default`, `is_default`, and other relevant properties

## Examples

### Type 2 Example: `-Wasm`

```
**`-Wasm`**
- `some_default`: False
- `is_default`: False
- **Direct sub-flags** (1):
  - `-Wasm-operand-widths` — ✅ **enabled by default**
```

This shows that `-Wasm` claims to have no sub-flags enabled by default (`some_default=false`) and is itself not enabled (`is_default=false`), but its sub-flag `-Wasm-operand-widths` is actually enabled by default.

### Type 3 Example: `-Wformat`

```
**`-Wformat`**
- `some_default`: False
- `is_default`: True ← **Parent is enabled by default**
- **Direct sub-flags** (9):
  - `-Wformat-extra-args` — ✅ enabled by default
  - `-Wformat-insufficient-args` — ✅ enabled by default
  - ...
  - `-Wformat-y2k` — ❌ **NOT enabled by default**
  - ...
```

This shows that `-Wformat` is enabled by default (`is_default=true`), which should mean all its sub-flags are enabled. However, `-Wformat-y2k` is NOT marked as enabled by default, which is inconsistent.

**Note:** Error-by-default flags (like `-Wreturn-mismatch`) are treated as enabled and will show `✅ enabled by default (error)` in the report.
