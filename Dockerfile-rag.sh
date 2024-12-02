source .venv/bin/activate

sudo apt-get install libsqlite3-dev

uv pip install pandas numpy boto3 openpyxl xlsxwriter 
uv pip install sentence-transformers transformers InstructorEmbedding 

uv pip install cohere langchain chromadb unstructured 
uv pip install -q langchain-text-splitters -U langchain-community 
uv pip install langchain-chroma langchain-cohere 

uv pip install llama-index pysqlite3 

uv pip install -q llama-index-embeddings-huggingface 
uv pip install -q llama-index-embeddings-instructor 
uv pip install -q llama-index-llms-cohere 
uv pip install "openinference-instrumentation-llama-index>=2" "opentelemetry-proto>=1.12.0" opentelemetry-exporter-otlp opentelemetry-sdk

uv pip install arize-phoenix