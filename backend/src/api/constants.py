# Shared authentication error responses for endpoints requiring authentication/authorization
AUTH_ERROR_RESPONSES = {
    401: {"description": "Not authenticated. Valid authentication credentials were not provided."},
    403: {"description": "Forbidden. You do not have permission to access this resource."}
}
