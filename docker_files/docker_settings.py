import dj_database_url

from pretix.settings import *  # noqa: F403

LOGGING['handlers']['mail_admins']['include_html'] = True  # noqa: F405

DATABASES['default'] = dj_database_url.config()  # noqa: F405
