# Raw output status

`observed_groq_error.txt` preserves the exact error text supplied from a real run of this project. The original question was not included with that error, so it is not attributed to any of the test cases.

No successful model output is included: the reported Groq request was rejected with HTTP 403, and the current execution environment has no usable Python interpreter. The three independent test inputs are in `../test_cases.json`. Once Python dependencies, the local knowledge base, and Groq access are available, run `../run_test_cases.ps1`; it writes the unedited terminal output for each case into a new time-stamped run folder without replacing previous output.
