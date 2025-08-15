import os
import sys
import logging

GPL_KEYWORDS = [
    "GNU GENERAL PUBLIC LICENSE",
    "Version 3, 29 June 2007",
    "https://www.gnu.org/licenses/gpl-3.0.html"
]

GPL_TEMPLATE = """\
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
Everyone is permitted to copy and distribute verbatim copies
of this license document, but changing it is not allowed.
...
(完整官方範本請至 https://www.gnu.org/licenses/gpl-3.0.txt 取得)
"""

def check_license(auto_fix=False):
    """Advanced LICENSE checker: validate content, auto-fix if needed."""
    license_file = os.path.join(os.path.dirname(__file__), "LICENSE")

    if not os.path.isfile(license_file):
        logging.critical("LICENSE file missing! The bot cannot start without a valid LICENSE.")
        if auto_fix:
            try:
                with open(license_file, "w", encoding="utf-8") as f:
                    f.write(GPL_TEMPLATE)
                logging.warning("LICENSE file auto-generated with GPL-3.0 template.")
                return
            except Exception as e:
                logging.critical(f"Auto-fix failed for LICENSE: {e}")
        sys.exit(1)

    try:
        with open(license_file, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError as e:
        logging.critical(f"Error reading LICENSE file: {e}")
        sys.exit(1)

    missing_keywords = [kw for kw in GPL_KEYWORDS if kw not in content]
    if missing_keywords:
        logging.critical(f"LICENSE file content invalid! Missing: {missing_keywords}")
        if auto_fix:
            try:
                with open(license_file, "w", encoding="utf-8") as f:
                    f.write(GPL_TEMPLATE)
                logging.warning("LICENSE file auto-updated with GPL-3.0 template.")
                return
            except Exception as e:
                logging.critical(f"Auto-fix failed for LICENSE: {e}")
        sys.exit(1)

    logging.info("LICENSE check passed.")
