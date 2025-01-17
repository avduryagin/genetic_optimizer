
class Config:
    DEBUG=False
    TESTING=False
    WTF_CSRF_ENABLED=True
    PREFERRED_URL_SCHEME='https'
    SESSION_COOKIE_SECURE=True
    SESSION_COOKIE_HTTPONLY=True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SECRET_KEY=None
    CSP="default-src 'self' 'unsafe-eval' 'unsafe-inline' data: blob:; font-src 'self' data: blob:; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:";
    HSTS='max-age=31536000;includeSubDomains'
    X_PERMITTED_CROSS_DOMAIN_POLICIES='none'
    X_FRAME_OPTIONS = 'SAMEORIGIN'
    X_XSS_PROTECTION = '1; mode=block'
    X_CONTENT_TYPE_OPTIONS = 'nosniff'
    X_DOWNLOAD_OPTIONS = 'noopen'


