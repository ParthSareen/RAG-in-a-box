from typing import List, Dict
from pathlib import Path
from pypdf import PdfReader
from icecream import ic

class PdfLoader:
    def __init__(self, directory_path: str):
        self.directory_path = Path(directory_path)

    def load(self) -> List[Dict[str, str]]:
        if not self.directory_path.is_dir():
            raise NotADirectoryError(f"The path {self.directory_path} is not a directory.")

        pdf_contents = []
        self._load_recursive(self.directory_path, pdf_contents)
        return pdf_contents

    def _load_recursive(self, current_path: Path, pdf_contents: List[Dict[str, str]]):
        for item in current_path.iterdir():
            if item.is_file() and item.suffix.lower() == '.pdf':
                try:
                    reader = PdfReader(str(item))
                    text_content = []

                    for page in reader.pages:
                        text_content.append(page.extract_text())

                    relative_path = item.relative_to(self.directory_path)
                    pdf_contents.append({
                        "doc_name": str(relative_path),
                        "content": "\n".join(text_content)
                    })
                except Exception as e:
                    print(f"Error processing {item}: {str(e)}")
            elif item.is_dir():
                self._load_recursive(item, pdf_contents)

if __name__ == "__main__":
    directory_path = input("Enter the path to your PDF directory: ")
    loader = PdfLoader(directory_path)
    all_pdf_contents = loader.load()
    ic(all_pdf_contents[0:5])

    # for filename, pages in all_pdf_contents:
    #     print(f"File: {filename}")
    #     for i, page_text in enumerate(pages, 1):
    #         print(f"  Page {i}: {page_text[:100]}...")  # Print first 100 characters of each page