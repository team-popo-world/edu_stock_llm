
def get_custom_css():
    """Streamlit 앱의 커스텀 CSS 스타일 반환"""
    return """
    <style>
        /* 메인 컨테이너 */
        .main > div {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* 헤더 스타일 */
        .main-header {
            text-align: center;
            padding: 2rem 0;
            margin-bottom: 3rem;
        }
        
        /* 카드 스타일 */
        .card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            border: 1px solid #f0f0f0;
            margin: 1rem 0;
        }
        
        /* 버튼 스타일 */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 2rem;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        
        /* 메트릭 카드 */
        .metric-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
            margin: 0.5rem 0;
        }
        
        /* 주식 카드 */
        .stock-card {
            background: white;
            border: 2px solid #f8f9fa;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            transition: all 0.3s ease;
        }
        
        .stock-card:hover {
            border-color: #667eea;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.1);
        }
        
        /* 성공 메시지 */
        .success-message {
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        /* 뉴스 카드 */
        .news-card {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
        }
        
        /* 스텝 인디케이터 */
        .step-indicator {
            display: flex;
            justify-content: center;
            margin: 2rem 0;
        }
        
        .step {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background: #e9ecef;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 0.5rem;
            font-weight: bold;
        }
        
        .step.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .step.completed {
            background: #28a745;
            color: white;
        }
        
        /* 숨기기 */
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        .stApp > header {visibility: hidden;}
    </style>
    """
