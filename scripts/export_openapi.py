"""Export the FastAPI OpenAPI schema to clients/specs/openapi.json."""
from __future__ import annotations

import json
import logging
import pathlib

from fastapi.openapi.utils import get_openapi

from mail_client_service.app import app

logger = logging.getLogger(__name__)
def main() -> None:
    spec = get_openapi(title=app.title, version=app.version, routes=app.routes)
    out = pathlib.Path("clients/specs")
    out.mkdir(parents=True, exist_ok=True)
    (out / "openapi.json").write_text(json.dumps(spec, indent=2))
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
    logger.info("OpenAPI spec written to clients/specs/openapi.json")
