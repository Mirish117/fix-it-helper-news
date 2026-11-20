"""Safety check for news.json. Runs on every pull request (see .github/workflows).

Fails if the file is not valid, if an item is missing something the app needs,
or if an item tries to do something the app does not allow.
"""
import json
import re
import sys
from datetime import date

ALLOWED_RUN = {"run:winupdate", "run:devmgmt", "run:security", "run:taskmgr",
               "run:startup", "run:power", "run:explorer", "run:mdsched"}
ALLOWED_FIX = {"internet", "cleanup", "graphics", "update", "windows", "apps", "virus",
               "explain", "sound", "printer", "taskbar", "clock", "bluetooth", "report"}
MATCH_KEYS = {"windows", "versions", "editions", "gpu", "nvidiaDriverBelow", "hasUpdate", "missingUpdate"}
TYPES = {"problem", "fixed", "info"}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URL = re.compile(r'^https://[^\s"<>]+$')


def action_ok(a: str) -> bool:
    if a in ALLOWED_RUN:
        return True
    m = re.match(r"^fix:(\w+)$", a)
    if m:
        return m.group(1) in ALLOWED_FIX
    return a.startswith("url:") and bool(URL.match(a[4:]))


def check(path: str) -> list[str]:
    errors = []
    raw = open(path, "rb").read()
    if len(raw) > 500_000:
        errors.append("news.json is larger than 500 KB; the app will refuse it.")
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError:
        errors.append("news.json must use plain characters only (no curly quotes, dashes or emoji).")
        text = raw.decode("utf-8", "replace")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return errors + [f"news.json is not valid JSON: {e}"]

    if not DATE.match(str(data.get("updated", ""))):
        errors.append('"updated" must be a date like 2026-11-20.')
    items = data.get("items")
    if not isinstance(items, list) or not items:
        return errors + ['"items" must be a list with at least one item.']

    seen = set()
    for n, it in enumerate(items, 1):
        where = f"item {n} ({it.get('id', 'no id')})"
        for key in ("id", "date", "type", "title", "summary", "whatToDo", "source"):
            if not str(it.get(key, "")).strip():
                errors.append(f"{where}: missing \"{key}\".")
        if it.get("id") in seen:
            errors.append(f"{where}: the id is used twice.")
        seen.add(it.get("id"))
        for key in ("date", "expires"):
            if key in it and not DATE.match(str(it[key])):
                errors.append(f"{where}: \"{key}\" must look like 2026-11-20.")
        if it.get("type") not in TYPES:
            errors.append(f"{where}: \"type\" must be problem, fixed or info.")
        if it.get("source") and not URL.match(str(it["source"])):
            errors.append(f"{where}: \"source\" must be an https link.")
        if "action" in it and not action_ok(str(it["action"])):
            errors.append(f"{where}: action \"{it['action']}\" is not allowed (see README).")
        if len(str(it.get("title", ""))) > 120:
            errors.append(f"{where}: title is longer than 120 characters.")
        m = it.get("match")
        if m is not None:
            if not isinstance(m, dict):
                errors.append(f"{where}: \"match\" must be an object.")
            else:
                for k in m:
                    if k not in MATCH_KEYS:
                        errors.append(f"{where}: unknown match field \"{k}\".")
                for k in ("editions", "gpu"):
                    if k in m:
                        try:
                            re.compile(str(m[k]))
                        except re.error:
                            errors.append(f"{where}: \"{k}\" is not a valid pattern.")
                if "nvidiaDriverBelow" in m and not re.match(r"^\d{3}\.\d{2}$", str(m["nvidiaDriverBelow"])):
                    errors.append(f"{where}: nvidiaDriverBelow must look like 621.14.")
                if "versions" in m and not isinstance(m["versions"], list):
                    errors.append(f"{where}: \"versions\" must be a list, like [\"25H2\"].")
        if str(it.get("date", "")) > date.today().isoformat():
            errors.append(f"{where}: the date is in the future.")
    return errors


if __name__ == "__main__":
    problems = check(sys.argv[1] if len(sys.argv) > 1 else "news.json")
    if problems:
        print("news.json has problems:")
        for p in problems:
            print("  - " + p)
        sys.exit(1)
    print("news.json looks good.")
