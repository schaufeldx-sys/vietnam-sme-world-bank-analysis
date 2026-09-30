"""Verify all required packages import successfully."""
import importlib
mods = [
    'pandas', 'numpy', 'matplotlib', 'seaborn', 'scipy',
    'openpyxl', 'xlrd', 'tabulate', 'mistune', 'reportlab',
    'pypdf', 'psycopg2',
]
all_ok = True
for m in mods:
    try:
        mod = importlib.import_module(m)
        v = getattr(mod, '__version__', '?')
        print(f'  OK   {m:15} {v}')
    except ImportError as e:
        print(f'  FAIL {m}: {e}')
        all_ok = False
print()
print('ALL OK' if all_ok else 'SOME FAILED')
