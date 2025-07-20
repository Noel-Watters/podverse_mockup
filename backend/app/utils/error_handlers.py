# app/utils/error_handlers.py

from flask import jsonify, current_app, request
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from marshmallow import ValidationError as MarshmallowValidationError
from werkzeug.exceptions import HTTPException
from app.utils.error_exceptions import APIException, ValidationError, NotFoundError, DatabaseError
from app.utils.auth import AuthError
from app.utils.security_logger import log_network_event
from functools import wraps
import traceback
import socket

def handle_errors(route_func):
    """
    Universal error handler decorator for route functions.
    
    This decorator wraps route functions to provide consistent error handling
    without requiring try/except blocks in every route. It catches common
    exceptions and returns appropriate HTTP responses.
    
    Usage:
        @feed_bp.route('/<int:feed_id>', methods=['GET'])
        @limiter.limit("80 per minute")
        @handle_errors
        def get_feed_by_id(feed_id):
            result = get_feed_by_id_controller(feed_id)
            return jsonify(result), 200
    """
    @wraps(route_func)
    def wrapper(*args, **kwargs):
        try:
            return route_func(*args, **kwargs)
        except ValidationError as e:
            current_app.logger.warning(f"Validation error in {route_func.__name__}: {str(e)}")
            return jsonify({"error": str(e)}), getattr(e, "status_code", 400)
        except NotFoundError as e:
            current_app.logger.warning(f"Not found error in {route_func.__name__}: {str(e)}")
            return jsonify({"error": str(e) if str(e) else "Resource not found"}), 404
        except DatabaseError as e:
            current_app.logger.error(f"Database error in {route_func.__name__}: {str(e)}")
            return jsonify({"error": str(e)}), getattr(e, "status_code", 500)
        except AuthError as e:
            if getattr(e, 'error', {}).get("code") == "authorization_header_missing":
                current_app.logger.debug(f"Missing auth header in {route_func.__name__}: {str(e)}")
            else:
                current_app.logger.warning(f"Auth error in {route_func.__name__}: {str(e)}")
            return jsonify({"error": e.error}), e.status_code
        except Exception as e:
            current_app.logger.error(f"Unexpected error in {route_func.__name__}: {str(e)}")
            current_app.logger.error(f"Full traceback: {traceback.format_exc()}")
            
            #  more specific error messages for common issues
            error_message = "Internal server error"
            if "rate limit" in str(e).lower() or "too many requests" in str(e).lower():
                error_message = "Rate limit exceeded"
            elif "validation" in str(e).lower():
                error_message = f"Validation error: {str(e)}"
            elif "not found" in str(e).lower():
                error_message = f"Resource not found: {str(e)}"
            
            return jsonify({"error": error_message}), 500
    return wrapper

def register_error_handlers(app):
    
    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        """Handle JWT authentication errors from Auth0"""
        return {"error": ex.error}, ex.status_code
    
    @app.errorhandler(APIException)
    def handle_api_exception(e):
        response = {
            'error': {
                'message': e.message,
                'status_code': e.status_code
            }
        }
        if e.payload:
            response['error']['payload'] = e.payload
            
        return jsonify(response), e.status_code
    
    @app.errorhandler(MarshmallowValidationError)
    def handle_marshmallow_validation_error(e):
        response = {
            'error': {
                'message': 'Validation Error',
                'status_code': 400,
                'errors': e.messages
            }
        }
        return jsonify(response), 400
    
    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(e):
        current_app.logger.error(f"Database error: {str(e)}")
        
        if isinstance(e, IntegrityError):
            return jsonify({
                'error': {
                    'message': 'Data integrity constraint violation',
                    'status_code': 409
                }
            }), 409
            
        return jsonify({
            'error': {
                'message': 'Database operation failed',
                'status_code': 500
            }
        }), 500
        
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return jsonify({
            'error': {
                'message': error.description,
                'status_code': error.code
            }
        }), error.code
    
    @app.errorhandler(429)
    def handle_rate_limit_error(error):
        """Handle rate limiting errors (429 Too Many Requests)"""
        current_app.logger.warning(f"Rate limit exceeded: {request.method} {request.path}")
        
        # Extract rate limit info from the error if available
        rate_limit_info = getattr(error, 'description', 'Rate limit exceeded')
        
        return jsonify({
            'error': {
                'message': 'Rate limit exceeded',
                'status_code': 429,
                'details': rate_limit_info
            }
        }), 429
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        current_app.logger.error(f"Unhandled exception: {str(error)}")
        current_app.logger.error(traceback.format_exc())
        
        # Detect network related issues (low level)
        network_related = isinstance(error, (socket.timeout, ConnectionError, TimeoutError, BrokenPipeError, ConnectionResetError))

        # Log error in the logger
        current_app.logger.error(
            f"UNHANDLED EXCEPTION: {request.method} {request.path} - {str(error)}\n{traceback.format_exc()}"
        )

        # If it is a network related issue log the event 
        if network_related:
            # Get admin_id from request context or use 'unknown' if not authenticated
            admin_id = getattr(getattr(request, "admin", None), "sub", "unknown")
            log_network_event(
                current_app.logger,
                "NETWORK_ISSUE",
                admin_id,
                f"{type(error).__name__}: {str(error)}"
            )

        return jsonify({
            'error': {
                'message': 'An unexpected error occurred',
                'status_code': 500
            }
        }), 500