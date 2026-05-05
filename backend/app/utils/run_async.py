# backend/app/utils/run_async.py

from flask import request, current_app
import threading
from app.utils.log_config import get_logger

logger = get_logger(__name__)

def maybe_run_async(target_func, *args, **kwargs):
    async_mode = request.args.get('async', '').lower() == 'true'
    if request.is_json:
        try:
            async_mode = async_mode or (request.get_json(silent=True) or {}).get('async', False)
        except Exception:
            pass

    if async_mode:
        app = current_app._get_current_object()
        # Capture request data before starting async thread
        request_data = None
        if request.is_json:
            try:
                request_data = request.get_json()
            except Exception:
                pass

        def runner():
            with app.app_context():
                try:
                    # Pass request data as payload if available
                    if request_data is not None:
                        target_func(payload=request_data, *args, **kwargs)
                    else:
                        target_func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Async task failed: {str(e)}")

        threading.Thread(target=runner).start()
        return {"status": "queued"}

    return target_func(*args, **kwargs)