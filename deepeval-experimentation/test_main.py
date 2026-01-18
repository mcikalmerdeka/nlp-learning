from deepeval import assert_test, evaluate
from deepeval.test_case import LLMTestCase, LLMTestCaseParams, ConversationalTestCase, Turn
from deepeval.metrics import GEval, ConversationalGEval, AnswerRelevancyMetric, FaithfulnessMetric

from dotenv import load_dotenv
load_dotenv()

# # Normal GEval Test
# def test_correctness():

#     # Define the correctness metric using the GEval metric
#     correctness_metric = GEval(
#         name="Correctness",
#         criteria="Determine if the 'actual output' is correct based on the 'expected output'.",
#         evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
#         threshold=0.5,
#         model="gpt-4.1-mini"
#     )

#     # Define the test cases
#     ## Several notes:
#     ## input: The user's question
#     ## actual output: The actual output from the LLM application
#     ## expected output: The expected output from the LLM application
#     ## retrieval context: The retrieval context from the LLM application

#     test_case_1 = LLMTestCase(
#         input="I have a persistent cough and fever. Should I be worried?",

#         # Replace this with the actual output from your LLM application
#         actual_output="A persistent cough and fever could be a viral infection or something more serious. See a doctor if symptoms worsen or don't improve in a few days.",
#         expected_output="A persistent cough and fever could indicate a range of illnesses, from a mild viral infection to more serious conditions like pneumonia or COVID-19. You should seek medical attention if your symptoms worsen, persist for more than a few days, or are accompanied by difficulty breathing, chest pain, or other concerning signs."
#     )

#     test_case_2 = LLMTestCase(
#         input="What if these shoes don't fit?",

#         # Replace this with the actual output from your LLM application
#         actual_output="You have 30 days to get a full refund at no extra cost.",
#         expected_output="We offer a 30-day full refund at no extra costs.",
#         retrieval_context=["All customers are eligible for a 30 day full refund at no extra costs."]
#     )


    # # Run the test cases (can only run one test case at a time)
    # assert_test(test_case_1, [correctness_metric])

    # # Evaluate the test cases (can run multiple test cases at once)
    # evaluate(test_cases=[test_case_1, test_case_2], metrics=[correctness_metric])

# # Conversational GEval Test
# def test_conversational_correctness():

#     # Define the professionalism metric
#     professionalism_metric = ConversationalGEval(
#         name="Professionalism",
#         criteria="Determine whether the assistant answers the user's question in a professional and appropriate manner.",
#         model="gpt-4.1-mini",
#         threshold=0.5
#     )

#     # Define the test cases
#     ## Case 1: The assistant answers the user's question in a professional and appropriate manner.
#     conversational_test_case_1 = ConversationalTestCase(
#         turns=[
#             Turn(role="user", content="Is Python an interpreted programming language?"),
#             Turn(role="assistant", content="Yes, Python is an interpreted programming language. It is designed to be easy to learn and use, and is a popular choice for beginners and experienced developers alike."),
#             Turn(role="user", content="What about C++?"),
#             Turn(role="assistant", content="Yes, C++ is a compiled programming language. It is designed to be efficient and fast, and is a popular choice for performance-critical applications.")
#         ]
#     )

#     ## Case 2: The assistant answers the user's question in an inappropriate manner.
#     conversational_test_case_2 = ConversationalTestCase(
#         turns=[
#             Turn(role="user", content="Is Python an interpreted programming language?"),
#             Turn(role="assistant", content="Are you seriously asking me this question?"),
#             Turn(role="user", content="What about C++?"),
#             Turn(role="assistant", content="Aight bro, my suggestions is that you consider career change")
#         ]
#     )

#     # Evaluate the test cases
#     evaluate(test_cases=[conversational_test_case_1, conversational_test_case_2], metrics=[professionalism_metric])

# # Answer Relevance Test
# def test_answer_relevance():

#     # Define the answer relevance metric
#     answer_relevance_metric = AnswerRelevancyMetric(
#         threshold=0.5,
#         include_reason=True,
#         model="gpt-4.1-mini"
#     )

#     # Define the test cases

#     ## Case 1: The assistant's answer is relevant to the user's question.
#     test_case_1 = LLMTestCase(
#         input="What is the capital of France?",
#         actual_output="The capital of France is Paris.",
#         expected_output="The capital of France is Paris."
#     )

#     ## Case 2: The assistant's answer is not relevant to the user's question.
#     test_case_2 = LLMTestCase(
#         input="What is the capital of Indonesia?",
#         actual_output="The capital of Indonesia is Bali.",
#         expected_output="The capital of Indonesia is Jakarta."
#     )

#     # Evaluate the test cases
#     evaluate(test_cases=[test_case_1, test_case_2], metrics=[answer_relevance_metric])

# Faithfulness Test
def test_faithfulness():

    # Define the faithfulness metric
    faithfulness_metric = FaithfulnessMetric(
        threshold=0.5,
        include_reason=True,
        model="gpt-4.1-mini"
    )

    # Define the test cases
    ## Several notes:
    ## The usage of faithfulness metric is actually whether the llm answer is faithful to the retrieval context or not, and not whether the llm answer is correct or not.
    ## So in here you will see that the first one will actually fail the test, while the second one will pass even though the llm answer is wrong but it is faithful to the retrieval context.

    ## Case 1: The assistant's answer is faithful to the user's question.
    test_case_1 = LLMTestCase(
        input="What is the capital of France?",
        actual_output="Paris",
        retrieval_context=["The capital of France is Madrid."]
    )

    ## Case 2: The assistant's answer is not faithful to the user's question.
    test_case_2 = LLMTestCase(
        input="What is the capital of Indonesia?",
        actual_output="Bali",
        retrieval_context=["The capital of Indonesia is Jakarta."]
    )

    # Evaluate the test cases
    evaluate(test_cases=[test_case_1, test_case_2], metrics=[faithfulness_metric])