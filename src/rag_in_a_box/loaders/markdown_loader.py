from typing import Dict, List
from pathlib import Path

class MarkdownLoader:
    def __init__(self, directory_path: str):
        self.directory_path = Path(directory_path)

    def load(self) -> List[Dict[str, str]]:
        if not self.directory_path.is_dir():
            raise NotADirectoryError(f"The path {self.directory_path} is not a directory.")

        markdown_contents = []
        self._load_recursive(self.directory_path, markdown_contents)
        return markdown_contents

    def _load_recursive(self, current_path: Path, markdown_contents: List[Dict[str, str]]):
        for item in current_path.iterdir():
            if item.is_file() and item.suffix.lower() == '.md':
                try:
                    with item.open('r', encoding='utf-8') as file:
                        content = file.read()
                    relative_path = item.relative_to(self.directory_path)
                    markdown_contents.append({
                        "doc_name": str(relative_path),
                        "content": content
                    })
                except Exception as e:
                    print(f"Error processing {item}: {str(e)}")
            elif item.is_dir():
                self._load_recursive(item, markdown_contents)


if __name__ == "__main__":
    directory_path = input("Enter the path to your Markdown directory: ")
    loader = MarkdownLoader(directory_path)
    all_md_contents = loader.load()
    for doc in all_md_contents:
        print(f"File: {doc['doc_name']}")
        print(f"Content preview: {doc['content'][:100]}...")  # Print first 100 characters