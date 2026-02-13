"""
Test RAG retrieval quality across diverse queries.

Usage:
    python test_rag.py

Requires VOYAGE_API_KEY to be set.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()


def test_chunker():
    """Test that the Manim chunker extracts meaningful chunks."""
    from app.rag.chunker import ManimChunker

    chunker = ManimChunker()
    chunks = chunker.extract_chunks()

    print(f"[chunker] Extracted {len(chunks)} chunks")
    assert len(chunks) > 100, f"Expected >100 chunks, got {len(chunks)}"

    # Check we got both module and class chunks
    types = {c["type"] for c in chunks}
    assert "class" in types, "No class chunks found"
    assert "module" in types, "No module chunks found"

    # Check some key Manim classes are present
    class_names = {c["name"] for c in chunks if c["type"] == "class"}
    expected = {"Scene", "Axes", "Circle", "Square", "Arrow", "Dot", "VGroup"}
    found = expected & class_names
    print(f"[chunker] Found key classes: {found}")
    assert len(found) >= 4, f"Missing key classes. Found: {found}"

    print("[chunker] PASSED")


def test_retrieval():
    """Test end-to-end retrieval quality."""
    if not os.getenv("VOYAGE_API_KEY"):
        print("[retrieval] SKIPPED — VOYAGE_API_KEY not set")
        return

    from app.rag.retriever import RAGRetriever

    retriever = RAGRetriever()
    counts = retriever.initialize()
    print(f"[retrieval] Index: {counts}")

    # Test queries and expected matches
    test_cases = [
        {
            "query": "3D rotating cube",
            "expect_api": ["ThreeDScene"],
            "expect_example_tags": ["3d"],
        },
        {
            "query": "plot sine function on axes",
            "expect_api": ["Axes"],
            "expect_example_tags": ["axes", "plot"],
        },
        {
            "query": "animate a circle transforming into a square",
            "expect_api": ["Circle", "Square", "Transform"],
            "expect_example_tags": ["transform"],
        },
        {
            "query": "value tracker with moving dot",
            "expect_api": ["ValueTracker"],
            "expect_example_tags": ["valuetracker", "tracker"],
        },
        {
            "query": "graph network with vertices and edges",
            "expect_api": ["Graph"],
            "expect_example_tags": ["graph"],
        },
        {
            "query": "camera zoom animation",
            "expect_api": ["MovingCameraScene"],
            "expect_example_tags": ["camera"],
        },
    ]

    passed = 0
    for tc in test_cases:
        query = tc["query"]
        results = retriever.search(query)

        api_names = [r["name"] for r in results["api_refs"]]
        example_tags = []
        for ex in results["examples"]:
            example_tags.extend(t.lower() for t in ex.get("tags", []))

        # Check API refs
        api_hit = any(
            expected.lower() in name.lower()
            for expected in tc["expect_api"]
            for name in api_names
        )

        # Check example tags
        tag_hit = any(
            expected in tag
            for expected in tc["expect_example_tags"]
            for tag in example_tags
        )

        status = "PASS" if (api_hit or tag_hit) else "FAIL"
        if status == "PASS":
            passed += 1
        print(f"  [{status}] '{query}'")
        print(f"    API refs: {api_names[:5]}")
        print(f"    Example tags: {list(set(example_tags))[:8]}")

    print(f"\n[retrieval] {passed}/{len(test_cases)} queries passed")
    assert passed >= len(test_cases) // 2, f"Too many failures: {passed}/{len(test_cases)}"
    print("[retrieval] PASSED")


if __name__ == "__main__":
    print("=" * 50)
    print("RAG Integration Tests")
    print("=" * 50)

    test_chunker()
    print()
    test_retrieval()

    print("\n" + "=" * 50)
    print("All tests passed!")
