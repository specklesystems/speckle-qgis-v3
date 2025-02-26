import sys


def patch_installer(tag):
    """Patches the installer with the correct connector version and specklepy version"""

    metadata = "metadata.txt"

    with open(metadata, "r") as file:
        lines = file.readlines()
        new_lines = []

        for i, line in enumerate(lines):
            if "version=" in line:
                line = f"version={tag}\n"
            if "experimental=" in line:
                if "-" in tag:
                    line = f"experimental=True\n"
                elif len(tag.split(".")) == 3 and tag != "0.0.99" and "-" not in tag:
                    line = f"experimental=False\n"  # .split("-")[0]
            new_lines.append(line)

        with open(metadata, "w") as file:
            file.writelines(new_lines)
            print(f"Patched metadata v{tag} ")
    file.close()


def main():
    if len(sys.argv) < 2:
        return

    tag = sys.argv[1]
    print(f"Patching version: {tag}")
    patch_installer(tag)


if __name__ == "__main__":
    main()
