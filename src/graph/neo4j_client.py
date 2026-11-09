"""Small local client for the transactional HTTP endpoint in pinned Neo4j 5.26.

The transport is isolated here for a later move to the Bolt driver/Query API.
"""

import base64
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
PROJECT_ID = "disease-pathway-graphrag"
ASSOCIATION_DISPLAY_LABEL = "Associated with a later diagnosis of"


def settings(root=ROOT):
    values = {}
    path = root / ".env"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.lstrip().startswith("#"):
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip()
    for key in ("NEO4J_HTTP_URL", "NEO4J_USERNAME", "NEO4J_PASSWORD"):
        if key in os.environ:
            values[key] = os.environ[key]
    return values


class Client:
    def __init__(self, root=ROOT):
        config = settings(root)
        self.url = config.get("NEO4J_HTTP_URL", "http://127.0.0.1:7474").rstrip("/")
        parsed = urlparse(self.url)
        if parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost") or parsed.username:
            raise ValueError("This prototype importer only targets the local project Neo4j instance")
        password = config.get("NEO4J_PASSWORD")
        if not password:
            raise ValueError("Missing NEO4J_PASSWORD in the project .env")
        token = base64.b64encode(f"{config.get('NEO4J_USERNAME', 'neo4j')}:{password}".encode()).decode()
        self.headers = {"Authorization": "Basic " + token, "Content-Type": "application/json"}

    def commit(self, statements):
        payload = json.dumps({"statements": statements}, ensure_ascii=False).encode("utf-8")
        request = Request(self.url + "/db/neo4j/tx/commit", data=payload, headers=self.headers)
        try:
            with urlopen(request, timeout=120) as response:
                result = json.load(response)
        except HTTPError as exc:
            raise RuntimeError(f"Neo4j HTTP request failed with status {exc.code}") from None
        if result.get("errors"):
            raise RuntimeError("Neo4j transaction failed: " + "; ".join(
                error["code"] + ": " + error["message"] for error in result["errors"]
            ))
        return result["results"]

    def query(self, statement, parameters=None):
        result = self.commit([{"statement": statement, "parameters": parameters or {}}])[0]
        return [dict(zip(result["columns"], item["row"])) for item in result["data"]]
