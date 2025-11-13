"""
Automated Testing for Chatbot Requirements
Tests if bot meets all recruiter-focused requirements
"""
import asyncio
import json
from typing import Dict, List
import requests
import time
from datetime import datetime

API_URL = "http://localhost:8000/api/v1"


class ChatbotTester:
    """Automated testing for chatbot requirements"""
    
    def __init__(self):
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "categories": {}
        }
        self.session_id = "test-session"
    
    def send_query(self, query: str) -> Dict:
        """Send query to chatbot and get response"""
        try:
            response = requests.post(
                f"{API_URL}/chat",
                json={
                    "message": query,
                    "conversation_history": [],
                    "session_id": self.session_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "response": data.get("response", ""),
                    "processing_time": data.get("processing_time", 0),
                    "sources": data.get("sources", [])
                }
            else:
                return {
                    "success": False,
                    "error": f"Status {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_keywords(self, response: str, keywords: List[str], min_matches: int = 1) -> bool:
        """Check if response contains required keywords"""
        response_lower = response.lower()
        matches = sum(1 for keyword in keywords if keyword.lower() in response_lower)
        return matches >= min_matches
    
    def test_category(self, category: str, test_cases: List[Dict]):
        """Run tests for a category"""
        print(f"\n{'='*60}")
        print(f"Testing Category: {category}")
        print(f"{'='*60}")
        
        category_results = {
            "total": len(test_cases),
            "passed": 0,
            "failed": 0,
            "tests": []
        }
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] Testing: {test['query'][:60]}...")
            
            result = self.send_query(test['query'])
            
            if not result['success']:
                print(f"❌ FAILED: {result['error']}")
                category_results["failed"] += 1
                category_results["tests"].append({
                    "query": test['query'],
                    "status": "FAILED",
                    "reason": result['error']
                })
                continue
            
            response = result['response']
            
            # Check if response contains required keywords
            has_keywords = self.check_keywords(
                response,
                test['expected_keywords'],
                test.get('min_matches', 1)
            )
            
            # Check response length (should be substantial)
            is_substantial = len(response) > test.get('min_length', 50)
            
            # Check processing time
            is_fast = result['processing_time'] < test.get('max_time', 10.0)
            
            # Overall pass/fail
            passed = has_keywords and is_substantial and is_fast
            
            if passed:
                print(f"✅ PASSED")
                print(f"   Response length: {len(response)} chars")
                print(f"   Processing time: {result['processing_time']:.2f}s")
                print(f"   Keywords found: {has_keywords}")
                category_results["passed"] += 1
            else:
                print(f"❌ FAILED")
                if not has_keywords:
                    print(f"   Missing keywords: {test['expected_keywords']}")
                if not is_substantial:
                    print(f"   Response too short: {len(response)} chars")
                if not is_fast:
                    print(f"   Too slow: {result['processing_time']:.2f}s")
                category_results["failed"] += 1
            
            category_results["tests"].append({
                "query": test['query'],
                "status": "PASSED" if passed else "FAILED",
                "response_length": len(response),
                "processing_time": result['processing_time'],
                "keywords_found": has_keywords,
                "response_preview": response[:200] + "..."
            })
            
            # Small delay between requests
            time.sleep(0.5)
        
        self.test_results["categories"][category] = category_results
        self.test_results["total_tests"] += category_results["total"]
        self.test_results["passed"] += category_results["passed"]
        self.test_results["failed"] += category_results["failed"]
        
        print(f"\n{category} Results: {category_results['passed']}/{category_results['total']} passed")
    
    def run_all_tests(self):
        """Run all requirement tests"""
        print("\n" + "="*60)
        print("STARTING CHATBOT REQUIREMENTS TESTING")
        print("="*60)
        
        # 1. PERSONAL INFORMATION TESTS
        personal_tests = [
            {
                "query": "What is Usama's full name?",
                "expected_keywords": ["Usama", "Masood"],
                "min_length": 20
            },
            {
                "query": "How old is Usama?",
                "expected_keywords": ["age", "year", "born"],
                "min_length": 30
            },
            {
                "query": "What is Usama's email address?",
                "expected_keywords": ["email", "@", "contact"],
                "min_length": 20
            },
            {
                "query": "Where is Usama located?",
                "expected_keywords": ["UK", "United Kingdom", "location"],
                "min_length": 30
            },
            {
                "query": "What is Usama's phone number?",
                "expected_keywords": ["phone", "contact", "number"],
                "min_length": 20
            }
        ]
        self.test_category("Personal Information", personal_tests)
        
        # 2. EDUCATION TESTS
        education_tests = [
            {
                "query": "What is Usama's educational background?",
                "expected_keywords": ["MSc", "Data Science", "Teesside", "University"],
                "min_matches": 2,
                "min_length": 100
            },
            {
                "query": "What degree does Usama have?",
                "expected_keywords": ["Master", "MSc", "Data Science"],
                "min_matches": 1,
                "min_length": 50
            },
            {
                "query": "Where did Usama study?",
                "expected_keywords": ["Teesside", "University", "UK"],
                "min_matches": 1,
                "min_length": 50
            },
            {
                "query": "What was Usama's GPA or grade?",
                "expected_keywords": ["distinction", "grade", "merit", "GPA"],
                "min_matches": 1,
                "min_length": 30
            }
        ]
        self.test_category("Education", education_tests)
        
        # 3. SKILLS TESTS
        skills_tests = [
            {
                "query": "What programming languages does Usama know?",
                "expected_keywords": ["Python", "programming", "language"],
                "min_matches": 2,
                "min_length": 100
            },
            {
                "query": "What are Usama's machine learning skills?",
                "expected_keywords": ["machine learning", "ML", "TensorFlow", "PyTorch", "scikit"],
                "min_matches": 2,
                "min_length": 150
            },
            {
                "query": "Does Usama know deep learning?",
                "expected_keywords": ["deep learning", "neural", "CNN", "RNN", "transformer"],
                "min_matches": 2,
                "min_length": 100
            },
            {
                "query": "What NLP skills does Usama have?",
                "expected_keywords": ["NLP", "natural language", "BERT", "GPT", "LLM"],
                "min_matches": 2,
                "min_length": 100
            },
            {
                "query": "Does Usama know LangChain?",
                "expected_keywords": ["LangChain", "RAG", "framework"],
                "min_matches": 1,
                "min_length": 50
            },
            {
                "query": "What cloud platforms does Usama use?",
                "expected_keywords": ["AWS", "cloud", "Azure", "GCP"],
                "min_matches": 1,
                "min_length": 50
            }
        ]
        self.test_category("Technical Skills", skills_tests)
        
        # 4. PROJECTS TESTS
        projects_tests = [
            {
                "query": "Tell me about Usama's projects",
                "expected_keywords": ["project", "RAG", "chatbot", "AI", "machine learning"],
                "min_matches": 2,
                "min_length": 200
            },
            {
                "query": "What is the RAG chatbot project?",
                "expected_keywords": ["RAG", "chatbot", "LangChain", "retrieval"],
                "min_matches": 2,
                "min_length": 150
            },
            {
                "query": "What projects showcase Usama's AI skills?",
                "expected_keywords": ["AI", "machine learning", "project", "NLP"],
                "min_matches": 2,
                "min_length": 150
            },
            {
                "query": "Has Usama built any production systems?",
                "expected_keywords": ["production", "system", "deployed", "enterprise"],
                "min_matches": 1,
                "min_length": 100
            }
        ]
        self.test_category("Projects", projects_tests)
        
        # 5. EXPERIENCE TESTS
        experience_tests = [
            {
                "query": "What is Usama's work experience?",
                "expected_keywords": ["experience", "work", "data scientist", "ML"],
                "min_matches": 1,
                "min_length": 100
            },
            {
                "query": "Has Usama worked as a Data Scientist?",
                "expected_keywords": ["data scientist", "experience", "work"],
                "min_matches": 1,
                "min_length": 50
            },
            {
                "query": "What kind of ML projects has Usama worked on?",
                "expected_keywords": ["ML", "machine learning", "project"],
                "min_matches": 2,
                "min_length": 100
            }
        ]
        self.test_category("Work Experience", experience_tests)
        
        # 6. AVAILABILITY & HIRING TESTS
        availability_tests = [
            {
                "query": "Is Usama available for hire?",
                "expected_keywords": ["available", "hire", "opportunity", "open"],
                "min_matches": 1,
                "min_length": 50
            },
            {
                "query": "When can Usama start?",
                "expected_keywords": ["start", "notice", "available", "immediately"],
                "min_matches": 1,
                "min_length": 50
            },
            {
                "query": "What is Usama's notice period?",
                "expected_keywords": ["notice", "week", "period"],
                "min_matches": 1,
                "min_length": 30
            },
            {
                "query": "Can we schedule an interview?",
                "expected_keywords": ["schedule", "meeting", "interview", "calendly", "available"],
                "min_matches": 1,
                "min_length": 50
            }
        ]
        self.test_category("Availability & Hiring", availability_tests)
        
        # 7. RECRUITER-SPECIFIC TESTS
        recruiter_tests = [
            {
                "query": "Does Usama fit a Senior Data Scientist role requiring Python, ML, and NLP?",
                "expected_keywords": ["fit", "Python", "ML", "NLP", "skills"],
                "min_matches": 2,
                "min_length": 100
            },
            {
                "query": "What makes Usama a good AI Engineer candidate?",
                "expected_keywords": ["AI", "engineer", "skills", "experience", "projects"],
                "min_matches": 2,
                "min_length": 150
            },
            {
                "query": "Show me Usama's portfolio",
                "expected_keywords": ["portfolio", "project", "GitHub", "work"],
                "min_matches": 1,
                "min_length": 100
            }
        ]
        self.test_category("Recruiter Queries", recruiter_tests)
        
        # 8. TECHNICAL DEPTH TESTS
        technical_tests = [
            {
                "query": "Explain Usama's RAG implementation",
                "expected_keywords": ["RAG", "retrieval", "embedding", "vector", "LangChain"],
                "min_matches": 2,
                "min_length": 150
            },
            {
                "query": "What LLM models has Usama worked with?",
                "expected_keywords": ["LLM", "GPT", "OpenAI", "model"],
                "min_matches": 2,
                "min_length": 100
            },
            {
                "query": "Show me code example from Usama's projects",
                "expected_keywords": ["code", "example", "Python", "implementation"],
                "min_matches": 1,
                "min_length": 50
            }
        ]
        self.test_category("Technical Depth", technical_tests)
        
        # GENERATE FINAL REPORT
        self.generate_report()
    
    def generate_report(self):
        """Generate final test report"""
        print("\n" + "="*60)
        print("FINAL TEST REPORT")
        print("="*60)
        
        total = self.test_results["total_tests"]
        passed = self.test_results["passed"]
        failed = self.test_results["failed"]
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\nOverall Results:")
        print(f"  Total Tests: {total}")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")
        print(f"  Pass Rate: {pass_rate:.1f}%")
        
        print(f"\nCategory Breakdown:")
        for category, results in self.test_results["categories"].items():
            cat_pass_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
            status = "✅" if cat_pass_rate >= 80 else "⚠️" if cat_pass_rate >= 60 else "❌"
            print(f"  {status} {category}: {results['passed']}/{results['total']} ({cat_pass_rate:.1f}%)")
        
        print(f"\n{'='*60}")
        
        # Save to file
        with open('test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\nDetailed results saved to: test_results.json")
        
        # Final verdict
        print(f"\n{'='*60}")
        if pass_rate >= 90:
            print("🎉 EXCELLENT! Chatbot meets requirements!")
        elif pass_rate >= 75:
            print("✅ GOOD! Minor improvements needed.")
        elif pass_rate >= 60:
            print("⚠️ ACCEPTABLE. Several improvements needed.")
        else:
            print("❌ NEEDS WORK. Major improvements required.")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    print("Starting automated chatbot testing...")
    print("Make sure the backend is running on http://localhost:8000")
    
    input("\nPress Enter to start testing...")
    
    tester = ChatbotTester()
    tester.run_all_tests()
