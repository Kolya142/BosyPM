#!/usr/bin/python3
import json
import subprocess
import tarfile
import pathlib
import sys
import os

import requests

argv = sys.argv
argc = len(argv)
HOME = os.environ["HOME"]
REPOS = [
    "http://bosyprograms.org/pkgs/index.json"
]

if argc < 2 or argv[1][0] != '-':
    print(f"Usage: {argv[0]} -[SULVsub] <file/link>")
    sys.exit(1)

args = argv[1][1:]

def compare_versions(old, new):
    old_major, old_minor, old_patch = map(int, old.split('.'))
    new_major, new_minor, new_patch = map(int, new.split('.'))
    if (old_major, old_minor, old_patch) == (new_major, new_minor, new_patch):
        return 0
    elif (old_major > new_major) or (old_major >= new_major and old_minor > new_minor) or (old_major >= new_major and old_minor >= new_minor and old_patch > new_patch):
        return -1
    else:
        return 1

def install(path):
    os.system("mkdir -p /tmp/bosypm-package")
    os.system(f"mkdir -p {str(pathlib.Path(HOME) / f".config/bosypm")}")
    try:
        if subprocess.run(["tar", "-xvJf", path, "-C", "/tmp/bosypm-package"]).returncode:
            print("Failed to unzip package")
            return

        with open("/tmp/bosypm-package/pkg.json") as f:
            pkg = json.load(f)
            try:
                lock_path = str(pathlib.Path(HOME) / f".config/bosypm/.lock{pkg["title"]}")

                if "desc" in pkg and pkg["desc"]:
                    print("Description:\n" + pkg["desc"])

                if os.path.exists(lock_path):
                    old_ver = open(lock_path).read()
                    old_major, old_minor, old_patch = map(int, old_ver.split('.'))
                    new_major, new_minor, new_patch = map(int, pkg["version"].split('.'))
                    if old_ver == pkg["version"]:
                        print(f"Do you want reinstall {pkg["title"]} {old_ver}(Y/?)?", end="")
                    elif (old_major > new_major) or (old_major >= new_major and old_minor > new_minor) or (old_major >= new_major and old_minor >= new_minor and old_patch > new_patch):
                        print(f"\x1b[32mWARNING\x1b[0m Do you want downgrade from {pkg["title"]} {old_ver} to {pkg["version"]}(Y/?)?", end="")
                    else:
                        print(f"Do you want upgrade from {pkg["title"]} {old_ver} to {pkg["version"]}(Y/?)?", end="")
                else:
                    print(f"Do you want install {pkg["title"]} {pkg["version"]}(Y/?)?", end="")

                if input()[0].upper() == 'Y':
                    with open(lock_path, 'w') as lockf:
                        lockf.write(pkg["version"])
                    entry = str(pathlib.Path("/tmp/bosypm-package/") / pkg["entry"])
                    os.chmod(entry, 0o755)
                    subprocess.run([entry], cwd="/tmp/bosypm-package/")
            except Exception as e:
                print(f"Exception during installation:\n{e}")
    finally:
        os.system("rm -rf /tmp/bosypm-package")

if 'b' in args:
    name = argv[2].replace('\\', '-').replace('/', '-')
    while name[-1] == '-':
        name = ''.join(name[:-1])
    with tarfile.open(f"{name}.tar.xz", 'w:xz') as t:
        for file in os.listdir(argv[2]):
            t.add(str(pathlib.Path(argv[2]) / file), file)

if 's' in args:
    install(argv[2])

if 'u' in args:
    os.system("curl http://bosyprograms.org/pkgs/bosypm.tar.xz -o /tmp/bosypm-package.tar.xz")
    try:
        install("/tmp/bosypm-package.tar.xz")
    finally:
        os.system("rm /tmp/bosypm-package.tar.xz")

if 'U' in args:
    for repo in REPOS:
        pkgs = requests.get(repo).json()
        print(f"Repository {repo}")
        empty = True
        for pkg in pkgs:
            try:
                lock_path = str(pathlib.Path(HOME) / f".config/bosypm/.lock{pkg["title"]}")
                if os.path.exists(lock_path):
                    old_ver = open(lock_path).read()
                    cv = compare_versions(old_ver, pkg["version"])
                    if cv == 1:
                        empty = False
                        print(f"Do you want update {pkg["title"]} from ({old_ver}) to ({pkg["version"]})?")
                        if input()[0].upper() == 'Y':
                            try:
                                subprocess.run(["curl", pkg["link"], "-o", "/tmp/bosypm-package.tar.xz"])
                                install("/tmp/bosypm-package.tar.xz")
                            finally:
                                os.system("rm /tmp/bosypm-package.tar.xz")
            except Exception:
                pass
        if empty:
            print("There nothing to update")

if 'V' in args:
    print('0.0.4')

if 'L' in args:
    for repo in REPOS:
        pkgs = requests.get(repo).json()
        print(f"Repository {repo}")
        empty = True
        for pkg in pkgs:
            print(pkg["title"], pkg["version"])

if 'S' in args:
    for repo in REPOS:
        pkgs = requests.get(repo).json()
        print(f"Repository {repo}")
        empty = True
        for pkg in pkgs:
            if pkg["title"] != argv[2]:
                continue
            empty = False
            try:
                subprocess.run(["curl", pkg["link"], "-o", "/tmp/bosypm-package.tar.xz"])
                try:
                    install("/tmp/bosypm-package.tar.xz")
                finally:
                    os.system("rm /tmp/bosypm-package.tar.xz")
            except Exception:
                pass
        if empty:
            print(f"No such {argv[2]} package")
            sys.exit(1)
