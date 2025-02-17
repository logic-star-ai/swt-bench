from src.constants import MAP_VERSION_TO_INSTALL

all_pre_installs = set()
for repo, version_map in MAP_VERSION_TO_INSTALL.items():
    for version, install in version_map.items():
        if "pre_install" in install:
            for pre_install in install["pre_install"]:
                all_pre_installs.add((pre_install, repo))
for pre_install in all_pre_installs:
    if "sed" in pre_install[0]:
        print(pre_install)

# all relevant files. "setup.py", "tox.ini" "pyproject.toml"