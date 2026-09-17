import os
from pathlib import Path
try:
    from pathutility import get_output_dir
    BASE_USER_DIR = get_output_dir()
except ImportError:
    BASE_USER_DIR = Path.home() / "Documents" / "AutoCAS Reports"

DEBUG_MODE = False
DBNAME      = "entries.db"
DBLOC       = str(BASE_USER_DIR) + "\\"
DB          = DBLOC + DBNAME
REPORTSFOL  = str(BASE_USER_DIR / "reports")
RAWFOL      = str(BASE_USER_DIR / "raw")
TEMPDIR     = str(BASE_USER_DIR / "TEMP")
LOGDIR      = str(BASE_USER_DIR / "logs")
LOGFILE     = str(BASE_USER_DIR / "logs" / "simple-log.txt")