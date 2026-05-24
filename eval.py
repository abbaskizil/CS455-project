import retriever
import generator
import sys
import api


def Answer_With_RAG(query):
    query_embedding = retriever.Encode_Query(query)
    top20 = retriever.Query_Collection(query_embedding)
    reranked = retriever.Rerank_Functions(query, top20)
    context_string = generator.Dict_To_Context_String_Converter(reranked)
    user_prompt = generator.Build_User_Prompt(query, context_string)
    response, _ = generator.Chat(user_prompt, [])
    return response

def Answer_Without_RAG(query):
    llm_message = generator.client.messages.create(
        model = "claude-haiku-4-5",
        max_tokens = 1000,
        messages = [{"role": "user", "content": query}]
    )
    return llm_message.content[0].text

def Get_Answers(queries, answer_func):
    answers = []
    for q in queries:
        answers.append(answer_func(q))
    return answers


if __name__ == "__main__":
    repos = {
        "test-codes-for-LLM-project": {
            "url": "https://github.com/omuremreyildiz03/test-codes-for-LLM-project",
            "questions": [
                "How is inheritance implemented between Dog and Animal?",
                "Is there a function that checks if a number is prime?",
                "How is duration converted from milliseconds to hours in this codebase?",
                "How is streaming history loaded from a JSON file?",
                "Is there a function that sorts songs by play count?",
                "How does the shopping cart handle adding duplicate items?",
                "Is there a function that generates a greeting message?",
                "How is string reversal implemented?",
                "How are playlists filtered by artist name?",
                "Is there any visualization logic and where is it?"
            ]
        },
        "CS308": {
            "url": "https://github.com/abbaskizil/CS308",
            "questions": [
                "How is stock quantity enforced when adding a product to cart?",
                "Is there a function that clears the cart?",
                "How is a new cart created if one does not exist yet?",
                "How is JWT authentication handled in this project?",
                "Is there a function that generates invoices?",
                "How are orders processed and is there a dedicated service for it?",
                "How is payment handled and where is it implemented?",
                "Is there any discount logic and where is it applied?",
                "How are product reviews stored and retrieved?",
                "How is user authentication checked before accessing protected routes?"
            ]
        },
        "CS436-Project": {
            "url": "https://github.com/abbaskizil/CS436-Project",
            "questions": [
                "How is email domain validation enforced during registration?",
                "Is there a function that cleans up expired OTP records?",
                "How is a Cognito JWT token validated?",
                "How is the OTP generated and sent to the user?",
                "Is there a function that caches the Cognito public keys?",
                "How is password hashing implemented?",
                "How does the system check if the current user is authenticated?",
                "Is there a function that handles password reset flow?",
                "How is the email binding process implemented?",
                "How are database sessions managed in this project?"
            ]
        }
    }

    repo_name = sys.argv[1]  # python eval.py repo-name
    repo = repos[repo_name]
    
    api.Run_Indexing_Pipeline(repo["url"])
    
    rag_answers = Get_Answers(repo["questions"], Answer_With_RAG)
    no_rag_answers = Get_Answers(repo["questions"], Answer_Without_RAG)
    
    # Used BERTScore to compare answers
    # P, R, F1 = bert_score.score(no_rag_answers, rag_answers, lang="en")
    # print(f"BERTScore F1: {F1.mean():.4f}")
    # Because general answers' semantic are same, scores nearly 0.8

    with open(f"{repo_name}_rag.txt", "w", encoding="utf-8") as f:
        for q, a in zip(repo["questions"], rag_answers):
            f.write(f"Q: {q}\n\nA: {a}\n\n{'='*80}\n\n")

    with open(f"{repo_name}_no_rag.txt", "w", encoding="utf-8") as f:
        for q, a in zip(repo["questions"], no_rag_answers):
            f.write(f"Q: {q}\n\nA: {a}\n\n{'='*80}\n\n")