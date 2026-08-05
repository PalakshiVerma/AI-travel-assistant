
from langchain_core.prompts import PromptTemplate
from src.retriever import retrieve_docs
from src.config import MODEL_PROVIDER, OPENAI_API_KEY

# Hugging Face imports
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from langchain_huggingface import HuggingFacePipeline

# OpenAI imports
from langchain_openai import ChatOpenAI


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

if MODEL_PROVIDER == "huggingface":
    model_id = "google/flan-t5-base"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
elif MODEL_PROVIDER == "openai":
    llm = ChatOpenAI(api_key=OPENAI_API_KEY, model_name="gpt-3.5-turbo", temperature=0.7)
    qa_chain = prompt_template | llm
else:
    raise ValueError(f"Unknown MODEL_PROVIDER: {MODEL_PROVIDER}")


def generate_answer(query: str) -> str:
    docs = retrieve_docs(query, top_k=2)
    context = "\n".join(docs)[:800]
    
    if MODEL_PROVIDER == "openai":
        result = qa_chain.invoke({"context": context, "question": query})
        return result.content

    prompt = prompt_template.format(context=context, question=query)
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=256)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return answer
