import json
import os
import shutil
import subprocess

import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_EXTRACT_UI_STRINGS_SCRIPT = """
const fs = require("fs");
const src = fs.readFileSync(process.argv[1], "utf8");
const start = src.indexOf("const UI_STRINGS = {");
if (start === -1) { console.error("UI_STRINGS not found"); process.exit(1); }
const braceStart = src.indexOf("{", start);
let depth = 0, i = braceStart;
for (; i < src.length; i++) {
  if (src[i] === "{") depth++;
  else if (src[i] === "}") { depth--; if (depth === 0) { i++; break; } }
}
const obj = eval("(" + src.slice(braceStart, i) + ")");
process.stdout.write(JSON.stringify({ vi: Object.keys(obj.vi), en: Object.keys(obj.en) }));
"""


def test_ui_strings_vi_and_en_have_identical_keys():
    """UI_STRINGS.vi and UI_STRINGS.en in i18n.js must cover exactly the
    same set of keys — otherwise switching language would silently fall
    back to Vietnamese (or the raw key) for anything missing on one side."""
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available in this environment")
    result = subprocess.run(
        [node, "-e", _EXTRACT_UI_STRINGS_SCRIPT, "--", os.path.join(BASE_DIR, "i18n.js")],
        capture_output=True, text=True, check=True,
        # BAT BUOC co encoding. text=True giai ma theo bang ma mac
        # dinh CUA MAY: tren Windows la cp1252, vo ngay o chu tieng
        # Viet trong i18n.js. Khi do stdout ra None va json.loads
        # nem TypeError — mot loi khong he nhac gi toi bang ma.
        encoding="utf-8",
    )
    keys = json.loads(result.stdout)
    vi_keys, en_keys = set(keys["vi"]), set(keys["en"])
    assert vi_keys == en_keys, (
        f"vi-only keys: {vi_keys - en_keys}; en-only keys: {en_keys - vi_keys}"
    )


def test_every_data_i18n_attribute_in_html_has_a_ui_strings_entry():
    """Every data-i18n / data-i18n-html / data-i18n-placeholder /
    data-i18n-aria-label key referenced in index.html must exist in
    UI_STRINGS — otherwise that element would silently render the raw key
    string instead of text.

    The regex below must list EVERY data-i18n-* variant applyStaticText()
    handles. A variant left out is not a harmless gap: the key it carries
    escapes this check entirely, so a typo in it ships a raw key string to
    the screen with the whole suite still green."""
    import re

    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available in this environment")

    html = open(os.path.join(BASE_DIR, "index.html"), encoding="utf-8").read()
    keys_used = set(re.findall(
        r'data-i18n(?:-html|-placeholder|-aria-label)?="([a-zA-Z0-9_]+)"', html))
    assert keys_used, "sanity check: should have found data-i18n attributes in index.html"

    result = subprocess.run(
        [node, "-e", _EXTRACT_UI_STRINGS_SCRIPT, "--", os.path.join(BASE_DIR, "i18n.js")],
        capture_output=True, text=True, check=True,
        # BAT BUOC co encoding. text=True giai ma theo bang ma mac
        # dinh CUA MAY: tren Windows la cp1252, vo ngay o chu tieng
        # Viet trong i18n.js. Khi do stdout ra None va json.loads
        # nem TypeError — mot loi khong he nhac gi toi bang ma.
        encoding="utf-8",
    )
    keys = json.loads(result.stdout)
    vi_keys = set(keys["vi"])

    missing = keys_used - vi_keys
    assert not missing, f"index.html uses i18n keys missing from UI_STRINGS: {missing}"


def test_generated_js_error_catalog_is_up_to_date():
    """i18n_loi.js is GENERATED from i18n_errors.py's MESSAGES by
    tao_i18n_js.py. If someone edits MESSAGES and forgets to regenerate,
    the UI silently falls back to showing a raw code instead of translated
    text. Pure Python byte comparison — runs everywhere, no Node.js needed
    (the old hand-copied catalog check was skipped on machines without it).
    """
    import io
    import tao_i18n_js

    with io.open(os.path.join(BASE_DIR, "i18n_loi.js"), encoding="utf-8",
                 newline="") as f:
        tren_dia = f.read()
    assert tren_dia == tao_i18n_js.noi_dung(), (
        "i18n_loi.js is stale — run: python tao_i18n_js.py")


def test_js_error_catalog_matches_python_error_catalog():
    """End to end: what the BROWSER actually evaluates must equal MESSAGES.
    Guards the generator itself (escaping, encoding), not just staleness."""
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available in this environment")
    script = (
        'global.window = {}; require(process.argv[1]); '
        'process.stdout.write(JSON.stringify(window.I18N_ERROR_MESSAGES));'
    )
    result = subprocess.run(
        [node, "-e", script, "--", os.path.join(BASE_DIR, "i18n_loi.js")],
        capture_output=True, text=True, check=True, encoding="utf-8",
    )
    from i18n_errors import MESSAGES as py_messages

    assert json.loads(result.stdout) == py_messages


def test_i18n_js_no_longer_carries_a_hand_copied_error_catalog():
    """A second hand-written copy would silently shadow the generated one."""
    import io

    js = io.open(os.path.join(BASE_DIR, "i18n.js"), encoding="utf-8").read()
    assert "const ERROR_MESSAGES = global.I18N_ERROR_MESSAGES" in js
    assert "error_reading_last_run" not in js


@pytest.mark.parametrize("trang", ["index.html", "recovery.html"])
def test_pages_load_generated_catalog_before_i18n_js(trang):
    import io

    html = io.open(os.path.join(BASE_DIR, trang), encoding="utf-8").read()
    a = html.find('<script src="i18n_loi.js"></script>')
    b = html.find('<script src="i18n.js"></script>')
    assert a != -1 and b != -1 and a < b


@pytest.mark.parametrize("trang", ["index.html", "recovery.html"])
def test_every_script_a_page_loads_is_bundled_into_the_exe(trang):
    """A script the page loads but PyInstaller does not bundle works from
    source and breaks only in the .exe — invisible until a school runs it.
    Both lists must carry it: kiosk.spec (what gets bundled) and the
    workflow's bundle check (what gets verified after building)."""
    import io
    import re

    html = io.open(os.path.join(BASE_DIR, trang), encoding="utf-8").read()
    spec = io.open(os.path.join(BASE_DIR, "kiosk.spec"), encoding="utf-8").read()
    wf = io.open(os.path.join(BASE_DIR, ".github", "workflows",
                              "build-windows-exe.yml"), encoding="utf-8").read()
    scripts = re.findall(r'<script src="([^"]+)"', html)
    assert scripts
    for s in scripts:
        if s.startswith("js/"):
            # js/ duoc dong goi ca thu muc; tests/test_dong_goi_du_tep.py
            # kiem tung tep trong do.
            assert '("js", "js")' in spec, "js/ missing from kiosk.spec"
            assert "js/$($tep.Name)" in wf, "js/ missing from the workflow bundle check"
            continue
        assert '("%s", ".")' % s in spec, "%s missing from kiosk.spec" % s
        assert '"%s"' % s in wf, "%s missing from the workflow bundle check" % s
