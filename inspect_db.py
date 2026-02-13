"""
Utility script to inspect and manage the ChromaDB RAG database.

Usage:
    python inspect_db.py                    # Show database status
    python inspect_db.py --init             # Initialize/build the database
    python inspect_db.py --rebuild          # Rebuild from scratch
    python inspect_db.py --search "query"   # Search for examples/APIs
    python inspect_db.py --list-examples    # List all indexed examples
    python inspect_db.py --list-api         # List all API chunks
"""
import sys
import argparse
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.rag import CHROMA_DB_PATH, COLLECTION_MANIM_API, COLLECTION_MANIM_EXAMPLES


def check_db_exists():
    """Check if the database exists and has data."""
    db_path = Path(CHROMA_DB_PATH)
    if not db_path.exists():
        return False, "Database directory does not exist"
    
    try:
        import chromadb
        from app.rag.embeddings import VoyageEmbeddingFunction
        
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        
        try:
            api_col = client.get_collection(COLLECTION_MANIM_API)
            ex_col = client.get_collection(COLLECTION_MANIM_EXAMPLES)
            
            api_count = api_col.count()
            ex_count = ex_col.count()
            
            return True, f"API chunks: {api_count}, Examples: {ex_count}"
        except Exception as e:
            return False, f"Collections not found or empty: {e}"
    except Exception as e:
        return False, f"Error checking database: {e}"


def initialize_db(rebuild=False):
    """Initialize or rebuild the database."""
    print(f"{'Rebuilding' if rebuild else 'Initializing'} database...")
    print("This may take a few minutes...\n")
    
    try:
        from app.rag.retriever import RAGRetriever
        
        retriever = RAGRetriever()
        counts = retriever.initialize(rebuild=rebuild)
        
        print("✓ Database initialized successfully!")
        print(f"  - API chunks indexed: {counts['api_chunks']}")
        print(f"  - Examples indexed: {counts['examples']}")
        print(f"  - Location: {CHROMA_DB_PATH}")
        return True
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        return False


def search_db(query):
    """Search the database."""
    try:
        from app.rag.retriever import RAGRetriever
        
        retriever = RAGRetriever()
        retriever.initialize()
        
        print(f"\nSearching for: '{query}'\n")
        results = retriever.search(query, top_k_api=5, top_k_examples=3)
        
        # Show examples
        print("=" * 60)
        print(f"EXAMPLES ({len(results['examples'])} results)")
        print("=" * 60)
        for i, ex in enumerate(results['examples'], 1):
            print(f"\n{i}. {ex['name']} (score: {ex['score']:.3f})")
            print(f"   ID: {ex['id']}")
            print(f"   Tags: {', '.join(ex['tags'])}")
            if ex.get('description'):
                print(f"   Description: {ex['description']}")
            print(f"   Code preview: {ex['code'][:100]}...")
        
        # Show API refs
        print("\n" + "=" * 60)
        print(f"API REFERENCES ({len(results['api_refs'])} results)")
        print("=" * 60)
        for i, ref in enumerate(results['api_refs'], 1):
            print(f"\n{i}. {ref['name']} (score: {ref['score']:.3f})")
            print(f"   Type: {ref['type']}")
            print(f"   Module: {ref['module']}")
            print(f"   Preview: {ref['content'][:150]}...")
        
    except Exception as e:
        print(f"✗ Error searching: {e}")
        return False


def list_examples():
    """List all indexed examples."""
    try:
        import chromadb
        from app.rag.embeddings import VoyageEmbeddingFunction
        
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        embedding_fn = VoyageEmbeddingFunction()
        collection = client.get_collection(
            name=COLLECTION_MANIM_EXAMPLES,
            embedding_function=embedding_fn
        )
        
        # Get all items (ChromaDB requires a query, so we get by limit)
        results = collection.get(limit=100)
        
        print(f"\n{'=' * 60}")
        print(f"ALL EXAMPLES ({len(results['ids'])} total)")
        print('=' * 60)
        
        for i, (doc_id, metadata) in enumerate(zip(results['ids'], results['metadatas']), 1):
            import json
            tags = json.loads(metadata.get('tags', '[]'))
            print(f"\n{i}. {metadata.get('name', doc_id)}")
            print(f"   ID: {doc_id}")
            print(f"   Tags: {', '.join(tags)}")
            print(f"   Difficulty: {metadata.get('difficulty', 'N/A')}")
            if metadata.get('description'):
                print(f"   Description: {metadata['description']}")
        
    except Exception as e:
        print(f"✗ Error listing examples: {e}")


def list_api_chunks():
    """List sample API chunks."""
    try:
        import chromadb
        from app.rag.embeddings import VoyageEmbeddingFunction
        
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        embedding_fn = VoyageEmbeddingFunction()
        collection = client.get_collection(
            name=COLLECTION_MANIM_API,
            embedding_function=embedding_fn
        )
        
        # Get first 20 items
        results = collection.get(limit=20)
        
        print(f"\n{'=' * 60}")
        print(f"API CHUNKS (showing first 20 of {collection.count()} total)")
        print('=' * 60)
        
        for i, (doc_id, metadata, doc) in enumerate(
            zip(results['ids'], results['metadatas'], results['documents']), 1
        ):
            print(f"\n{i}. {metadata.get('name', doc_id)}")
            print(f"   Type: {metadata.get('type', 'N/A')}")
            print(f"   Module: {metadata.get('module', 'N/A')}")
            print(f"   Preview: {doc[:100]}...")
        
        print(f"\n\nTotal API chunks: {collection.count()}")
        
    except Exception as e:
        print(f"✗ Error listing API chunks: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Inspect and manage the ChromaDB RAG database"
    )
    parser.add_argument('--init', action='store_true', 
                       help='Initialize the database (if not exists)')
    parser.add_argument('--rebuild', action='store_true',
                       help='Rebuild the database from scratch')
    parser.add_argument('--search', type=str, metavar='QUERY',
                       help='Search the database')
    parser.add_argument('--list-examples', action='store_true',
                       help='List all indexed examples')
    parser.add_argument('--list-api', action='store_true',
                       help='List sample API chunks')
    
    args = parser.parse_args()
    
    # If no arguments, show status
    if not any([args.init, args.rebuild, args.search, 
                args.list_examples, args.list_api]):
        print("=" * 60)
        print("ChromaDB RAG Database Status")
        print("=" * 60)
        exists, msg = check_db_exists()
        print(f"\nStatus: {'✓ Ready' if exists else '✗ Not initialized'}")
        print(f"Details: {msg}")
        print(f"Location: {CHROMA_DB_PATH}")
        
        if not exists:
            print("\nTo initialize the database, run:")
            print("  python inspect_db.py --init")
        else:
            print("\nAvailable commands:")
            print("  --search 'query'    # Search for content")
            print("  --list-examples     # List all examples")
            print("  --list-api          # List API chunks")
            print("  --rebuild           # Rebuild from scratch")
        return
    
    # Handle commands
    if args.rebuild:
        initialize_db(rebuild=True)
    elif args.init:
        exists, _ = check_db_exists()
        if exists:
            print("Database already exists. Use --rebuild to recreate it.")
        else:
            initialize_db(rebuild=False)
    elif args.search:
        search_db(args.search)
    elif args.list_examples:
        list_examples()
    elif args.list_api:
        list_api_chunks()


if __name__ == "__main__":
    main()
