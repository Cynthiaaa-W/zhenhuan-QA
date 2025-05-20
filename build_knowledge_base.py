from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import DirectoryLoader, JSONLoader
import os
from pathlib import Path
from typing import Dict, Any

# 配置参数
LOCAL_MODEL_PATH = "./local_models/bge-small-zh-v1.5"
CHROMA_DB_PATH = "./chroma_db"
DATA_DIR = "processed"


def metadata_func(record: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """从JSON记录中提取元数据"""
    metadata.update({
        "episode": record.get("episode_number", 0),
        "title": record.get("episode_title", ""),
        "scene_number": record.get("scene_number", ""),
        "location": record.get("location", ""),
        "characters": ", ".join(record.get("characters", []))
    })
    return metadata


def load_documents(data_dir: str = DATA_DIR):
    """加载处理后的剧本数据"""
    loader = DirectoryLoader(
        path=data_dir,
        glob="*.json",
        loader_cls=JSONLoader,
        loader_kwargs={
            "jq_schema": ".scenes[]",  # 直接从scenes数组提取
            "content_key": "content",  # 对应新格式中的content字段
            "metadata_func": metadata_func,
            "text_content": True  # 确保返回原始文本
        },
        show_progress=True
    )
    return loader.load()


def build_knowledge_base():
    # 初始化文本分割器（保持原有参数）
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        length_function=len,
        add_start_index=True
    )

    # 加载并分割文档
    print("⏳ 正在加载文档...")
    documents = load_documents()
    print(f"📄 原始文档数: {len(documents)}")

    splits = text_splitter.split_documents(documents)
    print(f"✂️ 分割后文档块数: {len(splits)}")

    # 初始化本地嵌入模型（保持不变）
    print("🔧 正在加载嵌入模型...")
    embedding = HuggingFaceEmbeddings(
        model_name=LOCAL_MODEL_PATH,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    # 创建向量数据库（保持不变）
    print("🏗️ 正在构建向量数据库...")
    vectordb = Chroma.from_documents(
        documents=splits,
        embedding=embedding,
        persist_directory=CHROMA_DB_PATH,
        collection_name="zhenhuan_zhuan",
        collection_metadata={"hnsw:space": "cosine"}
    )

    # 保存数据库（保持不变）
    vectordb.persist()
    print(f"✅ 知识库构建完成！保存路径: {os.path.abspath(CHROMA_DB_PATH)}")


if __name__ == "__main__":
    build_knowledge_base()