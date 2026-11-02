import logging.config

import yaml

from course_service.core.config import get_settings
from course_service.web.api.v1 import api_router
from course_service.web.app import create_app
from course_service.web.lifespans import lifespan_app

logger = logging.getLogger(__name__)

if __name__ == "course_service.main":
    with open("log-config.yaml", encoding="UTF-8") as f:
        log_config = yaml.safe_load(f)
        logging.config.dictConfig(log_config)
    settings = get_settings()
    routers = (api_router,)
    app = create_app(settings, routers, lifespan=lifespan_app)
    logger.debug(f"Created app={app} with settings={settings}")
