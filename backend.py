from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.llms import Ollama
import chromadb
from typing import List, Dict, Any
import os


class ZhenHuanQA:
    def __init__(self):
        # 初始化嵌入模型（使用本地模型）
        self.embedding = self._init_embedding()

        # 连接Chroma向量数据库
        self.vectordb = self._init_vectordb()

        # 初始化Ollama
        self.llm = Ollama(
            model="deepseek-r1:1.5b",
            temperature=0.3,
            top_k=20,
            repeat_penalty=1.1
        )

        # 自定义提示模板
        self.prompt_template = """你是一位精通《甄嬛传》的学者，请根据以下上下文回答问题。保持古代宫廷语气，并引用具体场景信息。

        上下文：
        {context}

        问题：{question}
        请按照以下要求回答：
        1. 回答需要根据人物对话和场景
        2. 分析人物关系要结合事件
        3. 回答结合逻辑分析
        回答："""

        self.QA_PROMPT = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context", "question"]
        )

    def _init_embedding(self):
        """初始化本地嵌入模型"""
        return HuggingFaceEmbeddings(
            model_name="./local_models/bge-small-zh-v1.5",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )

    def _init_vectordb(self):
        """初始化Chroma向量数据库"""
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_collection("zhenhuan_zhuan")

        return Chroma(
            client=client,
            collection_name="zhenhuan_zhuan",
            embedding_function=self.embedding
        )

    def ask(self, question: str, k: int = 3) -> Dict[str, Any]:
        """执行问答检索"""
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectordb.as_retriever(
                search_type="mmr",  # 使用最大边际相关性算法
                search_kwargs={"k": k}
            ),
            chain_type_kwargs={"prompt": self.QA_PROMPT},
            return_source_documents=True
        )

        result = qa_chain({"query": question})

        # 格式化结果
        return {
            "answer": result["result"],
            "sources": self._format_sources(result["source_documents"])
        }

    def _format_sources(self, docs: List) -> List[Dict]:
        """格式化来源文档信息"""
        return [{
            "episode": doc.metadata.get("episode", "未知"),
            "scene": doc.metadata.get("title", "未知场景"),
            "content": doc.page_content[:200] + "..."
        } for doc in docs]


# 使用示例
if __name__ == "__main__":
    qa_system = ZhenHuanQA()

    while True:
        question = input("\n请输入问题(输入q退出): ")
        if question.lower() == 'q':
            break

        response = qa_system.ask(question)
        print(f"\n回答：{response['answer']}")
        print("\n来源：")
        for src in response["sources"]:
            print(f"- 第{src['episode']}集 {src['scene']}")