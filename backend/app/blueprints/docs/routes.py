from flask import send_from_directory, Response
import os
from . import docs_bp


OPENAPI_BASE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "openapi")
)
BUNDLED_PATH = os.path.join(OPENAPI_BASE, "bundled.yaml")

@docs_bp.route("/openapi.yaml")
def openapi_yaml():
    # Serve the bundled OpenAPI spec as text/yaml
    with open(BUNDLED_PATH, "r") as f:
        yaml_content = f.read()
    return Response(yaml_content, mimetype="text/yaml")

@docs_bp.route("/")
def swagger_ui():
    # Create a simple HTML file that loads Swagger UI without inline scripts
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Podverse API Docs</title>
    <link href="https://unpkg.com/swagger-ui-dist@4/swagger-ui.css" rel="stylesheet" />
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@4/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@4/swagger-ui-standalone-preset.js"></script>
    <script src="/admin/docs/swagger-config.js"></script>
</body>
</html>"""
    return Response(html_content, mimetype="text/html")

@docs_bp.route("/swagger-config.js")
def swagger_config():
    # Serve the Swagger configuration as a separate JavaScript file
    js_content = """window.onload = function() {
    const ui = SwaggerUIBundle({
        url: "/admin/docs/openapi.yaml",
        dom_id: '#swagger-ui',
        presets: [
            SwaggerUIBundle.presets.apis,
            SwaggerUIStandalonePreset
        ],
        layout: "BaseLayout",
        deepLinking: true,
        showExtensions: true,
        showCommonExtensions: true,
        persistAuthorization: true,
        onComplete: function() {
            // Add simple text about Auth0 authentication
            const authInfo = document.createElement('div');
            authInfo.innerHTML = `
                <h3>Authentication</h3>
                <p>This API uses Auth0 JWT Bearer tokens for authentication.</p>
                <p><strong>How to get a token:</strong></p>
                <ol>
                    <li>Use the frontend login page at /login</li>
                    <li>Authenticate through Auth0</li>
                    <li>Copy the JWT token from your browser's developer tools</li>
                    <li>Click the "Authorize" button above and enter: Bearer YOUR_JWT_TOKEN</li>
                </ol>
                <p><strong>Alternative:</strong> You can also get a token directly from Auth0 using their API or SDK, then use it in the format: Bearer YOUR_TOKEN</p>
            `;
            
            // Insert the auth info at the top of the swagger-ui container
            const swaggerContainer = document.getElementById('swagger-ui');
            if (swaggerContainer) {
                swaggerContainer.insertBefore(authInfo, swaggerContainer.firstChild);
            }
        }
    });
};"""
    return Response(js_content, mimetype="application/javascript")