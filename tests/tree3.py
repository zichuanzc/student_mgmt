"""获取3层目录树形结构"""

import os
import sys

root = sys.argv[1] if len(sys.argv) > 1 else "."
max_level = int(sys.argv[2]) if len(sys.argv) > 2 else 3   # 3 = 根下三层

SKIP = {".venv", "venv", "__pycache__", "node_modules", ".git",
        ".idea", ".pytest_cache", "dist", "build", ".mypy_cache"}

def walk(path, level, prefix=""):
    if level > max_level:
        return
    try:
        entries = sorted(os.listdir(path),
                         key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))
    except PermissionError:
        print(f"{prefix}[权限不足]")
        return
    visible = [e for e in entries if e not in SKIP]
    for i, name in enumerate(visible):
        full = os.path.join(path, name)
        last = i == len(visible) - 1
        branch = "└── " if last else "├── "
        is_dir = os.path.isdir(full)
        print(f"{prefix}{branch}{name}{'/' if is_dir else ''}")
        if is_dir:
            walk(full, level + 1, prefix + ("    " if last else "│   "))

print(f"{os.path.basename(os.path.abspath(root))}/")
walk(root, 1)
