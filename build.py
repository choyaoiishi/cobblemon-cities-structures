from pathlib import Path
import json
import re
import zipfile


src_dir = Path("src")
dist_dir = Path("dist")

# list folders to skip (relative to src/)
exclude_dirs = [
    "data/ccs/src",
    "data/ccs/.vscode",
    "data/ccs/worldgen/src"
]


def get_version_from_changelog():
    changelog_file = src_dir / "changelog.md"

    if not changelog_file.exists():
        raise FileNotFoundError(f"Missing {changelog_file}")

    lines = changelog_file.read_text(encoding="utf-8-sig").splitlines()

    for line in lines:
        match = re.search(
            r"###\s+\d{2}-\d{2}-\d{4}\s*-\s*([^\s*]+)",
            line,
        )

        if match:
            return match.group(1)

    raise ValueError(
        f"Could not find a version in {changelog_file}. "
        "Expected a line like: **### 08-10-2026 - 1.0.09**"
    )


def update_version(version):
    # update fabric.mod.json
    fabric_file = src_dir / "fabric.mod.json"

    if not fabric_file.exists():
        raise FileNotFoundError(f"Missing {fabric_file}")

    with fabric_file.open("r", encoding="utf-8") as f:
        mod_info = json.load(f)

    mod_info["version"] = version

    with fabric_file.open("w", encoding="utf-8") as f:
        json.dump(mod_info, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # update META-INF/neoforge.mods.toml
    neoforge_file = src_dir / "META-INF" / "neoforge.mods.toml"

    if not neoforge_file.exists():
        raise FileNotFoundError(f"Missing {neoforge_file}")

    toml = neoforge_file.read_text(encoding="utf-8")

    pattern = (
        r'(modId\s*=\s*"cobblemon_cities_structures"'
        r'\s*,\s*version\s*=\s*")[^"]*(")'
    )

    updated_toml, count = re.subn(
        pattern,
        rf"\g<1>{version}\g<2>",
        toml,
        count=1,
    )

    if count != 1:
        raise ValueError(
            f"Could not find the version for "
            f"cobblemon_cities_structures in {neoforge_file}"
        )

    neoforge_file.write_text(updated_toml, encoding="utf-8")

    return mod_info


def is_excluded(file_path):
    if file_path.suffix in (".code-workspace", ".py", ".cmd"):
        return True

    # check if file is inside an excluded folder
    rel_path = file_path.relative_to(src_dir)
    rel_str = rel_path.as_posix()

    for exclude in exclude_dirs:
        if rel_str == exclude or rel_str.startswith(exclude + "/"):
            return True

    return False


def main():
    version = get_version_from_changelog()
    mod_info = update_version(version)

    name = mod_info.get("name")

    if not name:
        raise ValueError("fabric.mod.json is missing 'name'")

    dist_dir.mkdir(parents=True, exist_ok=True)
    output_file = dist_dir / f"{name}-{version}.jar"

    if output_file.exists():
        output_file.unlink()

    with zipfile.ZipFile(
        output_file,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as jar:
        for file in src_dir.rglob("*"):
            if file.is_file() and not is_excluded(file):
                arcname = file.relative_to(src_dir)
                jar.write(file, arcname)

    print(f"Version: {version}")
    print(f"Built: {output_file}")


if __name__ == "__main__":
    main()