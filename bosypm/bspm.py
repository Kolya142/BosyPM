#!/usr/bin/python3
import json
import subprocess
import tarfile
import pathlib
import sys
import os

argv = sys.argv
argc = len(argv)
HOME = os.environ["HOME"]

if argc < 3 or argv[1][0] != '-':
    print(f"Usage: {argv[0]} -[SUsb] <file/link>")
    sys.exit(1)

args = argv[1][1:]

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
                    if old_ver == pkg["version"]:
                        print(f"Do you want reinstall {pkg["title"]} {old_ver}(Y/?)?", end="")
                    else:
                        print(f"Do you want replace {pkg["title"]} {old_ver} with {pkg["version"]}(Y/?)?", end="")
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

if 'U' in args:
    os.system("curl https://raw.githubusercontent.com/Kolya142/BosyPM/refs/heads/main/bosypm.tar.xz -o /tmp/bosypm-package.tar.xz")
    try:
        install("/tmp/bosypm-package.tar.xz")
    finally:
        os.system("rm /tmp/bosypm-package.tar.xz")

if 'S' in args:
    subprocess.run(["curl", argv[2], "-o", "/tmp/bosypm-package.tar.xz"])
    try:
        install("/tmp/bosypm-package.tar.xz")
    finally:
        os.system("rm /tmp/bosypm-package.tar.xz")
