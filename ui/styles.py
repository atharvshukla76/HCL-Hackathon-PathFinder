import streamlit as st

def apply_custom_styles():
    st.markdown(
        """
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Apply fonts and hide defaults */
        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Chat bubble styling overrides */
        .stChatMessage {
            background-color: transparent;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        
        /* Thinking animation dots */
        .thinking-dots {
            display: inline-block;
        }
        .thinking-dots span {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #666;
            margin: 0 2px;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        .thinking-dots span:nth-child(1) { animation-delay: -0.32s; }
        .thinking-dots span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
        
        /* Roadmap Card */
        .roadmap-card {
            background-color: #1E1E24;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            transition: transform 0.2s;
        }
        .roadmap-card:hover {
            border-color: #555;
        }
        .roadmap-step {
            color: #888;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 4px;
        }
        .roadmap-skill {
            font-size: 1.2rem;
            font-weight: 700;
            color: #FFF;
            margin-bottom: 8px;
        }
        .roadmap-details {
            display: flex;
            gap: 16px;
            font-size: 0.9rem;
            color: #BBB;
            margin-bottom: 12px;
        }
        .roadmap-reason {
            color: #ccc;
            font-size: 0.95rem;
            margin: 12px 0;
            line-height: 1.5;
        }
        
        .roadmap-segment-tag {
            display: inline-block;
            background: rgba(76, 175, 80, 0.15);
            color: #4CAF50;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-top: 6px;
            border: 1px solid rgba(76, 175, 80, 0.3);
        }
        
        .roadmap-link {
            color: #4CAF50;
            text-decoration: none;
            font-weight: 500;
        }
        
        .roadmap-link:hover {
            text-decoration: underline;
        }
        
        /* Flowchart Styles */
        .flowchart-container {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 10px;
            margin: 20px 0 30px 0;
            padding: 20px;
            background: rgba(30, 30, 36, 0.5);
            border-radius: 12px;
            border: 1px solid #333;
        }
        
        .flowchart-node {
            background: linear-gradient(145deg, #222228, #1a1a1f);
            border: 1px solid #555;
            padding: 8px 16px;
            border-radius: 20px;
            color: #fff;
            font-size: 0.9rem;
            font-weight: 600;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        
        .flowchart-arrow {
            color: #4CAF50;
            font-weight: bold;
            font-size: 1.2rem;
        }
        
        
        /* Dashboard Animations */
        @keyframes slideFill {
            from { width: 0%; }
        }
        @keyframes pulseGlow {
            0% { box-shadow: 0 0 5px rgba(76, 175, 80, 0.2); }
            50% { box-shadow: 0 0 15px rgba(76, 175, 80, 0.6); }
            100% { box-shadow: 0 0 5px rgba(76, 175, 80, 0.2); }
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .metric-dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin: 20px 0;
            animation: fadeIn 0.6s ease-out forwards;
        }
        
        .metric-card {
            background: linear-gradient(145deg, #222228, #1a1a1f);
            border: 1px solid #333;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            position: relative;
            overflow: hidden;
            transition: transform 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            border-color: #4CAF50;
            animation: pulseGlow 2s infinite;
        }
        
        .metric-title {
            color: #888;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
            font-weight: 600;
        }
        
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #fff;
            margin-bottom: 8px;
        }
        
        .metric-bar-bg {
            height: 6px;
            background-color: #333;
            border-radius: 3px;
            width: 100%;
            overflow: hidden;
        }
        
        .metric-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #8BC34A);
            border-radius: 3px;
            animation: slideFill 1.5s cubic-bezier(0.1, 0.7, 0.1, 1) forwards;
        }
        
        .metric-focus {
            background: linear-gradient(90deg, #FF9800, #FFC107);
        }
        /* AI Core Animation */
        @keyframes pulseCore {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(76, 175, 80, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(76, 175, 80, 0); }
        }
        
        .ai-core-container {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
            padding: 10px;
            background: rgba(30, 30, 36, 0.6);
            border-radius: 8px;
            border-left: 3px solid #4CAF50;
        }
        
        .ai-core-dot {
            width: 12px;
            height: 12px;
            background-color: #4CAF50;
            border-radius: 50%;
            animation: pulseCore 2s infinite;
        }
        
        .ai-core-text {
            color: #E0E0E0;
            font-weight: 600;
            font-size: 0.9rem;
            letter-spacing: 0.5px;
        }

        /* Sidebar Cards */
        .sidebar-card {
            background-color: #1a1a1f;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .sidebar-title {
            color: #888;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 6px;
        }
        
        .sidebar-value {
            color: #fff;
            font-size: 1rem;
            font-weight: 600;
        }
        
        .sidebar-value.highlight {
            color: #FF9800;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
