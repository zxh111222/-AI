import json
import jieba
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from baidu_ernie import BaiduErnie


class KnowledgeBase:
    def __init__(self, docs_file: str, client_id: str, client_secret: str):
        # 加载文档
        with open(docs_file, 'r', encoding='utf-8') as f:
            self.docs_serializable = json.load(f)
        self.docs = [Document(page_content=doc['content'], metadata={'source': doc['source']}) for doc in
                     self.docs_serializable]

        # 文本预处理
        self.stopwords = set(["的", "了", "和", "是", "在", "上", "与", "为", "有", "我", "你", "他", "她", "它"])
        self.processed_docs = [self.preprocess_text(doc.page_content) for doc in self.docs]
        self.processed_docs = [Document(page_content=doc) for doc in self.processed_docs]

        # 文档切分
        text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=30, separator='\n')
        self.splits = text_splitter.split_documents(self.processed_docs)

        # 初始化文心大模型API
        self.ba_ernie = BaiduErnie(client_id, client_secret)

        # 初始化嵌入
        self.embeddings = HuggingFaceEmbeddings(model_name='moka-ai/m3e-base')

        # 创建FAISS向量数据库
        self.vector_store = FAISS.from_documents(self.splits, self.embeddings)

    def preprocess_text(self, text):
        # 中文分词并去除停用词
        words = jieba.cut(text)
        words_filtered = [word for word in words if word not in self.stopwords]
        return " ".join(words_filtered)

    def chat(self, prompt: str) -> str:
        # 通过文心大模型进行问答
        messages = [{"role": "user", "content": prompt}]
        user_id = "user1"
        result, _ = self.ba_ernie.chat(messages, user_id)
        print(result)
        return result

    def predict(self, question: str) -> str:
        # 匹配知识库中最相关的文本
        docs_and_scores = self.vector_store.similarity_search_with_score(question, k=5)

        # 构建背景上下文
        context = ''.join([doc[0].page_content for doc in docs_and_scores])

        # 构建提示词
        prompt = f'你是一个学习助手，请根据下面的已知信息回答问题，你只需要回答和已知信息相关的问题，如果问题和已知信息不相关，你可以直接回答"不知道" 问题：{question} 已知信息:{context}'

        # 通过文心大模型进行回答
        return self.chat(prompt)
