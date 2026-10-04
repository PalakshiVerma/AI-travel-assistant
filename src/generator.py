"""
Answer generation module integrating Large Language Models (LLMs).
Combines retrieved travel guide context with user queries using LangChain prompt templates.
Supports model generation from either Hugging Face (google/flan-t5-base) or OpenAI (gpt-3.5-turbo).
"""
from langchain_core.prompts import PromptTemplate
from src.retriever import retrieve_docs
import os
from src.config import MODEL_PROVIDER, OPENAI_API_KEY, GROQ_API_KEY, GEMINI_API_KEY

prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are a helpful travel assistant.
Use the following travel guide context to answer the question.
If the answer is not found, say you don't know — don’t make it up.

Context:
{context}

Question:
{question}

Answer:"""
)

if MODEL_PROVIDER == "gemini":
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.7
    )
    qa_chain = prompt_template | llm
elif MODEL_PROVIDER == "huggingface":
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    model_id = "google/flan-t5-large"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
elif MODEL_PROVIDER == "openai":
    from langchain_openai import ChatOpenAI
    api_key = GROQ_API_KEY or OPENAI_API_KEY
    base_url = "https://api.groq.com/openai/v1" if GROQ_API_KEY else None
    model_name = "llama-3.3-70b-versatile" if GROQ_API_KEY else "gpt-3.5-turbo"
    
    llm = ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model_name=model_name,
        temperature=0.7
    )
    qa_chain = prompt_template | llm
else:
    raise ValueError(f"Unknown MODEL_PROVIDER: {MODEL_PROVIDER}")


def generate_answer(query: str) -> str:
    docs = retrieve_docs(query, top_k=2)
    context = "\n".join(docs)[:800] if docs else ""
    
    if MODEL_PROVIDER in ["openai", "gemini"]:
        result = qa_chain.invoke({"context": context if context else "No extra document context provided.", "question": query})
        return result.content

    if context.strip():
        prompt = (
        f"Context from travel guide:\n{context}\n\n"
        f"Question: {query}\n\n"
        f"Based on the context, provide a clear, helpful answer:\n"
    )
    else:
        prompt = f"Question: {query}\n\nAnswer:"


    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(
        **inputs,
        max_new_tokens=256,
        no_repeat_ngram_size=3, 
        do_sample=True,
        temperature=0.3,
        top_p=0.9,
        repetition_penalty=1.5
    )
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return answer

