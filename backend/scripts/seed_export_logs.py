# backend/scripts/seed_export_logs.py

import os
import csv
from datetime import datetime, timedelta
from seed_utils import get_db_session, fake, unique_uuid
from app.models.export_logs import ExportLog
from sqlalchemy.exc import IntegrityError
import random

def seed_export_logs(n=25):
    """Seed the database with export log data"""
    session = get_db_session()
    try:
        export_types = ['channels', 'feeds', 'items']
        statuses = ['pending', 'success', 'failed', 'skipped', 'expired']
        formats = ['csv', 'json']
        
        for _ in range(n):
            export_type = random.choice(export_types)
            status = random.choice(statuses)
            format_type = random.choice(formats)
            
            # Generate realistic counts based on export type
            if export_type == 'channels':
                channels_count = random.randint(10, 100)
                feeds_count = None
                items_count = None
            elif export_type == 'feeds':
                channels_count = None
                feeds_count = random.randint(50, 500)
                items_count = None
            else:  # items
                channels_count = None
                feeds_count = None
                items_count = random.randint(100, 2000)
            
            # Generate file path for successful exports
            file_path = None
            if status == 'success':
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                file_path = f"/app/exports/{export_type}_export_{timestamp}_{str(unique_uuid())[:8]}.{format_type}"
                
                # Ensure exports directory exists
                os.makedirs('/app/exports', exist_ok=True)
                
                # Create the actual export file
                try:
                    with open(file_path, 'w', newline='') as f:
                        if format_type == 'csv':
                            writer = csv.writer(f)
                            writer.writerow([
                                'id', 'export_by', 'export_type', 'status', 'format', 
                                'file_path', 'created_at', 'completed_at', 'feeds_count', 'channels_count', 'items_count', 'error_message'
                            ])
                        else:  # json
                            import json
                            f.write('[\n]')  # Empty JSON array
                except Exception as e:
                    print(f"Warning: Could not create export file {file_path}: {e}")
                    file_path = None  # Reset file_path if creation fails
            
            # Generate error message for failed exports
            error_message = None
            if status == 'failed':
                error_messages = [
                    "Export timeout: Operation exceeded maximum time limit",
                    "Database connection error during export",
                    "Invalid filter parameters provided",
                    "Insufficient permissions to access requested data",
                    "File system error: Unable to write export file"
                ]
                error_message = random.choice(error_messages)
            
            # Set completion time for completed exports
            completed_at = None
            if status in ['success', 'failed']:
                completed_at = datetime.utcnow() - timedelta(minutes=random.randint(1, 30))
            
            export_log = ExportLog(
                export_by=fake.email(),
                export_type=export_type,
                filters={
                    "date_from": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                    "date_to": datetime.utcnow().isoformat(),
                    "status": random.choice(['active', 'inactive', None])
                } if random.choice([True, False]) else None,
                status=status,
                file_path=file_path,
                format=format_type,
                channels_count=channels_count,
                feeds_count=feeds_count,
                items_count=items_count,
                created_at=datetime.utcnow() - timedelta(minutes=random.randint(31, 120)),
                completed_at=completed_at,
                error_message=error_message
            )
            
            session.add(export_log)
        
        session.commit()
        print(f"Seeded {n} export logs successfully")
        
        # Populate the created files with actual export log data
        populate_export_files(session)
        
    except IntegrityError as e:
        session.rollback()
        print("Integrity error while inserting export logs:", str(e))
    finally:
        session.close()

def populate_export_files(session):
    """Populate the created export files with actual data"""
    try:
        # Get all export logs that have file paths
        logs_with_files = session.query(ExportLog).filter(ExportLog.file_path.isnot(None)).all()
        
        for log in logs_with_files:
            if not os.path.exists(log.file_path):
                continue
                
            # Populate the file with export log data
            try:
                with open(log.file_path, 'w', newline='') as f:
                    if log.format == 'csv':
                        writer = csv.writer(f)
                        writer.writerow([
                            'id', 'export_by', 'export_type', 'status', 'format', 
                            'file_path', 'created_at', 'completed_at', 'feeds_count', 'channels_count', 'items_count', 'error_message'
                        ])
                        
                        # Write the current log data
                        writer.writerow([
                            log.id,
                            log.export_by,
                            log.export_type,
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
                    else:  # json
                        import json
                        data = {
                            'id': log.id,
                            'export_by': log.export_by,
                            'export_type': log.export_type,
                            'status': log.status,
                            'format': log.format,
                            'file_path': log.file_path,
                            'created_at': log.created_at.isoformat() if log.created_at else None,
                            'completed_at': log.completed_at.isoformat() if log.completed_at else None,
                            'feeds_count': log.feeds_count,
                            'channels_count': log.channels_count,
                            'items_count': log.items_count,
                            'error_message': log.error_message
                        }
                        json.dump([data], f, indent=2)
                        
                print(f"✅ Populated export file: {os.path.basename(log.file_path)}")
                
            except Exception as e:
                print(f"Warning: Could not populate export file {log.file_path}: {e}")
                
    except Exception as e:
        print(f"Warning: Could not populate export files: {e}")

# Note: fix_export_files() function has been moved to fix_export_files.py

if __name__ == "__main__":
    seed_export_logs() 