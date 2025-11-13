"""
Document loader for processing knowledge base files.
"""
import os
from typing import List, Dict
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger(__name__)


class KnowledgeBaseLoader:
    """Load and process knowledge base documents."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize the knowledge base loader.
        
        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def load_from_file(self, file_path: str, metadata: Dict = None) -> List[Document]:
        """
        Load content from a single file.
        
        Args:
            file_path: Path to the file
            metadata: Additional metadata to attach
            
        Returns:
            List of Document objects
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            base_metadata = {
                "source": os.path.basename(file_path),
                "file_path": file_path
            }
            if metadata:
                base_metadata.update(metadata)
            
            # Create document
            doc = Document(page_content=content, metadata=base_metadata)
            
            # Split into chunks
            chunks = self.text_splitter.split_documents([doc])
            
            logger.info(f"Loaded {len(chunks)} chunks from {file_path}")
            return chunks
            
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {str(e)}")
            return []
    
    def load_from_directory(self, directory_path: str) -> List[Document]:
        """
        Load all text files from a directory.
        
        Args:
            directory_path: Path to directory
            
        Returns:
            List of Document objects
        """
        all_documents = []
        
        if not os.path.exists(directory_path):
            logger.warning(f"Directory not found: {directory_path}")
            return all_documents
        
        for filename in os.listdir(directory_path):
            if filename.endswith('.txt') or filename.endswith('.md'):
                file_path = os.path.join(directory_path, filename)
                metadata = {"category": filename.replace('.txt', '').replace('.md', '')}
                documents = self.load_from_file(file_path, metadata)
                all_documents.extend(documents)
        
        logger.info(f"Loaded total {len(all_documents)} chunks from {directory_path}")
        return all_documents
    
    def create_cv_document(self, cv_text: str) -> List[Document]:
        """
        Create structured documents from CV text.
        
        Args:
            cv_text: Raw CV text
            
        Returns:
            List of Document objects
        """
        sections = self._parse_cv_sections(cv_text)
        documents = []
        
        for section_name, content in sections.items():
            metadata = {
                "source": "cv",
                "section": section_name,
                "type": "profile"
            }
            doc = Document(page_content=content, metadata=metadata)
            chunks = self.text_splitter.split_documents([doc])
            
            # Update metadata with section info
            for chunk in chunks:
                chunk.metadata.update(metadata)
            
            documents.extend(chunks)
        
        logger.info(f"Created {len(documents)} CV document chunks")
        return documents
    
    def _parse_cv_sections(self, cv_text: str) -> Dict[str, str]:
        """
        Parse CV into sections.
        
        Args:
            cv_text: Raw CV text
            
        Returns:
            Dictionary of section name to content
        """
        sections = {}
        current_section = "summary"
        current_content = []
        
        section_headers = [
            "PROFESSIONAL SUMMARY",
            "KEY PROJECTS",
            "EDUCATION",
            "PROFESSIONAL EXPERIENCE",
            "TECHNICAL SKILLS",
            "CERTIFICATIONS"
        ]
        
        for line in cv_text.split('\n'):
            line = line.strip()
            
            # Check if this is a section header
            is_header = False
            for header in section_headers:
                if header in line.upper():
                    # Save previous section
                    if current_content:
                        sections[current_section] = '\n'.join(current_content)
                    
                    # Start new section
                    current_section = header.lower().replace(' ', '_')
                    current_content = []
                    is_header = True
                    break
            
            if not is_header and line:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
