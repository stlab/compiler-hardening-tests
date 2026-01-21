# Diagnostics.json Inconsistency Analysis Report

## Summary

Analysis of `tools/diagnostic-flags/diagnostics.json` using **transitive analysis** revealed **41 total inconsistencies**:

- **26 Type 0 issues**: Parent flag marked as `some_default=true` but has **NO sub-flags at all**
- **15 Type 1 issues**: Parent flag marked as `some_default=true` but NO transitive sub-flags have `is_default=true` (excluding Type 0 flags which are treated as enabled)
- **0 Type 2 issues**: Parent flag marked as `some_default=false` AND `is_default=false` but at least one transitive sub-flag has `is_default=true` (excluding `has_no_effect` flags)
- **0 Type 3 issues**: Parent flag marked as `is_default=true` or `is_error=true` but NOT all transitive sub-flags are enabled (note: `has_no_effect` and Type 0 flags are treated as enabled)

## Documentation Reference

All flag links in this report point to the official [Clang Diagnostics Reference](https://clang.llvm.org/docs/DiagnosticsReference.html).

## Methodology

This analysis uses the `implies_transitive` field in the JSON, which contains the full transitive closure of all sub-flags.

---

## Type 0 Issues: Claims of Default Sub-flags with NO Sub-flags

**Count: 26**

These flags claim to have some sub-flags enabled by default (`some_default=true`), but they have **no sub-flags at all** (empty `implies` list).

### 1. [`-Waarch64-sme-attributes`](https://clang.llvm.org/docs/DiagnosticsReference.html#waarch64-sme-attributes)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 2. [`-Wc++26-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-26-extensions)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 3. [`-Wc99-compat`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc99-compat)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 4. [`-Wcomment`](https://clang.llvm.org/docs/DiagnosticsReference.html#wcomment)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 5. [`-Wcuda-compat`](https://clang.llvm.org/docs/DiagnosticsReference.html#wcuda-compat)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 6. [`-Wdtor-name`](https://clang.llvm.org/docs/DiagnosticsReference.html#wdtor-name)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 7. [`-Wduplicate-decl-specifier`](https://clang.llvm.org/docs/DiagnosticsReference.html#wduplicate-decl-specifier)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 8. [`-Wexpansion-to-defined`](https://clang.llvm.org/docs/DiagnosticsReference.html#wexpansion-to-defined)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 9. [`-Wgcc-compat`](https://clang.llvm.org/docs/DiagnosticsReference.html#wgcc-compat)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 10. [`-Wgnu-designator`](https://clang.llvm.org/docs/DiagnosticsReference.html#wgnu-designator)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 11. [`-Wgnu-folding-constant`](https://clang.llvm.org/docs/DiagnosticsReference.html#wgnu-folding-constant)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 12. [`-Wimplicit-function-declaration`](https://clang.llvm.org/docs/DiagnosticsReference.html#wimplicit-function-declaration)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 13. [`-Wimplicit-int`](https://clang.llvm.org/docs/DiagnosticsReference.html#wimplicit-int)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 14. [`-Wmain`](https://clang.llvm.org/docs/DiagnosticsReference.html#wmain)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 15. [`-Wmain-return-type`](https://clang.llvm.org/docs/DiagnosticsReference.html#wmain-return-type)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 16. [`-Wmicrosoft-anon-tag`](https://clang.llvm.org/docs/DiagnosticsReference.html#wmicrosoft-anon-tag)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 17. [`-Wmicrosoft-exception-spec`](https://clang.llvm.org/docs/DiagnosticsReference.html#wmicrosoft-exception-spec)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 18. [`-Wpre-c++26-compat`](https://clang.llvm.org/docs/DiagnosticsReference.html#wpre-c-26-compat)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 19. [`-Wreceiver-forward-class`](https://clang.llvm.org/docs/DiagnosticsReference.html#wreceiver-forward-class)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 20. [`-Wsource-uses-openacc`](https://clang.llvm.org/docs/DiagnosticsReference.html#wsource-uses-openacc)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 21. [`-Wsource-uses-openmp`](https://clang.llvm.org/docs/DiagnosticsReference.html#wsource-uses-openmp)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 22. [`-Wstatic-in-inline`](https://clang.llvm.org/docs/DiagnosticsReference.html#wstatic-in-inline)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 23. [`-Wunknown-pragmas`](https://clang.llvm.org/docs/DiagnosticsReference.html#wunknown-pragmas)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 24. [`-Wvariadic-macros`](https://clang.llvm.org/docs/DiagnosticsReference.html#wvariadic-macros)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 25. [`-Wvector-conversion`](https://clang.llvm.org/docs/DiagnosticsReference.html#wvector-conversion)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

### 26. [`-Wvla-extension-static-assert`](https://clang.llvm.org/docs/DiagnosticsReference.html#wvla-extension-static-assert)

- `some_default`: True
- `is_default`: False
- `implies`: *(empty)*

---

## Type 1 Issues: False Claims of Default Sub-flags

**Count: 15**

These flags claim to have some sub-flags enabled by default (`some_default=true`), but when checking the full transitive closure, **none** of their transitive sub-flags are actually enabled by default. Note: Type 0 flags (flags with `some_default=true` but no children) are treated as enabled by default, so they don't cause Type 1 issues.

### 1. [`-Wc++14-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-14-extensions)

**Transitive sub-flags count**: 2 (0 enabled by default)

#### Flag Hierarchy

**[`-Wc++14-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-14-extensions)**
- `some_default`: True
- `is_default`: False
- **Direct sub-flags** (2):
  - [`-Wc++14-attribute-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-14-attribute-extensions)
  - [`-Wc++14-binary-literal`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-14-binary-literal)

### 2. [`-Wc++17-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-17-extensions)

**Transitive sub-flags count**: 1 (0 enabled by default)

#### Flag Hierarchy

**[`-Wc++17-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-17-extensions)**
- `some_default`: True
- `is_default`: False
- **Direct sub-flags** (1):
  - [`-Wc++17-attribute-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-17-attribute-extensions)

### 3. [`-Wc++1y-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-1y-extensions)

**Transitive sub-flags count**: 3 (0 enabled by default)

#### Flag Hierarchy

**[`-Wc++1y-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-1y-extensions)**
- `some_default`: True
- `is_default`: False
- **Direct sub-flags** (1):
  - [`-Wc++14-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-14-extensions) — `some_default=true`

### 4. [`-Wc++1z-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-1z-extensions)

**Transitive sub-flags count**: 2 (0 enabled by default)

#### Flag Hierarchy

**[`-Wc++1z-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-1z-extensions)**
- `some_default`: True
- `is_default`: False
- **Direct sub-flags** (1):
  - [`-Wc++17-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-17-extensions) — `some_default=true`

### 5. [`-Wc++20-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-20-extensions)

**Transitive sub-flags count**: 3 (0 enabled by default)

#### Flag Hierarchy

**[`-Wc++20-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-20-extensions)**
- `some_default`: True
- `is_default`: False
- **Direct sub-flags** (3):
  - [`-Wc++20-attribute-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-20-attribute-extensions)
  - [`-Wc++20-designator`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-20-designator)
  - [`-Wvariadic-macro-arguments-omitted`](https://clang.llvm.org/docs/DiagnosticsReference.html#wvariadic-macro-arguments-omitted)

### 6. [`-Wc++2a-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-2a-extensions)

**Transitive sub-flags count**: 4 (0 enabled by default)

#### Flag Hierarchy

**[`-Wc++2a-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-2a-extensions)**
- `some_default`: True
- `is_default`: False
- **Direct sub-flags** (1):
  - [`-Wc++20-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-20-extensions) — `some_default=true`

### 7. [`-Wc23-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc23-extensions)

**Transitive sub-flags count**: 1 (0 enabled by default)

#### Flag Hierarchy

**[`-Wc23-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc23-extensions)**
- `some_default`: True
- `is_default`: False
- **Direct sub-flags** (1):
  - [`-Wvariadic-macro-arguments-omitted`](https://clang.llvm.org/docs/DiagnosticsReference.html#wvariadic-macro-arguments-omitted)

### 8. [`-Wc2x-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc2x-extensions)

**Transitive sub-flags count**: 2 (0 enabled by default)

#### Flag Hierarchy

**[`-Wc2x-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc2x-extensions)**
- `some_default`: True
- `is_default`: False
- **Direct sub-flags** (1):
  - [`-Wc23-extensions`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc23-extensions) — `some_default=true`

### 9. [`-Wcalled-once-parameter`](https://clang.llvm.org/docs/DiagnosticsReference.html#wcalled-once-parameter)

**Transitive sub-flags count**: 1 (0 enabled by default)

#### Flag Hierarchy

**[`-Wcalled-once-parameter`](https://clang.llvm.org/docs/DiagnosticsReference.html#wcalled-once-parameter)**
- `some_default`: True
- `is_default`: False
- **Direct sub-flags** (1):
  - [`-Wcompletion-handler`](https://clang.llvm.org/docs/DiagnosticsReference.html#wcompletion-handler)

### 10. [`-Wdynamic-exception-spec`](https://clang.llvm.org/docs/DiagnosticsReference.html#wdynamic-exception-spec)

**Transitive sub-flags count**: 1 (0 enabled by default)

#### Flag Hierarchy

**[`-Wdynamic-exception-spec`](https://clang.llvm.org/docs/DiagnosticsReference.html#wdynamic-exception-spec)**
- `some_default`: True
- `is_default`: False
- **Direct sub-flags** (1):
  - [`-Wdeprecated-dynamic-exception-spec`](https://clang.llvm.org/docs/DiagnosticsReference.html#wdeprecated-dynamic-exception-spec)

### 11. [`-Wlocal-type-template-args`](https://clang.llvm.org/docs/DiagnosticsReference.html#wlocal-type-template-args)

**Transitive sub-flags count**: 1 (0 enabled by default)

#### Flag Hierarchy

**[`-Wlocal-type-template-args`](https://clang.llvm.org/docs/DiagnosticsReference.html#wlocal-type-template-args)**
- `some_default`: True
- `is_default`: False
- **Direct sub-flags** (1):
  - [`-Wc++98-compat-local-type-template-args`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-98-compat-local-type-template-args)

### 12. [`-Wpointer-arith`](https://clang.llvm.org/docs/DiagnosticsReference.html#wpointer-arith)

**Transitive sub-flags count**: 1 (0 enabled by default)

#### Flag Hierarchy

**[`-Wpointer-arith`](https://clang.llvm.org/docs/DiagnosticsReference.html#wpointer-arith)**
- `some_default`: True
- `is_default`: False
- **Direct sub-flags** (1):
  - [`-Wgnu-pointer-arith`](https://clang.llvm.org/docs/DiagnosticsReference.html#wgnu-pointer-arith)

### 13. [`-Wpragma-pack`](https://clang.llvm.org/docs/DiagnosticsReference.html#wpragma-pack)

**Transitive sub-flags count**: 1 (0 enabled by default)

#### Flag Hierarchy

**[`-Wpragma-pack`](https://clang.llvm.org/docs/DiagnosticsReference.html#wpragma-pack)**
- `some_default`: True
- `is_default`: False
- **Direct sub-flags** (1):
  - [`-Wpragma-pack-suspicious-include`](https://clang.llvm.org/docs/DiagnosticsReference.html#wpragma-pack-suspicious-include)

### 14. [`-Wreserved-user-defined-literal`](https://clang.llvm.org/docs/DiagnosticsReference.html#wreserved-user-defined-literal)

**Transitive sub-flags count**: 1 (0 enabled by default)

#### Flag Hierarchy

**[`-Wreserved-user-defined-literal`](https://clang.llvm.org/docs/DiagnosticsReference.html#wreserved-user-defined-literal)**
- `some_default`: True
- `is_default`: False
- **Direct sub-flags** (1):
  - [`-Wc++11-compat-reserved-user-defined-literal`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-11-compat-reserved-user-defined-literal)

### 15. [`-Wunnamed-type-template-args`](https://clang.llvm.org/docs/DiagnosticsReference.html#wunnamed-type-template-args)

**Transitive sub-flags count**: 1 (0 enabled by default)

#### Flag Hierarchy

**[`-Wunnamed-type-template-args`](https://clang.llvm.org/docs/DiagnosticsReference.html#wunnamed-type-template-args)**
- `some_default`: True
- `is_default`: False
- **Direct sub-flags** (1):
  - [`-Wc++98-compat-unnamed-type-template-args`](https://clang.llvm.org/docs/DiagnosticsReference.html#wc-98-compat-unnamed-type-template-args)
