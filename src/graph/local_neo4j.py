"""Set up/start a project-local Windows Neo4j Community instance (Java 21)."""

import argparse
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import time
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

from neo4j_client import Client, ROOT, settings

VERSION = "5.26.33"
ARCHIVE = f"neo4j-community-{VERSION}-windows.zip"
URL = "https://dist.neo4j.org/" + ARCHIVE
EXPECTED_SHA256 = "380a4cfd26ea23ece35922ed1ab27c33503eebda634e4e58cdd6f908bd0166ff"
LOCAL = ROOT / ".local"
HOME = LOCAL / f"neo4j-community-{VERSION}"


def java_home():
    runtime = LOCAL / "neo4j_runtime.json"
    if runtime.exists():
        candidate = Path(json.loads(runtime.read_text())["java_home"])
    elif os.environ.get("JAVA_HOME"):
        candidate = Path(os.environ["JAVA_HOME"])
    else:
        java = shutil.which("java")
        if not java:
            raise RuntimeError("Java 21 is required; set JAVA_HOME")
        candidate = Path(java).resolve().parents[1]
    if not (candidate / "bin/java.exe").exists():
        raise RuntimeError("Configured Java executable does not exist")
    return candidate


def command(kind, *arguments):
    java = java_home()
    env = os.environ.copy()
    env.update(JAVA_HOME=str(java), NEO4J_HOME=str(HOME), NEO4J_CONF=str(HOME / "conf"))
    main = "Neo4jAdminCommand" if kind == "admin" else "Neo4jCommand"
    args = [str(java / "bin/java.exe"), "-cp", str(HOME / "lib/*"), f"-Dbasedir={HOME}",
            "org.neo4j.server.startup." + main, *arguments]
    return args, env


def setup():
    LOCAL.mkdir(exist_ok=True)
    archive = LOCAL / ARCHIVE
    if not archive.exists():
        with urlopen(URL, timeout=45) as response, archive.open("wb") as stream:
            shutil.copyfileobj(response, stream)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != EXPECTED_SHA256:
        raise RuntimeError("Neo4j download checksum mismatch")
    if not HOME.exists():
        with ZipFile(archive) as zipped:
            for item in zipped.infolist():
                if not (LOCAL / item.filename).resolve().is_relative_to(LOCAL.resolve()):
                    raise ValueError("Archive path escapes the local runtime folder")
            zipped.extractall(LOCAL)
    java = java_home()
    (LOCAL / "neo4j_runtime.json").write_text(json.dumps({"version": VERSION, "java_home": str(java)}, indent=2) + "\n")
    config = HOME / "conf/neo4j.conf"
    text = config.read_text()
    if "# Disease Pathway GraphRAG local instance" not in text:
        text += "\n# Disease Pathway GraphRAG local instance\n"
        text += "server.default_listen_address=127.0.0.1\nserver.default_advertised_address=127.0.0.1\n"
        text += "server.http.listen_address=127.0.0.1:7474\nserver.bolt.listen_address=127.0.0.1:7687\n"
        text += "server.memory.heap.initial_size=256m\nserver.memory.heap.max_size=512m\n"
        text += "server.memory.pagecache.size=128m\ndbms.usage_report.enabled=false\n"
        config.write_text(text)
    env_path = ROOT / ".env"
    if not env_path.exists():
        password = secrets.token_urlsafe(24)
        env_path.write_text("NEO4J_HTTP_URL=http://127.0.0.1:7474\nNEO4J_URI=bolt://127.0.0.1:7687\n"
                            "NEO4J_USERNAME=neo4j\nNEO4J_PASSWORD=" + password + "\n")
    password = settings()["NEO4J_PASSWORD"]
    marker = LOCAL / "neo4j_auth_initialized"
    if not marker.exists():
        if (HOME / "data/databases/neo4j").exists():
            raise RuntimeError("Database already exists; refusing to reset credentials")
        args, env = command("admin", "dbms", "set-initial-password", password)
        result = subprocess.run(args, env=env, cwd=HOME, capture_output=True, text=True,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode:
            raise RuntimeError("Neo4j initial-password setup failed: " + result.stderr.replace(password, "[redacted]"))
        marker.write_text("Initialized; credentials are in the ignored project .env.\n")
    print(f"Project-local Neo4j Community {VERSION} configured; credentials kept in .env.")


def start():
    client = Client()
    try:
        client.query("RETURN 1 AS ready")
        print("Project Neo4j is already reachable.")
        return
    except OSError:
        pass
    args, env = command("server", "console")
    with (LOCAL / "neo4j-console.log").open("a", encoding="utf-8") as stream:
        process = subprocess.Popen(args, env=env, cwd=HOME, stdout=stream, stderr=stream,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
    (LOCAL / "neo4j_launcher.json").write_text(json.dumps({"pid": process.pid, "home": str(HOME)}, indent=2) + "\n")
    for _ in range(50):
        if process.poll() is not None:
            raise RuntimeError("Neo4j exited during startup; inspect .local/neo4j-console.log")
        try:
            client.query("RETURN 1 AS ready")
            print("Neo4j ready: http://127.0.0.1:7474/browser/")
            return
        except OSError:
            time.sleep(1)
    print("Neo4j is starting; check status or .local/neo4j-console.log shortly.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("setup", "start", "status", "console"))
    action = parser.parse_args().action
    if action == "setup":
        setup()
    elif action == "start":
        start()
    elif action == "status":
        print(Client().query("CALL dbms.components() YIELD name, versions RETURN name, versions"))
    else:
        args, env = command("server", action)
        raise SystemExit(subprocess.call(args, env=env, cwd=HOME))
