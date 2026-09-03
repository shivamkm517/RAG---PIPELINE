from docling.document_converter import DocumentConverter


def parse_pdf(file_path: str):
    converter = DocumentConverter()

    result = converter.convert(file_path)

    return result.document