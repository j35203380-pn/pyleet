def build_script(user_code: str, method_name: str, test_cases: list[dict]) -> str:
    return f"""
from typing import List, Optional, Dict, Tuple
import json

{user_code}

class CodeRunner:
    def run(self, func, test_cases):
        results = []
        for case in test_cases:
            try:
                actual = func(*case["input"])
                results.append({{"passed": actual == case["expected"], "actual": actual}})
            except Exception as e:
                results.append({{"passed": False, "error": repr(e)}})
        return results

__sandbox__solution___ = Solution()
__sandbox__runner___ = CodeRunner()
__sandbox__results___ = __sandbox__runner___.run(__sandbox__solution___.{method_name}, {test_cases!r})

print("###RESULT###")
print(json.dumps(__sandbox__results___))
"""