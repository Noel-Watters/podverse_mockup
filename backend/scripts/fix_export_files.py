# backend/scripts/fix_export_files.py

import os
import csv
from seed_utils import get_db_session
from app.models.export_logs import ExportLog

def fix_export_files():
    """Fix the export files to have the correct export log format"""
    session = get_db_session()
    
    try:
        # Get all export logs that have file paths
        logs_with_files = session.query(ExportLog).filter(ExportLog.file_path.isnot(None)).all()
        
        for log in logs_with_files:
            # Extract filename from the file_path
            filename = os.path.basename(log.file_path)
            filepath = os.path.join('/app/exports', filename)
            
            # Create the correct CSV format with export log data
            def write_export_log_data(f):
                writer = csv.writer(f)
                writer.writerow([
                    'id', 'export_by', 'source', 'status', 'format', 
                    'file_path', 'created_at', 'completed_at', 'feeds_count', 'channels_count', 'items_count', 'error_message'
                ])
                
                # Write the current log data
                writer.writerow([
                    log.id,
                    log.export_by,
                    log.source,
                    log.status,
                    log.format,
                    log.file_path or "",
                    log.created_at.isoformat() if log.created_at else "",
                    log.completed_at.isoformat() if log.completed_at else "",
                    log.feeds_count or "",
                    log.channels_count or "",
                    log.items_count or "",
                    log.error_message or ""
                ])
            
            # Write the file
            with open(filepath, 'w', newline='') as f:
                write_export_log_data(f)
            
            print(f"✅ Fixed export file: {filename}")
        
        print(f"✅ Successfully fixed {len(logs_with_files)} export files")
        
    except Exception as e:
        print(f"❌ Failed to fix export files: {str(e)}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    fix_export_files() 