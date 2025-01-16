try:
    from autotask.nodes import Node, GeneratorNode, ConditionalNode, register_node
except ImportError:
    from stub import Node, GeneratorNode, ConditionalNode, register_node

from typing import Dict, Any, Generator, List
from PyPDF2 import PdfReader



@register_node
class PDFTextExtractorNode(Node):
    """Extract text from PDF file page by page"""
    NAME = "PDF Text Extractor"
    DESCRIPTION = "Extract text content from PDF file and output as array of strings (one string per page)"

    INPUTS = {
        "pdf_file": {
            "label": "PDF File Path",
            "description": "Path to the PDF file to process",
            "type": "STRING",
            "required": True
        }
    }

    OUTPUTS = {
        "text_array": {
            "label": "Text Content Array",
            "description": "Array of strings, each element contains text from one page",
            "type": "LIST"
        }
    }

    def execute(self, node_inputs: Dict[str, Any], workflow_logger) -> Dict[str, Any]:
        try:
            pdf_path = node_inputs["pdf_file"]
            workflow_logger.info(f"Start processing PDF file: {pdf_path}")
            
            # Open and read PDF file
            reader = PdfReader(pdf_path)
            text_array = []
            
            # Extract text from each page
            for page_num in range(len(reader.pages)):
                workflow_logger.debug(f"Processing page {page_num + 1}")
                page = reader.pages[page_num]
                text = page.extract_text()
                text_array.append(text)
            
            workflow_logger.info(f"Successfully extracted text from {len(text_array)} pages")
            return text_array
            
        except Exception as e:
            error_msg = f"PDF text extraction failed: {str(e)}"
            workflow_logger.error(error_msg)
            return {
                "success": False,
                "error_message": error_msg
            }


if __name__ == "__main__":
    # Setup basic logging
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    
    # Test PDFTextExtractorNode
    print("\n4. Testing PDFTextExtractorNode:")
    pdf_node = PDFTextExtractorNode()
    pdf_result = pdf_node.execute({"pdf_path": "test.pdf"}, logger)
    if pdf_result["success"]:
        for i, page_text in enumerate(pdf_result["text_array"]):
            print(f"Page {i+1} content length: {len(page_text)} characters")


