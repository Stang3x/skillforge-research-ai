"""
Skill Performance Testing

Test suite to measure performance improvement from integrated skills.
Runs sample research queries and benchmarks responses.
"""

import subprocess
import sys
import time
from pathlib import Path


class SkillTester:
    """Test skill integration and measure performance improvements."""
    
    def __init__(self, python_exe: str):
        self.python_exe = python_exe
        self.results = []
    
    def run_query(self, query: str, timeout: int = 15) -> tuple[str, float, int]:
        """
        Run a query through the research assistant.
        
        Returns:
            (response, execution_time, exit_code)
        """
        start_time = time.time()
        
        try:
            result = subprocess.run(
                [self.python_exe, "research_assistant.py"],
                input=f"{query}\nexit\n",
                text=True,
                timeout=timeout,
                capture_output=True,
                cwd=str(Path.cwd())
            )
            
            exec_time = time.time() - start_time
            return result.stdout, exec_time, result.returncode
        
        except subprocess.TimeoutExpired:
            return "TIMEOUT", timeout, 1
        except Exception as e:
            return f"ERROR: {e}", 0, 1
    
    def test_skill(self, skill_name: str, test_queries: list[dict]) -> dict:
        """
        Test a specific skill with queries.
        
        Args:
            skill_name: Name of skill to test
            test_queries: List of dicts with 'query' and 'expected_keywords'
        
        Returns:
            Results dictionary
        """
        print(f"\n{'='*70}")
        print(f"Testing: {skill_name.upper()}")
        print(f"{'='*70}\n")
        
        skill_results = {
            "skill": skill_name,
            "queries": [],
            "avg_time": 0,
            "success_rate": 0
        }
        
        times = []
        successes = 0
        
        for i, test in enumerate(test_queries, 1):
            query = test["query"]
            expected_keywords = test.get("expected_keywords", [])
            
            print(f"Test {i}: {query}")
            response, exec_time, exit_code = self.run_query(query)
            
            # Check if response contains expected keywords
            success = exit_code == 0 and all(kw.lower() in response.lower() for kw in expected_keywords)
            
            times.append(exec_time)
            if success:
                successes += 1
            
            # Show first 100 chars of response
            response_preview = response[:100].replace("\n", " ") if response else "NO RESPONSE"
            status = "[PASS]" if success else "[CHECK]"
            print(f"  {status} Time: {exec_time:.2f}s")
            print(f"  Response: {response_preview}...\n")
            
            skill_results["queries"].append({
                "query": query,
                "time": exec_time,
                "success": success
            })
        
        skill_results["avg_time"] = sum(times) / len(times) if times else 0
        skill_results["success_rate"] = (successes / len(test_queries) * 100) if test_queries else 0
        
        return skill_results


def main():
    """Run comprehensive skill tests."""
    
    # Determine Python executable
    py_exe = sys.executable
    
    print("\n" + "="*70)
    print("RESEARCH ASSISTANT SKILL INTEGRATION TEST SUITE")
    print("="*70)
    print(f"Python: {py_exe}")
    print(f"Working Directory: {Path.cwd()}\n")
    
    tester = SkillTester(py_exe)
    
    # Test queries for each skill
    test_suites = {
        "research-methodology": [
            {
                "query": "How should I plan a literature review on AI ethics?",
                "expected_keywords": ["research", "plan", "scope", "inclusion"]
            },
            {
                "query": "What methodology should I use for studying machine learning bias?",
                "expected_keywords": ["methodology", "approach", "method", "study"]
            },
            {
                "query": "How do I identify bias in my research?",
                "expected_keywords": ["bias", "identify", "detect", "mitigation"]
            }
        ],
        "citation-standards": [
            {
                "query": "How do I format a journal article in APA style?",
                "expected_keywords": ["APA", "citation", "format", "article"]
            },
            {
                "query": "What's the difference between APA and MLA citations?",
                "expected_keywords": ["APA", "MLA", "citation", "format", "difference"]
            },
            {
                "query": "Help me create a bibliography for my research paper",
                "expected_keywords": ["bibliography", "citation", "reference", "sources"]
            }
        ],
        "source-evaluation": [
            {
                "query": "How do I know if a Wikipedia article is reliable for research?",
                "expected_keywords": ["Wikipedia", "reliable", "source", "quality", "credibility"]
            },
            {
                "query": "What makes a source credible for academic research?",
                "expected_keywords": ["credible", "source", "academic", "authority", "reliability"]
            },
            {
                "query": "How can I detect bias in online articles?",
                "expected_keywords": ["bias", "detect", "article", "credibility", "evaluation"]
            }
        ]
    }
    
    # Run all tests
    all_results = []
    for skill_name, queries in test_suites.items():
        result = tester.test_skill(skill_name, queries)
        all_results.append(result)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70 + "\n")
    
    total_tests = 0
    total_time = 0
    total_success = 0
    
    for result in all_results:
        skill = result["skill"].upper()
        avg_time = result["avg_time"]
        success_rate = result["success_rate"]
        query_count = len(result["queries"])
        
        print(f"{skill}")
        print(f"  Tests: {query_count}")
        print(f"  Avg Time: {avg_time:.2f}s")
        print(f"  Success Rate: {success_rate:.1f}%")
        print()
        
        total_tests += query_count
        total_time += sum(q["time"] for q in result["queries"])
        total_success += sum(1 for q in result["queries"] if q["success"])
    
    print("="*70)
    print("OVERALL METRICS")
    print("="*70)
    print(f"Total Tests Run: {total_tests}")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Average Time per Query: {total_time/total_tests:.2f}s")
    print(f"Overall Success Rate: {total_success/total_tests*100:.1f}%")
    print(f"\nTest Status: {'PASSED' if total_success/total_tests >= 0.8 else 'NEEDS REVIEW'}")
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("1. Try interactive mode: python research_assistant.py")
    print("2. Test skill queries manually")
    print("3. Type 'help' to see skill list")
    print("4. Type 'skills' for detailed documentation")
    print("5. Ask research methodology, citation, or source evaluation questions")
    print("\nExpected Improvements:")
    print("- Better research planning guidance (Research Methodology skill)")
    print("- More accurate citation formatting (Citation Standards skill)")
    print("- Smarter source credibility assessment (Source Evaluation skill)")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()