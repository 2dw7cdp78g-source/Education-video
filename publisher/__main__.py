"""Start the publisher: python3 -m publisher"""
import logging
import sys

import uvicorn

from . import config


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if not config.is_local_url(config.BASE_URL) and not config.APP_PASSWORD:
        sys.exit("PUBLIC_BASE_URL isn't localhost, so set APP_PASSWORD in publisher/.env first. "
                 "Otherwise anyone with the link could post to your accounts.")
    print(f"Publisher running: open {config.BASE_URL}" + ("  (DRY RUN: nothing is uploaded)" if config.DRY_RUN else ""))
    uvicorn.run("publisher.web:app", host=config.HOST, port=config.PORT, log_level="warning")


if __name__ == "__main__":
    main()
