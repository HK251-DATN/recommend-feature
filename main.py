import sys
from chatbot_agent import extract_keywords, generate_chat_response
from search_engine import search_hybrid, search_keyword, search_vector

def main():
    print("=========================================")
    print("=== Hệ Thống Gợi Ý Sản Phẩm (Chatbot) ===")
    print("=========================================")
    print("Nhập 'exit' hoặc 'quit' để thoát.")
    
    while True:
        try:
            user_msg = input("\nBạn: ")
            if user_msg.lower() in ['exit', 'quit']:
                print("Tạm biệt!")
                break
                
            print("\n[Hệ thống] Đang phân tích yêu cầu của bạn bằng Gemini API...")
            keywords = extract_keywords(user_msg)
            print(f"[Debug] Từ khoá trích xuất được: {keywords}")
            
            if not keywords:
                print("Chatbot: Xin chào! Bạn đang cần tìm kiếm hoặc mua sản phẩm gì hôm nay?")
                continue
                
            # Perform search (using Hybrid by default)
            print("[Hệ thống] Đang tìm kiếm trong Elasticsearch (Hybrid Search)...")
            results = search_hybrid(keywords, top_k=5)
            
            if not results:
                print("Chatbot: Xin lỗi, hiện tại tôi không tìm thấy sản phẩm nào phù hợp với yêu cầu của bạn.")
                continue
                
            print("[Debug] Top sản phẩm tìm thấy:")
            for p in results:
                print(f"   - {p['product_name']} (Điểm: {p['score']:.4f})")
                
            # Generate final response
            print("\n[Hệ thống] Đang tạo câu trả lời tự nhiên bằng Gemini API...")
            response = generate_chat_response(user_msg, results)
            print(f"\nChatbot: {response}")
            
        except KeyboardInterrupt:
            print("\nTạm biệt!")
            break
        except Exception as e:
            print(f"Lỗi hệ thống: {e}")

if __name__ == "__main__":
    main()
