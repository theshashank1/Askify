import traceback
from llm import ModelService
from utils.pdf_processor import load_pdf

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import uuid


class ChatService :
    """
    Service for answering questions based on PDF content.
    """

    def __init__(self, pdf_path) :
        """
        Initializes by loading a PDF, splitting it into chunks, and setting up retrieval.

        Args:
            pdf_path (str): Path to the PDF file.

        Raises:
            Exception: If LLM is missing or an error occurs.
        """
        self.service = ModelService()
        self.llm = self.service.get_llm_model()

        if not self.llm:
            raise Exception('LLM not found')

        try :
            # Load and split PDF into chunks
            doc = load_pdf(pdf_path)
            if not doc :
                raise Exception("Failed to load PDF document")

            # Split documents with validation
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                length_function=len,
                add_start_index=True
            )
            split_docs = splitter.split_documents(doc)

            if not split_docs:
                raise Exception("No content extracted from PDF")

            # Extract text and metadata separately
            texts = [doc.page_content for doc in split_docs]
            metadatas = [doc.metadata for doc in split_docs]

            # Generate unique IDs for each chunk
            ids = [str(uuid.uuid4()) for _ in range(len(texts))]

            # Set up embeddings
            self.embeddings = self.service.get_embedding_model()
            if not self.embeddings :
                raise Exception("Embedding model not initialized")

            # Initialize vector store with explicit parameters
            self.vectorstore = Chroma(
                collection_name="pdf_collection",
                embedding_function=self.embeddings,
                persist_directory="./chroma_db"
            )

            # Add documents with explicit parameters
            self.vectorstore.add_texts(
                texts=texts,
                metadatas=metadatas,
                ids=ids
            )

            # Set up retriever with search parameters
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4}
            )

            # Define prompt template with improved context handling
            template = """Answer the question based only on the provided context. If the answer cannot be found in the context, say "I cannot answer this based on the provided context."

Context:
{context}

Question: {question}

Answer:"""

            self.prompt = ChatPromptTemplate.from_template(template)

            # Set up the chain with proper error handling
            self.chain = (
                    {
                        "context" : self.retriever,
                        "question" : RunnablePassthrough()
                    }
                    | self.prompt
                    | self.llm
                    | StrOutputParser()
            )

        except Exception as e :
            print(f"Initialization error: {str(e)}")
            traceback.print_exc()
            raise

    def chat(self, question) :
        """
        Answers a question based on PDF content.

        Args:
            question (str): User question.

        Returns:
            str: Answer or error message.
        """
        if not question or not question.strip() :
            return "Please provide a valid question."

        try :
            return self.chain.invoke(question)
        except Exception as e :
            error_msg = f"Error processing your question: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            return error_msg


if __name__ == "__main__" :
    try :
        pdf_path = r"E:/Music_and_Movie_Recommendation_System.pdf"
        chat_service = ChatService(pdf_path)
        print("Chat service initialized successfully. Type 'quit' to exit.")

        while True :
            question = input("\nEnter your question: ").strip()
            if question.lower() == 'quit' :
                print("Exiting chat service...")
                break
            print("\nResponse:", chat_service.chat(question))

    except Exception as e :
        print(f"Fatal error: {str(e)}")
        traceback.print_exc()