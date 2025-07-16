# Export Logs API Filtering Options

## Base Endpoint
`GET /export_logs/`

## Available Query Parameters

### Basic Filtering
- `id` (integer) - Filter by specific log ID
- `status` (string) - Filter by export status: `pending`, `success`, `failed`, `skipped`, `expired`
- `export_type` (string) - Filter by export type: `channels`, `feeds`, `items`
- `export_by` (string) - Filter by user who initiated the export (email)
- `format` (string) - Filter by export format: `csv`, `json`

### Error Filtering
- `has_error` (boolean) - Filter by error status:
  - `true` - Only failed exports
  - `false` - Only successful exports

### Duration Filtering
- `min_duration` (float) - Minimum duration in seconds
- `max_duration` (float) - Maximum duration in seconds

### Date Range Filtering
- `start_date` (string) - Start date (YYYY-MM-DD format)
- `end_date` (string) - End date (YYYY-MM-DD format)

### Text Search
- `search` (string) - Search across:
  - User email (`export_by`)
  - Error messages (`error_message`)
  - Export type (`export_type`)

### Pagination & Sorting
- `page` (integer) - Page number (default: 1)
- `per_page` (integer) - Items per page (default: 10)
- `sort_by` (string) - Sort field: `created_at`, `completed_at`, `status`, `export_type`, `format`, `duration`
- `sort_order` (string) - Sort direction: `asc`, `desc` (default: `desc`)

## Example API Calls

### Basic Filtering
```bash
# Get all CSV exports
GET /export_logs/?format=csv

# Get failed exports only
GET /export_logs/?has_error=true

# Get exports by specific user
GET /export_logs/?export_by=user@example.com

# Get channel exports
GET /export_logs/?export_type=channels
```

### Duration Filtering
```bash
# Get exports that took more than 30 seconds
GET /export_logs/?min_duration=30

# Get exports that took less than 5 minutes
GET /export_logs/?max_duration=300

# Get exports between 10-60 seconds
GET /export_logs/?min_duration=10&max_duration=60
```

### Text Search
```bash
# Search for exports containing "channel" in any searchable field
GET /export_logs/?search=channel

# Search for failed exports with specific error
GET /export_logs/?search=database&has_error=true
```

### Combined Filtering
```bash
# Get CSV exports by user that took more than 30 seconds
GET /export_logs/?format=csv&export_by=user@example.com&min_duration=30

# Get failed channel exports from last week
GET /export_logs/?export_type=channels&has_error=true&start_date=2024-01-01&end_date=2024-01-07

# Search and paginate
GET /export_logs/?search=error&page=2&per_page=20&sort_by=duration&sort_order=desc
```

## Response Format
```json
{
  "logs": [
    {
      "id": 1,
      "export_by": "user@example.com",
      "export_type": "channels",
      "status": "success",
      "format": "csv",
      "duration": 45.2,
      "created_at": "2024-01-15T10:30:00Z",
      "completed_at": "2024-01-15T10:30:45Z",
      "file_path": "/exports/channels_20240115.csv",
      "channels_count": 150
    }
  ],
  "page": 1,
  "per_page": 10,
  "total": 25,
  "pages": 3
}
``` 