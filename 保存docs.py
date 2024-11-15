import json
from langchain_community.document_loaders import PyPDFLoader

loaders = [
    PyPDFLoader('物理知识文档/八年级上.pdf'),
    PyPDFLoader('物理知识文档/八年级下.pdf'),
    PyPDFLoader('物理知识文档/九年级.pdf'),
    PyPDFLoader('物理知识文档/高中必修一.pdf'),
    PyPDFLoader('物理知识文档/高中必修二.pdf'),
    PyPDFLoader('物理知识文档/高中必修三.pdf'),
    PyPDFLoader('物理知识文档/高中选择性必修一.pdf'),
    PyPDFLoader('物理知识文档/高中选择性必修二.pdf'),
    PyPDFLoader('物理知识文档/高中选择性必修三.pdf')
]

# docs = []
# for loader in loaders:
#     docs.extend(loader.load())
docs = []
for loader in loaders:
    loaded_docs = loader.load()
    for doc in loaded_docs:
        # 显式设置metadata
        doc.metadata['source'] = loader.file_path  # 设置source为文件路径
    docs.extend(loaded_docs)
# 转换文档为可序列化的格式
docs_serializable = [{'content': doc.page_content, 'source': doc.metadata['source']} for doc in docs]

# 保存到 JSON 文件
with open('docs.json', 'w', encoding='utf-8') as f:
    json.dump(docs_serializable, f, ensure_ascii=False, indent=4)
