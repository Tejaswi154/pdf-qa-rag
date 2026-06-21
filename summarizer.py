from llm import chat


def get_full_text(documents):
    full_text = "\n".join(
        [doc.page_content for doc in documents]
    )
    return full_text


def summarize_document(full_text):
    response = chat(
        model="llama3.1:8b",
        messages=[
            {
                "role": "user",
                "content": f"Summarize this document:\n\n{full_text[:10000]}"
            }
        ]
    )

    summary = response["message"]["content"]
    return summary
