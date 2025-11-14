import os
import shutil
import tempfile
from pathlib import Path
from typing import List

from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from langchain_community.document_loaders import (
    CSVLoader,
    DirectoryLoader,
    Docx2txtLoader,
    PyMuPDFLoader,
    TextLoader,
)

from .config import get_config
from langchain_core.documents import Document
from dotenv import load_dotenv
import base64

config = get_config()
load_dotenv()


HANDWRITTEN_FOLDER = "handwritten_notes"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
IMAGE_OUTPUT_DIR = config.image_output_dir
IMAGE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_img_content(img_path: str) -> str:
    """Send an image to Azure and return the extracted text."""
    # if not all([config.azure_vision_endpoint, config.azure_vision_key]):
    #     raise ValueError(
    #         "Azure Vision endpoint and key must be configured in environment variables."
    #     )

    client = ImageAnalysisClient(
        endpoint=os.getenv('VISION_ENDPOINT'),
        credential=AzureKeyCredential(os.getenv('VISION_KEY')),
    )

    with open(img_path, "rb") as f:
        image_data = f.read()

    result = client.analyze(
        image_data=image_data, visual_features=[VisualFeatures.READ]
    )

    if result.read and result.read.blocks:
        return "\n".join(
            [line.text for block in result.read.blocks for line in block.lines]
        )

    return "No textual content could be extracted from this image."

def convert_pdf_to_images(
    pdf_path: str, output_folder: Path, dpi: int = 300
) -> List[str]:
    """Convert each page of a PDF to a JPEG image and return the image paths."""
    output_folder.mkdir(parents=True, exist_ok=True)
    images = convert_from_path(pdf_path, dpi=dpi)

    image_paths: List[str] = []
    for index, image in enumerate(images, start=1):
        image_path = output_folder / f"page_{index:03d}.jpg"
        image.save(image_path, "JPEG")
        image_paths.append(str(image_path))

    return image_paths


def _create_handwritten_document(
    image_path: Path,
    handwritten_root: Path,
    relative_root: Path,
    page_number: int,
    content: str,
    source_type: str,
    original_source: Path,
) -> Document:
    note_segments = list(relative_root.parts)
    note_group = note_segments[0] if note_segments else image_path.stem
    note_section = "/".join(note_segments[1:]) if len(note_segments) > 1 else ""

    try:
        relative_path = image_path.relative_to(handwritten_root)
    except ValueError:
        relative_path = Path(os.path.relpath(image_path, handwritten_root))

    metadata = {
        "source": str(original_source),
        "image_path": str(image_path),
        "note_group": note_group,
        "note_section": note_section,
        "file_name": image_path.name,
        "page_number": page_number,
        "doc_type": source_type,
        "relative_path": str(relative_path),
    }

    return Document(page_content=content, metadata=metadata)


def _load_handwritten_notes(base_dir: Path) -> List[Document]:
    handwritten_root = base_dir / HANDWRITTEN_FOLDER
    if not handwritten_root.exists() or not handwritten_root.is_dir():
        return []

    handwritten_docs: List[Document] = []

    for current_root, _, files in os.walk(handwritten_root):
        current_path = Path(current_root)
        relative = current_path.relative_to(handwritten_root)

        image_files = sorted(
            f for f in files if Path(f).suffix.lower() in IMAGE_EXTENSIONS
        )
        pdf_files = sorted(f for f in files if Path(f).suffix.lower() == ".pdf")

        # Process standalone handwritten images
        for index, image_name in enumerate(image_files, start=1):
            image_path = current_path / image_name
            try:
                text = get_img_content(str(image_path))
            except Exception as exc:  # pragma: no cover - best effort logging
                text = f"Failed to transcribe image: {exc}"
            handwritten_docs.append(
                _create_handwritten_document(
                    image_path=image_path,
                    handwritten_root=handwritten_root,
                    relative_root=relative,
                    page_number=index,
                    content=text,
                    source_type="handwritten_image",
                    original_source=image_path,
                )
            )

        # Process PDFs inside handwritten notes by converting them to images first
        for pdf_name in pdf_files:
            pdf_path = current_path / pdf_name
            temp_dir = Path(
                tempfile.mkdtemp(prefix="pdf_images_", dir=IMAGE_OUTPUT_DIR)
            )
            try:
                image_paths = convert_pdf_to_images(str(pdf_path), temp_dir)
                for index, image_path in enumerate(sorted(image_paths), start=1):
                    try:
                        text = get_img_content(image_path)
                    except Exception as exc:  # pragma: no cover - best effort logging
                        text = f"Failed to transcribe PDF page image: {exc}"
                    handwritten_docs.append(
                        _create_handwritten_document(
                            image_path=Path(image_path),
                            handwritten_root=handwritten_root,
                            relative_root=relative,
                            page_number=index,
                            content=text,
                            source_type="handwritten_pdf_page",
                            original_source=pdf_path,
                        )
                    )
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)

    return handwritten_docs


def load_docs(
    base_dir: str = config.kb_path,
) -> List[Document]:
    base_path = Path(base_dir)
    docs: List[Document] = []

    # PDFs
    loader = DirectoryLoader(
        path=str(base_path),
        glob="**/*.pdf",
        loader_cls=PyMuPDFLoader,
        show_progress=True,
    )
    docs.extend(loader.load())

    # Text and Markdown
    loader = DirectoryLoader(
        path=str(base_path),
        glob="**/*.txt",
        loader_cls=TextLoader,
        show_progress=True,
    )
    docs.extend(loader.load())
    loader = DirectoryLoader(
        path=str(base_path),
        glob="**/*.md",
        loader_cls=TextLoader,
        show_progress=True,
    )
    docs.extend(loader.load())

    # Word documents
    loader = DirectoryLoader(
        path=str(base_path),
        glob="**/*.docx",
        loader_cls=Docx2txtLoader,
        show_progress=True,
    )
    docs.extend(loader.load())
    loader = DirectoryLoader(
        path=str(base_path),
        glob="**/*.doc",
        loader_cls=Docx2txtLoader,
        show_progress=True,
    )
    docs.extend(loader.load())

    # CSV files
    loader = DirectoryLoader(
        path=str(base_path),
        glob="**/*.csv",
        loader_cls=CSVLoader,
        show_progress=True,
    )
    docs.extend(loader.load())

    # Handwritten notes (images + embedded PDFs)
    docs.extend(_load_handwritten_notes(base_path))

    return docs


if __name__ == "__main__":
    text = get_img_content("/home/anujkumar/Downloads/rag_with_langchain/frontend/ai-chatbot-ui/WhatsApp Image 2025-11-11 at 11.19.24 AM.jpeg")
    print(f"Loaded text\n\n{text}\n\n documents.")
