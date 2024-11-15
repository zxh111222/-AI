
'''
# 载入多个中文知识库
# 旧的导入方式，已弃用
# from langchain.document_loaders import UnstructuredFileLoader
# from langchain.document_loaders import PyPDFLoader
# 新的导入方式
from langchain_community.document_loaders import UnstructuredFileLoader
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

docs = []
for loader in loaders:
    docs.extend(loader.load())

'''

# # docs是一个列表，每个元素表示一个文档，并保存了对应的出处
# len(docs)
# docs[50]


import json
from langchain.schema import Document

# 从 JSON 文件加载文档 - 避免每次重复运行，节约时间
with open('docs.json', 'r', encoding='utf-8') as f:
    docs_serializable = json.load(f)

# 恢复为原始文档对象
docs = [Document(page_content=doc['content'], metadata={'source': doc['source']}) for doc in docs_serializable]


# 对数据进行预处理，如分词、去停用词等
import jieba

# 停用词表（可以根据需要加载本地停用词文件）
stopwords = set(["的", "了", "和", "是", "在", "上", "与", "为", "有", "我", "你", "他", "她", "它"])

def preprocess_text(text):
    # 中文分词
    words = jieba.cut(text)
    # 去除停用词
    words_filtered = [word for word in words if word not in stopwords]
    return " ".join(words_filtered)

# 对所有文档进行预处理
processed_docs = [preprocess_text(doc.page_content) for doc in docs]
# 转换为 `Document` 对象
processed_docs = [Document(page_content=doc) for doc in processed_docs]


# 文档切分为若干chunk文本块
from langchain.text_splitter import CharacterTextSplitter

text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=30, separator='\n')
splits = text_splitter.split_documents(processed_docs)
# len(splits)
# splits[100]

# Embedding算法
# 开源免费算法 --- 在线下载
from langchain.embeddings import HuggingFaceEmbeddings

# embeddings = HuggingFaceEmbeddings(model_name='shibing624/text2vec-base-chinese')
# embeddings = HuggingFaceEmbeddings(model_name='GanymedeNil/text2vec-large-chinese')
embeddings = HuggingFaceEmbeddings(model_name='moka-ai/m3e-base')


# 提取每个chunk文本块的Embedding向量，构建知识库文本-向量数据库
from langchain.vectorstores import FAISS

vector_store = FAISS.from_documents(splits, embeddings)

# 提问，在知识库中匹配出相关段落
# 提一个与知识库有关的问题
# 一个小球从一定高度自由下落，在不考虑空气阻力的情况下，小球在下落过程中动能和势能是如何变化的？如何计算它的落地速度？
# 在一个闭合电路中，电流产生的磁场如何影响相邻导线中的电流？如何应用安培定律或法拉第定律来分析这种现象？
# 当光从空气进入水中时，折射角会如何变化？如果入射角是 45 度，如何计算折射角？
# 一个密闭容器内的气体温度升高，压力会发生什么变化？在等压条件下，如何使用理想气体状态方程解释气体的体积变化？
# 在同一个介质中传播的两列波发生干涉时会形成哪些现象？如何确定它们的波节和波腹？
# 一带电粒子在匀强磁场中做圆周运动，如何计算它的运动轨迹和周期？如何运用洛伦兹力公式来解释这种现象？
question = '一个小球从一定高度自由下落，在不考虑空气阻力的情况下，小球在下落过程中动能和势能是如何变化的？如何计算它的落地速度？'

# 在知识库文本-向量数据库中，匹配相关段落，按相关性倒序排序
K = 5  # 返回前5个最相关的文档
docs_and_scores = vector_store.similarity_search_with_score(question, k=K)

# for i in range(len(docs_and_scores)):
#     source = docs_and_scores[i][0].metadata.get('source', '未知来源')  # 使用get方法避免KeyError
#     content = docs_and_scores[i][0].page_content
#     similarity = docs_and_scores[i][1]
#     print('来源 {} 字数 {} 匹配度 {:.2f}'.format(source, len(content), similarity))
#     print(content[:30] + '……')
#     print('------------------')

# 生成提示词Prompt
# 生成背景上下文
context = ''
for doc in docs_and_scores:
    context += doc[0].page_content
    context += '\n'

# 生成提示词
prompt = '你是一个学习助手，请根据下面的已知信息回答问题，你只需要回答和已知信息相关的问题，如果问题和已知信息不相关，你可以直接回答"不知道" 问题：{} 已知信息:{}'.format(
    question, context)

# 文心大模型API
# 填入文心大模型后台你自己的API信息
from baidu_ernie import BaiduErnie

client_id = "Ag49f0uNIEmD6ePhajgMopLq"
client_secret = "l08YIKV4pZPn6lcLZVhs7lGjogXDC7ru"
baidu_ernie = BaiduErnie(client_id, client_secret)

user_id = "user1"


def chat(prompt):
    messages = []
    messages.append({"role": "user", "content": prompt})  # 用户输入
    result, response = baidu_ernie.chat(messages, user_id)  # 调用接口
    return result


# # 小小测一下
# result = chat('你是哪家公司开发的什么大语言模型？')
# print(result)


# 将提示词Prompt输入给文心大模型，获得输出结果

def predict(question):
    # 匹配K段知识库原文
    docs_and_scores = vector_store.similarity_search_with_score(question, k=K)

    # 构建背景材料字符串
    context = ''
    for doc in docs_and_scores:
        context += doc[0].page_content
        context += '\n'

    # 构建提示词
    prompt = '你是一个学习助手，请根据下面的已知信息回答问题，你只需要回答和已知信息相关的问题，如果问题和已知信息不相关，你可以直接回答"不知道" 问题：{} 已知信息:{}'.format(
        question, context)

    # 输入文心大模型
    result = chat(prompt)
    print(result)



predict(
    '光是什么')
# predict(
#     '一个小球从一定高度自由下落，在不考虑空气阻力的情况下，小球在下落过程中动能和势能是如何变化的？如何计算它的落地速度？')
