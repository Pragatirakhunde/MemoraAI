from pathlib import Path

from app.connectors.local.directory import LocalDirectoryConnector


# Project root:
# enterprise-memory-engine/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

data_path = (
    PROJECT_ROOT
    / "datasets"
    / "sample_company"
    / "documentation"
)

print("Checking directory:")
print(data_path)
print("Exists:", data_path.exists())
print("Is directory:", data_path.is_dir())


connector = LocalDirectoryConnector(str(data_path))

print("\nValid:", connector.validate())

files = connector.list_files()

print(f"Files found: {len(files)}")

for file in files:
    print(
        f"- {file.name} | "
        f"{file.extension} | "
        f"{file.size} bytes"
    )

if files:
    content = connector.read_file(files[0].path)

    print("\n--- File Content ---")
    print(content)