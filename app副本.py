import json
from flask import Flask, request, jsonify, Response
from util import KnowledgeBase  # 引入你之前的 KnowledgeBase 类

app = Flask(__name__)

# 初始化 KnowledgeBase 实例
# client_id = "jZKnHFH4hu3FU636DyGnkcxT"
# client_secret = "BjwRdlWaj7I6FZvYnotLW8ZweWcMFl63"
client_id = "Ag49f0uNIEmD6ePhajgMopLq"
client_secret = "l08YIKV4pZPn6lcLZVhs7lGjogXDC7ru"
kb = KnowledgeBase(docs_file="docs.json", client_id=client_id, client_secret=client_secret)

@app.route('/predict', methods=['GET'])
def predict():
    question = request.args.get('question')  # 从请求中获取问题

    if not question:
        return jsonify({'error': 'No question provided'}), 400

    # 获取模型的回答
    answer = kb.predict(question)

    # 格式化返回的回答内容为 HTML
    formatted_answer = answer.replace("\n\n", "<br>")  # 替换换行符为 <br> 标签
    formatted_answer = formatted_answer.replace("**", "")  # 替换**为空
    formatted_answer = formatted_answer.replace("$", "")  # 替换**为空
    formatted_answer = formatted_answer.replace("\n", "<br>")  # 替换换行符为 <br> 标签
    formatted_answer = formatted_answer.replace("\\\"", "&quot;")  # 转义引号

    # 生成最终的响应数据
    response_data = json.dumps({"answer": formatted_answer}, ensure_ascii=False)  # 确保不转义为ASCII
    return Response(response_data, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
