# Application Structure Guide

This document explains the refactored professional structure of the Business Intelligence Chatbot.

## Directory Structure

```
src/app/
├── config/                 # Configuration and settings
│   ├── settings.py         # Environment variables, constants, paths
│   ├── models.py           # LLM model initialization logic
│   └── prompts/            # Prompt templates
│       └── templates.py    # SQL generation and response prompts
│
├── core/                   # Core business logic
│   ├── database.py         # Database connection and query execution
│   ├── llm_client.py       # LLM interaction handling
│   └── rag.py              # RAG implementation for schema retrieval
│
├── utils/                  # Utility scripts
│   ├── database_setup_single_table.py
│   └── database_setup_multiple_tables.py
│
├── db/                     # Database-related utilities (reserved for future use)
│
└── Application Files:
    ├── app_single_basic.py     # Single table without RAG
    ├── app_single_rag.py       # Single table with RAG
    ├── app_multi_basic.py      # Multiple tables without RAG
    └── app_multi_rag.py        # Multiple tables with RAG
```

## Key Components

### Config Package
- **settings.py**: All configuration constants, environment variables, and paths
- **models.py**: Initialize LLM clients (OpenAI, Anthropic)
- **prompts/templates.py**: Store all prompt templates in one place

### Core Package
- **database.py**: 
  - `DatabaseConnection` class for managing connections
  - `execute_sql_query()` function for running queries
  
- **llm_client.py**:
  - `LLMClient` class handling both OpenAI and Anthropic models
  - Unified interface for generating responses
  
- **rag.py**:
  - `RAGEngine` class for vector store operations
  - Schema loading and chunking utilities
  - Similarity search for relevant schema retrieval

### Application Files
Each app file is a standalone Streamlit application that:
1. Imports from config and core packages
2. Sets up the UI
3. Handles user interactions
4. Coordinates between LLM, database, and RAG components

## Usage Examples

### Running an Application

```bash
# Single table - Basic (recommended for single table)
streamlit run src/app/app_single_basic.py

# Single table - with RAG
streamlit run src/app/app_single_rag.py

# Multiple tables - Basic
streamlit run src/app/app_multi_basic.py

# Multiple tables - with RAG (recommended for multiple tables)
streamlit run src/app/app_multi_rag.py
```

### Setting up Database

```bash
# Single table setup
python src/app/utils/database_setup_single_table.py

# Multiple tables setup
python src/app/utils/database_setup_multiple_tables.py
```

## Design Principles

1. **Separation of Concerns**: Config, core logic, and UI are separated
2. **Reusability**: Core components can be imported and reused
3. **Maintainability**: Easy to locate and modify specific functionality
4. **Scalability**: Simple to add new features or LLM providers
5. **No Complexity**: Kept simple and straightforward, no over-engineering

## Key Benefits of This Structure

- **Easy Testing**: Core logic is separated and can be tested independently
- **Clear Organization**: Each component has a specific responsibility
- **Simple Imports**: Clean import paths from config and core packages
- **Professional**: Follows industry-standard Python project structure
- **Flexible**: Easy to add new models, prompts, or database types
