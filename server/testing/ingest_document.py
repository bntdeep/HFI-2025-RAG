import asyncio
from dotenv import load_dotenv

load_dotenv()

from src.rag import configure_logging
from src.ingestion.pipeline import ingest_document

configure_logging()

async def main():
  result = await ingest_document(
      "/Users/Artsiom_Sushchenia/Library/CloudStorage/OneDrive-EPAM/Learn/trainings/AI Architect/module 3. rag/hfi_rag/documents/Albania-Burundi.pdf",
      document_name="2025 Human Freedom Index Albania-Burundi",
  )
  print(result.summary())

asyncio.run(main())