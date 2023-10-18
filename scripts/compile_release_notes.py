import click
import markdown
import os


README_FILENAME = "README.txt"
CHANGELOG_FOLDER = "./changelog"
UNRELEASED_FOLDER = f"{CHANGELOG_FOLDER}/unreleased"


@click.command()
@click.option("--version", help="The version releasing the changes")
def process(version: str) -> None:
    print(f"Creating release notes for version {version}")
    print("Processing changelog files")
    result_text = merge_files_in_folder(UNRELEASED_FOLDER, skip=[README_FILENAME])
    print("Converting to html")
    text_with_header = append_header(result_text, get_header_text(version), 1)
    write_html_output(version, text_with_header)
    print("Cleaning up")
    make_folder_empty(UNRELEASED_FOLDER, skip=[README_FILENAME])


def append_header(text: str, header: str, imp: int) -> str:
    return "\n".join([f"{''.join(['#' for _ in range(imp)])}{header}", text])


def merge_files_in_folder(folder: str, skip: list[str]) -> str:
    files: list[str] = []
    for file in os.listdir(folder):
        if file not in skip:
            abspath = os.path.abspath(f"{UNRELEASED_FOLDER}/{file}")
            print(f"Processing {abspath}")
            file_content = read_markdown_file(abspath)
            file_with_header = append_header(file_content, file, 2)
            files.append(file_with_header)
    return "\n".join(files)


def make_folder_empty(folder: str, skip: list[str]) -> None:
    for file in os.listdir(folder):
        if file not in skip:
            os.remove(f"{folder}/{file}")


def write_html_output(version: str, text: str) -> None:
    new_folder = f"{CHANGELOG_FOLDER}/{version}"
    try:
        os.mkdir(new_folder)
    except FileExistsError:
        raise ValueError(f"Changelog entry for version '{version}', already exists!")
    html = markdown.markdown(text)
    with open(f"{new_folder}/release_notes.html", "w") as file:
        file.write(html)


def read_markdown_file(path: str) -> str:
    with open(path) as file:
        return file.read()


def get_header_text(version: str) -> str:
    return f"Release notes version: {version}"


if __name__ == "__main__":
    process()
