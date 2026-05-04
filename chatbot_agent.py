import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY is not set in .env file.")

def extract_keywords(user_message: str) -> str:
    """
    Uses Gemini API to extract search keywords from the user's message.
    """
    if not GEMINI_API_KEY:
        # Fallback if no API key is provided
        return user_message
        
    prompt = f"""
    Bạn là một trợ lý AI phân tích ngôn ngữ cho một hệ thống gợi ý sản phẩm thương mại điện tử (đặc biệt là thực phẩm, rau củ quả, thịt cá).
    Nhiệm vụ của bạn là trích xuất các từ khoá tìm kiếm quan trọng nhất từ tin nhắn của người dùng để đưa vào công cụ tìm kiếm (Elasticsearch).
    
    Chỉ trả về các từ khoá, phân tách nhau bởi dấu phẩy, không giải thích gì thêm.
    Nếu người dùng chào hỏi bình thường mà không nói muốn mua gì, hãy trả về rỗng.
    
    Tin nhắn của người dùng: "{user_message}"
    Từ khoá:
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        keywords = response.text.strip()
        return keywords
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        # Fallback to the original message if API fails
        return user_message

def generate_chat_response(user_message: str, recommended_products: list) -> str:
    """
    Generates a natural language response based on the recommended products.
    """
    if not GEMINI_API_KEY or not recommended_products:
        return "Đây là các sản phẩm tôi tìm thấy cho bạn."
        
    products_text = "\n".join([f"- {p['product_name']} (Giá: {p['min_price']} VND)" for p in recommended_products])
    
    prompt = f"""
    Bạn là một nhân viên bán hàng thân thiện. 
    Người dùng vừa nhắn: "{user_message}"
    Hệ thống đã tìm thấy các sản phẩm sau:
    {products_text}
    
    Hãy viết một câu trả lời ngắn gọn, thân thiện để giới thiệu các sản phẩm này cho người dùng.
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "Đây là các sản phẩm tôi tìm thấy cho bạn."
