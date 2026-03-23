# Example Files

This directory contains sample files for testing the Ignition Tag Bulk Uploader.

## Phase 1 (POC)

Phase 1 does not yet parse spreadsheets. The `/api/upload` endpoint accepts any file but creates a hardcoded test tag to demonstrate the Ignition integration.

## Phase 2 (Full Implementation)

These files will be used for testing Phase 2 features:

### sample_tags.csv

A sample CSV file with tag definitions. This demonstrates the expected format for bulk tag uploads.

**Columns:**
- `name` - Tag name (required)
- `path` - Tag folder path (optional, e.g., "Facility/Zone1")
- `dataType` - Data type (Boolean, Integer, Float, Double, String, DateTime, Long)
- `opcItemPath` - OPC item path (required for OPC tags, e.g., "[PLC1]Zone1/Temp")
- `opcServer` - OPC server name (optional, default from config)
- `description` - Tag description (optional)
- `enabled` - Whether tag is enabled (optional, default true)

**Usage (Phase 2):**
```bash
curl -X POST http://localhost:8080/api/upload \
  -F "file=@examples/sample_tags.csv" \
  -F 'config={"tagProvider":"default","basePath":"","dryRun":false}'
```

## Future Examples

Additional example files to be added:
- `sample_tags.xlsx` - Excel format
- `sample_tags_with_errors.csv` - For testing validation
- `large_import.csv` - 1000+ tags for batch testing
- `minimal_tags.csv` - Minimum required fields only
