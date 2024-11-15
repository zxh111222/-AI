from flask import Flask, render_template, request, jsonify
from util import KnowledgeBase

app = Flask(__name__)

# 初始化 KnowledgeBase
client_id = "Ag49f0uNIEmD6ePhajgMopLq"
client_secret = "l08YIKV4pZPn6lcLZVhs7lGjogXDC7ru"
docs_file = "docs.json"
knowledge_base = KnowledgeBase(docs_file, client_id, client_secret)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    question = request.json['question']
    answer = knowledge_base.predict(question)

    # # 格式化返回的回答内容为 HTML
    # formatted_answer = answer.replace("\n\n", "<br>")  # 替换换行符为 <br> 标签
    # formatted_answer = formatted_answer.replace("**", "")  # 替换**为空
    # formatted_answer = formatted_answer.replace("$", "")  # 替换**为空
    # formatted_answer = formatted_answer.replace("\n", "<br>")  # 替换换行符为 <br> 标签
    # formatted_answer = formatted_answer.replace("\\\"", "&quot;")  # 转义引号

    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(debug=True)
