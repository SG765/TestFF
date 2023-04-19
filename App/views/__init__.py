# blue prints are imported 
# explicitly instead of using *
from .user import user_views
from .index import index_views
from .auth import auth_views
from App.controllers.auth import auth_viewsC


views = [user_views, index_views, auth_views, auth_viewsC] 
# blueprints must be added to this list