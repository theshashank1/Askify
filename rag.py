
import traceback

from llm import ModelService
from utils.pdf_processor import load_pdf



from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

class ChatService:
    def __init__(self, pdf_path):
        self.service = ModelService()
        self.llm = self.service.get_llm_model()

        if self.llm is None:
            raise Exception('LLM not found')

        try:
            doc = load_pdf(pdf_path)

            # This will split the document into chunks with a specified size and overlap
            split = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                length_function=len
            )

            # Splitting the document into chunks for better processing
            split_docs = split.split_documents(doc)

            print(f"Number of document chunks: {len(split_docs)}")

            self.embeddings = self.service.get_embedding_model()

            # Creating a Chroma vector database from the document chunks and embeddings
            self.vectorstore = Chroma.from_documents(
                documents=split_docs,  # Data: the split document chunks
                embedding=self.embeddings,  # Embedding model
                persist_directory="./chroma_db"  # Directory to save the vector database
            )

            self.retriever = self.vectorstore.as_retriever()


            # Define a template for the prompt
            template = """
            Answer the question based only on the following context:

            {context}

            Question: {question}
            """

            # Create a prompt template from the defined template
            self.prompt = ChatPromptTemplate.from_template(template)

            # Define the chain or pipeline to execute the retrieval, prompt, model, and output parsing
            self.chain = (
                {"context": self.retriever, "question": RunnablePassthrough()}
                | self.prompt
                | self.llm
                | StrOutputParser()
            )

        except Exception as e:
            print(f"An error occurred during initialization: {str(e)}")
            traceback.print_exc()
            raise

    def chat(self, question):
        try:
            # Invoke the chain with the question
            output = self.chain.invoke(question)
            # json_data = json.loads(output)
            # return json_data
            return output
        except Exception as e:
            print(f"An error occurred during chat: {str(e)}")
            traceback.print_exc()
            return "I'm sorry, but I encountered an error while processing your question."

if __name__ == "__main__":
    try:
        # pdf_path = r"C:\Users\hp\Downloads\pdf-sample.pdf"  # Replace with the correct path to your PDF
        pdf_path=r"E:/Music_and_Movie_Recommendation_System.pdf"
        chat_service = ChatService(pdf_path)

        while True:
            question = input("Enter your question (or 'quit' to exit): ")
            if question.lower() == 'quit':
                break
            response = chat_service.chat(question)
            print("Response:", response)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        traceback.print_exc()