from typing import List
import PyPDF2
from io import BytesIO
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config import Config
import logging

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
        )

    def extract_text_from_pdf(self, pdf_content: bytes, filename: str) -> str:
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text.strip():
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            
            if not text.strip():
                raise ValueError("No text could be extracted from the PDF")
                
            logger.info(f"Extracted text from {filename}: {len(text)} characters")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from {filename}: {e}")
            raise

    def create_documents(self, text: str, filename: str) -> List[Document]:
        try:
            chunks = self.text_splitter.split_text(text)
            documents = []
            
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    doc = Document(
                        page_content=chunk,
                        metadata={
                            "source": filename,
                            "chunk_index": i,
                            "total_chunks": len(chunks)
                        }
                    )
                    documents.append(doc)
            
            logger.info(f"Created {len(documents)} documents from {filename}")
            return documents
            
        except Exception as e:
            logger.error(f"Error creating documents from {filename}: {e}")
            raise

    def process_pdf(self, pdf_content: bytes, filename: str) -> List[Document]:
        text = self.extract_text_from_pdf(pdf_content, filename)
        documents = self.create_documents(text, filename)
        return documents 