### install django-cors-headers
pip install django-cors-headers

### add the following lines to settings.py

INSTALLED_APPS = (
    #...
    'corsheaders'
    #...

)

MIDDLEWARE_CLASSES = (
    #...
    'corsheaders.middleware.CorsMiddleware',
    #...
)

CORS_ORIGIN_ALLOW_ALL = False  # set true if all website allowed

CORS_ORIGIN_WHITELIST = (
    'http//:localhost:8000',
)