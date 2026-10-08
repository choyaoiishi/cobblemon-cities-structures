from pathlib import Path
import json
import re
import zipfile


SRC_DIR = Path("src")
DIST_DIR = Path("dist")


def get_version_from_changelog():
    changelog_file = SRC_DIR / "changelog.md"

    if not changelog_file.exists():
        raise FileNotFoundError(f"Missing {changelog_file}")

    lines = changelog_file.read_text(encoding="utf-8-sig").splitlines()

    for line in lines:
        # Matches:
        # **### 08-10-2026 - 1.0.09**
        # ### 08-10-2026 - 1.0.09
        # ### 08-10-2026 - 1.0.09 **
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
    # Update fabric.mod.json
    fabric_file = SRC_DIR / "fabric.mod.json"

    if not fabric_file.exists():
        raise FileNotFoundError(f"Missing {fabric_file}")

    with fabric_file.open("r", encoding="utf-8") as f:
        mod_info = json.load(f)

    mod_info["version"] = version

    with fabric_file.open("w", encoding="utf-8") as f:
        json.dump(mod_info, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # Update META-INF/neoforge.mods.toml
    neoforge_file = SRC_DIR / "META-INF" / "neoforge.mods.toml"

    if not neoforge_file.exists():
        raise FileNotFoundError(f"Missing {neoforge_file}")

    toml = neoforge_file.read_text(encoding="utf-8")

    # Update the version in the mod declaration only.
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


def main():
    # changelog.md is the single source of truth for the version.
    version = get_version_from_changelog()

    # Keep both mod metadata files in sync.
    mod_info = update_version(version)

    name = mod_info.get("name")

    if not name:
        raise ValueError("fabric.mod.json is missing 'name'")

    # Create dist directory
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    output_file = DIST_DIR / f"{name}-{version}.jar"

    # Remove existing output
    if output_file.exists():
        output_file.unlink()

    # Create JAR (JAR files are ZIP archives)
    with zipfile.ZipFile(
        output_file,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as jar:
        for file in SRC_DIR.rglob("*"):
            if file.is_file():
                # Store paths relative to src/
                arcname = file.relative_to(SRC_DIR)
                jar.write(file, arcname)

    print(f"Version: {version}")
    print(f"Built: {output_file}")


if __name__ == "__main__":
    main()
