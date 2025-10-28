from abc import ABC, abstractmethod
from pypdf import PdfReader  
from docx import Document
from utils.logger import Logger

logger = Logger.get_logger()

class Parser(ABC):
    @abstractmethod
    def file_to_text(self, file_obj) -> str:
        """ file : starlette.datastructures.UploadFile"""
        pass

class PDFParser(Parser):
    def file_to_text(self, file_obj) -> str:
        logger.debug(f"Parsing PDF File.")
        try:
            text = ""
            reader = PdfReader(file_obj)
            for page in reader.pages:
                content = page.extract_text()
                text += f"{content}\n"
            logger.debug("Finished parsing PDF file")
            return text
        except Exception as e:
            logger.error(f"An error happend while parsing PDF: {e}")

class DOCXParser(Parser):
    def file_to_text(self, file_obj) -> str:
        logger.debug(f"Parsing DOCX File.")
        try:
            doc = Document(file_obj)
            text_chunks = []

            for block in doc.element.body:
                if block.tag.endswith("p"):
                    paragraph = block.xpath(".//w:t")
                    text = "".join([t.text for t in paragraph if t.text])
                    if text.strip():
                        text_chunks.append(text)
                elif block.tag.endswith("tbl"):
                    for table in doc.tables:
                        text_chunks.append(self._parse_tables(table))
                    break
            full_text = "\n".join(text_chunks)
            logger.debug("Finished parsing DOCX file")
            return full_text.strip()
        except Exception as e:
            logger.error(f"An error happend while parsing DOCX: {e}")
    
    def _parse_tables(self, table) -> str:
        table_text = ["\n[TABLE START]"]

        for row in table.rows:
            row_data = []
            for cell in row.cells:
                cell_text = " ".join(cell.text.split())
                row_data.append(cell_text)
            table_text.append(" | ".join(row_data))

        table_text.append("[TABLE END]\n")
        return "\n".join(table_text)


class TXTParser(Parser):
    def file_to_text(self, file_obj) -> str:
        logger.debug(f"Parsing TXT File.")
        try:
            content = file_obj.read()
            if isinstance(content, bytes):
                content = content.decode("utf-8")
            logger.debug("Finished parsing TXT file")
            return content
        except Exception as e:
            logger.error(f"An error happend while parsing TXT: {e}")

class FileParser:
    def parse_file(self, file_obj) -> str:
        try:
            parser = self._select_parser(file_obj)
            if parser:
                return parser.file_to_text(file_obj.file)
            else:
                return "UNSUPPORTED FILE"
        except Exception as e:
            logger.error(f"An error in FileParser: {e}")

    def _select_parser(self, file_obj) -> Parser:
        parser = None 
        if file_obj.filename.endswith("pdf"):
            parser = PDFParser()
        elif file_obj.filename.endswith("docx"):
            parser = DOCXParser()
        elif file_obj.filename.endswith("txt"):
            parser = TXTParser()
        else:
            logger.warning("Unsupported File.")
        return parser