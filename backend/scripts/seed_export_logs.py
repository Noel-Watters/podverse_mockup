# backend/scripts/seed_export_logs.py

import os
import csv
from datetime import datetime, timedelta
from seed_utils import get_db_session
from app.models.export_logs import ExportLog

def ensure_export_directory():
    """Ensures the exports directory exists"""
    # Use a path relative to the backend directory
    export_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
        # Ensure directory has correct permissions
        os.chmod(export_dir, 0o755)
    return export_dir

def safe_write_file(filepath: str, write_func):
    """Safely write a file using a write function"""
    import tempfile
    import shutil
    
    temp_file = None
    try:
        # Create temporary file in the same directory
        directory = os.path.dirname(filepath)
        with tempfile.NamedTemporaryFile(mode='w', 
                                       dir=directory,
                                       prefix='._tmp_',
                                       delete=False) as temp_file:
            # Write to temporary file
            write_func(temp_file)
            temp_file.flush()
            os.fsync(temp_file.fileno())
            
        # Atomic rename
        shutil.move(temp_file.name, filepath)
        return True, None
        
    except Exception as e:
        error_msg = f"Error writing file {filepath}: {str(e)}"
        
        # Clean up temp file if it exists
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except Exception:
                pass
                
        return False, error_msg

def seed_export_logs(n: int = 5):
    """
    Seed export logs with various statuses and file paths.
    
    Args:
        n: Number of export logs to create
    """
    session = get_db_session()
    
    try:
        # Ensure exports directory exists
        export_dir = ensure_export_directory()
        
        # Create some sample export files
        sample_files = []
        for i in range(3):
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"sample_export_{i+1}_{timestamp}.csv"
            filepath = os.path.join(export_dir, filename)
            
            # Create a sample CSV file
            def write_sample_data(f):
                writer = csv.writer(f)
                writer.writerow(['id', 'title', 'description'])
                writer.writerow([1, f'Sample Item {i+1}', f'Description for item {i+1}'])
                writer.writerow([2, f'Another Item {i+1}', f'Another description {i+1}'])
            
            success, error = safe_write_file(filepath, write_sample_data)
            if success:
                sample_files.append(filepath)
                print(f"✅ Created sample file: {filename}")
            else:
                print(f"❌ Failed to create sample file: {error}")
        
        # Create export log entries
        export_types = ['channels', 'feeds', 'items']
        
        for i in range(n):
            # Alternate between valid and invalid file paths
            if i < len(sample_files):
                file_path = sample_files[i]
                status = 'success'
                completed_at = datetime.utcnow() - timedelta(hours=i)
            else:
                file_path = None
                status = 'expired' if i % 2 == 0 else 'failed'
                completed_at = datetime.utcnow() - timedelta(days=31) if status == 'expired' else datetime.utcnow() - timedelta(hours=1)
            
            log = ExportLog(
                admin_email=f"admin{i+1}@podverse.com",
                export_type=export_types[i % len(export_types)],
                filters={"format": "csv", "sort_by": "id"},
                status=status,
                file_path=file_path,
                format="csv",
                channels_count=10 + i if status == 'success' else None,
                feeds_count=5 + i if status == 'success' else None,
                items_count=20 + i if status == 'success' else None,
                created_at=datetime.utcnow() - timedelta(days=i+1),
                completed_at=completed_at,
                error_message=f"Sample error message for log {i+1}" if status == 'failed' else None
            )
            
            session.add(log)
        
        session.commit()
        print(f"✅ Successfully created {n} export log entries")
        
        # Print summary
        print("\nExport Logs Summary:")
        for log in session.query(ExportLog).all():
            file_status = "✅ File exists" if log.file_path and os.path.exists(log.file_path) else "❌ File missing"
            print(f"  ID {log.id}: {log.status} - {log.export_type} - {file_status}")
            
    except Exception as e:
        session.rollback()
        print(f"❌ Failed to create export logs: {str(e)}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed export logs")
    parser.add_argument("--count", "-n", type=int, default=5, help="Number of export logs to create")
    
    args = parser.parse_args()
    seed_export_logs(args.count) 