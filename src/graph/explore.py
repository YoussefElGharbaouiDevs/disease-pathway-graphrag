"""Bounded forward/backward searches over observed temporal associations only."""

import argparse
import json
import re

from neo4j_client import Client, PROJECT_ID


def explore(code, direction="both", depth=1, limit=20):
    if not re.fullmatch(r"[A-Z][0-9]{2}", code) or depth not in (1, 2, 3) or not 1 <= limit <= 100:
        raise ValueError("Use a three-character code, depth 1-3 and limit 1-100")
    if direction not in ("forward", "backward", "both"):
        raise ValueError("Unknown direction")
    arrows = {"forward": f"-[:TEMPORALLY_ASSOCIATED_WITH*1..{depth}]->",
              "backward": f"<-[:TEMPORALLY_ASSOCIATED_WITH*1..{depth}]-"}
    client = Client()
    result = {}
    for mode in (("backward", "forward") if direction == "both" else (direction,)):
        query = f"MATCH p=(d:Diagnosis {{diagnosis_id:$id}}){arrows[mode]}(other:Diagnosis) "
        query += "WHERE all(r IN relationships(p) WHERE r.project_id=$project) "
        query += "RETURN [n IN nodes(p) | n.code] AS codes, [n IN nodes(p) | n.name] AS names, "
        query += "[r IN relationships(p) | r.relationship_id] AS relationship_ids, "
        query += "[r IN relationships(p) | r.relative_risk_reported] AS relative_risks_reported, "
        query += "[r IN relationships(p) | r.source_row] AS source_rows, length(p) AS hops "
        query += "ORDER BY hops, codes LIMIT $limit"
        result[mode] = client.query(query, {"id": "S006:ICD10:" + code, "project": PROJECT_ID, "limit": limit})
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("code")
    parser.add_argument("--direction", choices=("forward", "backward", "both"), default="both")
    parser.add_argument("--depth", type=int, choices=(1, 2, 3), default=1)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    print(json.dumps(explore(args.code, args.direction, args.depth, args.limit), indent=2, ensure_ascii=False))
