from flask import Flask, request, jsonify
from flask_cors import CORS
from search_engine import search_keyword, search_vector, search_hybrid
from chatbot_agent import extract_keywords, generate_chat_response

app = Flask(__name__)
CORS(app)

@app.route("/api/search/keyword", methods=["GET"])
def api_search_keyword():
    """API for BM25 Keyword Search"""
    query = request.args.get("q", "")
    top_k = int(request.args.get("top_k", 5))
    
    if not query:
        return jsonify({"error": "Vui lòng truyền tham số 'q' (query)"}), 400
        
    try:
        results = search_keyword(query, top_k)
        return jsonify({
            "status": "success",
            "query": query,
            "top_k": top_k,
            "data": results
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/search/vector", methods=["GET"])
def api_search_vector():
    """API for k-NN Vector Search"""
    query = request.args.get("q", "")
    top_k = int(request.args.get("top_k", 5))
    
    if not query:
        return jsonify({"error": "Vui lòng truyền tham số 'q' (query)"}), 400
        
    try:
        results = search_vector(query, top_k)
        return jsonify({
            "status": "success",
            "query": query,
            "top_k": top_k,
            "data": results
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/search/hybrid", methods=["GET"])
def api_search_hybrid():
    """API for Hybrid Search (Keyword + Vector)"""
    query = request.args.get("q", "")
    top_k = int(request.args.get("top_k", 5))
    
    if not query:
        return jsonify({"error": "Vui lòng truyền tham số 'q' (query)"}), 400
        
    try:
        results = search_hybrid(query, top_k)
        return jsonify({
            "status": "success",
            "query": query,
            "top_k": top_k,
            "data": results
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """API for Chatbot interaction"""
    data = request.json
    if not data or "message" not in data:
        return jsonify({"error": "Yêu cầu body chứa trường 'message'"}), 400
        
    user_msg = data["message"]
    
    try:
        # 1. Trích xuất từ khoá
        keywords = extract_keywords(user_msg)
        
        if not keywords:
            return jsonify({
                "status": "success",
                "chat_response": "Xin chào! Bạn đang cần tìm kiếm hoặc mua sản phẩm gì hôm nay?",
                "recommended_products": [],
                "extracted_keywords": ""
            })
            
        # 2. Tìm kiếm sản phẩm
        results = search_hybrid(keywords, top_k=5)
        
        if not results:
            return jsonify({
                "status": "success",
                "chat_response": "Xin lỗi, hiện tại tôi không tìm thấy sản phẩm nào phù hợp với yêu cầu của bạn.",
                "recommended_products": [],
                "extracted_keywords": keywords
            })
            
        # 3. Tạo câu trả lời tự nhiên
        chat_response = generate_chat_response(user_msg, results)
        
        return jsonify({
            "status": "success",
            "chat_response": chat_response,
            "recommended_products": results,
            "extracted_keywords": keywords
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Cấu hình host="0.0.0.0" để có thể gọi từ bên ngoài vào
    app.run(host="0.0.0.0", port=5000, debug=True)
