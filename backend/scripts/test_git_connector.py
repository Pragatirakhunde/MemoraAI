from app.connectors.git.repository import (
    GitRepositoryConnector,
)


connector = GitRepositoryConnector(
    url="https://github.com/octocat/Hello-World.git",
    branch="master",
)

print("Valid:", connector.validate())

print("\nSyncing repository...")

connector.sync_repository()

print("Repository synced.")

files = connector.list_files()

print(f"\nFiles found: {len(files)}")

for file in files[:10]:
    print(
        f"- {file.name} | "
        f"{file.extension} | "
        f"{file.size} bytes"
    )

if files:
    print("\n--- First File Content ---")

    content = connector.read_file(
        files[0].path
    )

    print(content[:1000])