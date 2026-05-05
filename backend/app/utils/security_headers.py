# app/utils/security_headers.py

from flask_talisman import Talisman

# Minimal but essential security headers
def secure_headers(app, config_name):
    Talisman(
        app,
        content_security_policy={
            'default-src': ["'self'"],
            'script-src': ["'self'", 'https://unpkg.com'],
            'style-src': ["'self'", 'https://unpkg.com'],
            'img-src': ["'self'", "data:"],
            'font-src': ["'self'", 'https://fonts.gstatic.com'],
            'frame-src': ["'none'"],
            'object-src': ["'none'"],
        },
        force_https=(config_name == "production"),
        strict_transport_security=True,
        strict_transport_security_max_age=31_536_000,
        referrer_policy='strict-origin-when-cross-origin'
    )

    @app.after_request
    def set_additional_headers(response):
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=()'
        response.headers['Cache-Control'] = 'no-store, max-age=0'
        return response