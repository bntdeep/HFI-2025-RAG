## 8. Evaluation

8.1 Evaluation Dataset

Create eval/eval_dataset.json with 25+ question-answer pairs manually verified against the PDF document:

json


{
  "eval_questions": [
    {
      "id": "eval_001",
      "question": "Which country ranks #1 in the 2025 Human Freedom Index?",
      "expected_answer": "Switzerland",
      "answer_type": "exact_match",
      "category": "factual"
    },
    {
      "id": "eval_002", 
      "question": "What is Japan's personal freedom score?",
      "expected_answer": "8.59",
      "answer_type": "numeric",
      "tolerance": 0.05,
      "category": "factual"
    },
    {
      "id": "eval_003",
      "question": "Compare the economic freedom of Estonia and Poland",
      "expected_data": {
        "Estonia": { "economic_freedom": 8.15 },
        "Poland": { "economic_freedom": 7.02 }
      },
      "answer_type": "comparison",
      "category": "extraction"
    },
    {
      "id": "eval_004",
      "question": "Which region has the lowest average personal freedom?",
      "expected_answer": "Middle East & North Africa",
      "answer_type": "exact_match",
      "category": "analytical"
    }
    // ... 21+ more questions
  ]
}
8.2 Metrics

Metric 1: Answer Accuracy (Primary)
python


# For exact_match questions:
accuracy = correct_answers / total_questions

# For numeric questions:
numeric_accuracy = answers_within_tolerance / total_numeric_questions

# Target: >= 80%
Metric 2: Retrieval Relevance
python


# For each question, check if the retrieved chunks 
# contain the information needed to answer

retrieval_hit_rate = questions_with_relevant_chunks / total_questions

# A "hit" = at least one chunk in top_k contains the answer
# Target: >= 85%
Metric 3: Chart Data Correctness
python


# For comparison/extraction questions:
# Check if chart_data values match expected values

chart_accuracy = correct_data_points / total_data_points

# Target: >= 75%
8.3 Evaluation Script



python eval/run_evaluation.py

Output:
┌─────────────────────────────────────────────┐
│  EVALUATION RESULTS                         │
├─────────────────────────────────────────────┤
│  Questions evaluated: 25                    │
│                                             │
│  Answer Accuracy:     84% (21/25)           │
│  Retrieval Hit Rate:  88% (22/25)           │
│  Chart Data Accuracy: 78% (18/23)           │
│                                             │
│  By Category:                               │
│    Factual:    90% (9/10)                   │
│    Extraction: 80% (8/10)                   │
│    Analytical: 80% (4/5)                    │
│                                             │
│  Failed Questions:                          │
│    eval_007: Expected "Norway", got "Sweden" │
│    eval_015: Score off by 0.3               │
│    eval_019: Chart missing 2 countries       │
│    eval_022: Retriever missed relevant chunk │
└─────────────────────────────────────────────┘
