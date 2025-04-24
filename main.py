import streamlit as st
from ai_generated_analyzer import AIGeneratedAnalyzer
import io
import docx2txt
import PyPDF2
import pandas as pd

def extract_text_from_file(uploaded_file):
    """Extract text from various file formats"""
    file_type = uploaded_file.type
    
    try:
        if 'text/plain' in file_type:
            # Text files
            return uploaded_file.getvalue().decode('utf-8')
            
        elif 'application/pdf' in file_type:
            # PDF files
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
            
        elif 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in file_type:
            # DOCX files
            return docx2txt.process(io.BytesIO(uploaded_file.getvalue()))
            
        elif 'application/vnd.ms-excel' in file_type or 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in file_type:
            # Excel files
            df = pd.read_excel(io.BytesIO(uploaded_file.getvalue()))
            return df.to_string()
            
        else:
            return None
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def main():
    st.set_page_config(page_title="AI Content Detector", page_icon="🧠", layout="wide")
    
    # Modern UI styling
    st.markdown("""
    <style>
        /* Global styling */
        .main {
            padding: 2.5rem;
            background-color: #f0f4f8;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Header styling */
        h1, h2, h3 {
            font-family: 'Poppins', 'Segoe UI', Tahoma, sans-serif;
            color: #1a365d;
            letter-spacing: -0.5px;
        }
        
        h1 {
            font-weight: 700;
            font-size: 2.4rem;
            margin-bottom: 1rem;
            background: linear-gradient(90deg, #1a365d 0%, #3182ce 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: inline-block;
        }
        
        /* Cards for different sections */
        .card {
            border-radius: 16px;
            padding: 1.8rem;
            background: white;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
            margin-bottom: 1.8rem;
            border: 1px solid rgba(226, 232, 240, 0.8);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .card:hover {
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }
        
        /* Results styling */
        .score-box {
            padding: 1.4rem;
            border-radius: 12px;
            margin: 1.2rem 0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        }
        
        .score-box:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
        }
        
        .ai-generated {
            background-color: #fff5f5;
            border-left: 6px solid #e53e3e;
            background-image: linear-gradient(to right, rgba(229, 62, 62, 0.05), transparent);
        }
        
        .human-written {
            background-color: #f0fff4;
            border-left: 6px solid #38a169;
            background-image: linear-gradient(to right, rgba(56, 161, 105, 0.05), transparent);
        }
        
        /* Pattern styling */
        .pattern-box {
            padding: 1.2rem;
            margin: 0.6rem 0;
            border-left: 4px solid #4299e1;
            background-color: #f7fafc;
            border-radius: 0 8px 8px 0;
        }
        
        /* Input textarea styling */
        .stTextArea textarea {
            border-radius: 10px;
            border: 1px solid #e2e8f0;
            padding: 12px;
            font-family: 'Inter', system-ui, sans-serif;
            font-size: 1rem;
            transition: all 0.2s ease;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.02);
        }
        
        .stTextArea textarea:focus {
            border-color: #4299e1;
            box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.15);
        }
        
        /* File uploader styling */
        [data-testid="stFileUploader"] {
            border-radius: 10px;
            border: 2px dashed #e2e8f0;
            padding: 0.5rem;
            transition: all 0.2s ease;
        }
        
        [data-testid="stFileUploader"]:hover {
            border-color: #4299e1;
            background-color: rgba(66, 153, 225, 0.02);
        }
        
        /* Button styling */
        .stButton button {
            background-image: linear-gradient(to right, #3182ce, #4299e1);
            color: white;
            border-radius: 10px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            border: none;
            transition: all 0.3s;
            box-shadow: 0 4px 10px rgba(66, 153, 225, 0.2);
            text-transform: uppercase;
            font-size: 0.9rem;
            letter-spacing: 0.5px;
        }
        
        .stButton button:hover {
            background-image: linear-gradient(to right, #2c5282, #3182ce);
            box-shadow: 0 6px 15px rgba(49, 130, 206, 0.3);
            transform: translateY(-2px);
        }
        
        .stButton button:active {
            transform: translateY(0);
            box-shadow: 0 2px 6px rgba(49, 130, 206, 0.2);
        }
        
        /* Progress bar styling */
        [data-testid="stProgress"] > div > div {
            background-image: linear-gradient(to right, #3182ce, #4299e1);
            border-radius: 100px;
        }
        
        [data-testid="stProgress"] {
            height: 10px;
            border-radius: 100px;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 0.5rem 1rem;
            font-weight: 500;
        }
        
        .stTabs [data-baseweb="tab-highlight"] {
            background-color: #4299e1;
            border-radius: 8px;
            height: 3px;
            bottom: -2px;
        }
        
        /* Info box styling */
        .stAlert {
            border-radius: 10px;
            border-left-width: 6px !important;
        }
        
        /* Layout for columns */
        [data-testid="stHorizontalBlock"] {
            gap: 2.5rem;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            font-size: 1rem;
            font-weight: 600;
            border-radius: 8px;
            background-color: #f7fafc;
            border: 1px solid #e2e8f0;
            padding: 0.75rem 1rem;
            transition: all 0.2s ease;
        }
        
        .streamlit-expanderHeader:hover {
            background-color: #edf2f7;
            border-color: #cbd5e0;
        }
        
        /* Animation for loading */
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .stSpinner > div {
            animation: pulse 1.5s infinite ease-in-out;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("🧠 AI Content Detector")
    st.markdown("<div class='card'><p style='font-size: 1.1rem; line-height: 1.6; color: #4a5568;'>Upload a file or paste text to analyze whether content was generated by AI or written by a human.</p></div>", unsafe_allow_html=True)
    
    left_col, right_col = st.columns([2, 3])
    with left_col:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Input Content")
        
        # Create tabs for different input methods
        input_tab, file_tab = st.tabs(["📝 Text Input", "📁 File Upload"])
        
        with input_tab:
            with st.form("analysis_form_text"):
                text_input = st.text_area(
                    "Paste your text below (min 200 characters):", 
                    height=350,
                    label_visibility="collapsed",
                    placeholder="Enter or paste your text here for analysis (minimum 200 characters)..."
                )
                analyze_text_button = st.form_submit_button("🔍 Analyze Text")
                
        with file_tab:
            with st.form("analysis_form_file"):
                st.markdown("""
                <div style="margin-bottom: 1rem; text-align: center;">
                    <div style="font-size: 3rem; margin-bottom: 0.5rem;">📄</div>
                    <div style="font-weight: 600; margin-bottom: 0.5rem; color: #4a5568;">Upload a document</div>
                    <p style="color: #718096; font-size: 0.9rem; margin-bottom: 1rem;">Supported formats: TXT, PDF, DOCX, XLSX, XLS</p>
                </div>
                """, unsafe_allow_html=True)
                
                uploaded_file = st.file_uploader(
                    "Upload a document (TXT, PDF, DOCX, XLSX)",
                    type=["txt", "pdf", "docx", "xlsx", "xls"],
                    label_visibility="collapsed"
                )
                if uploaded_file is not None:
                    file_ext = uploaded_file.name.split('.')[-1].lower()
                    file_icon = {
                        'txt': '📄',
                        'pdf': '📕',
                        'docx': '📘',
                        'xlsx': '📊',
                        'xls': '📊'
                    }.get(file_ext, '📄')
                    
                    st.markdown(f"""
                    <div style="padding: 0.8rem; border-radius: 8px; background-color: #ebf8ff; display: flex; align-items: center; margin-top: 1rem;">
                        <div style="font-size: 1.5rem; margin-right: 0.8rem;">{file_icon}</div>
                        <div>
                            <div style="font-weight: 600; color: #2b6cb0;">{uploaded_file.name}</div>
                            <div style="font-size: 0.85rem; color: #4a5568;">{round(uploaded_file.size/1024, 1)} KB</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                analyze_file_button = st.form_submit_button("🔍 Analyze File")
                
        st.markdown("</div>", unsafe_allow_html=True)
        
    with right_col:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Analysis Results")

        result = st.session_state.get('result', None)
        if result:
            score_col, conclusion_col = st.columns([1, 2])
            with score_col:
                gauge_color = "red" if result['score'] > 70 else "orange" if result['score'] > 40 else "green"
                st.markdown(f"""
                <div style="text-align: center; padding: 0.5rem;">
                    <h4 style="margin-bottom: 0.5rem; font-size: 1.1rem; color: #64748b;">AI Score</h4>
                    <div style="position: relative; width: 150px; height: 150px; margin: 0 auto; border-radius: 50%; background: conic-gradient({gauge_color} {result['score']}%, #e2e8f0 0); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                        <div style="width: 120px; height: 120px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                            <div style="font-size: 2.5rem; font-weight: bold; color: {gauge_color}; text-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                                {result['score']}
                            </div>
                        </div>
                    </div>
                    <div style="margin-top: 1rem; font-size: 0.9rem; color: #64748b;">
                        Score out of 100
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with conclusion_col:
                conclusion_class = "ai-generated" if result['score'] > 70 else "human-written"
                conclusion_icon = "🤖" if result['score'] > 70 else "👨‍💻"
                conclusion_title = "AI-Generated Content" if result['score'] > 70 else "Human-Written Content"
                confidence_level = "High" if result['score'] > 85 or result['score'] < 15 else "Medium" if result['score'] > 70 or result['score'] < 30 else "Moderate"
                
                st.markdown(f"""
                <div class="score-box {conclusion_class}">
                    <h3 style="margin-top: 0; display: flex; align-items: center; font-size: 1.6rem;">
                        <span style="margin-right: 0.5rem; font-size: 1.8rem;">{conclusion_icon}</span> 
                        {conclusion_title}
                    </h3>
                    <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid rgba(0,0,0,0.05);">
                        <span style="font-weight: 600; color: #4a5568;">Confidence:</span> 
                        <span style="display: inline-block; padding: 0.2rem 0.6rem; border-radius: 1rem; font-size: 0.85rem; font-weight: 600; background-color: {'rgba(229, 62, 62, 0.1)' if result['score'] > 70 else 'rgba(56, 161, 105, 0.1)'}; color: {'#e53e3e' if result['score'] > 70 else '#38a169'};">{confidence_level}</span>
                    </div>
                    <p style="margin-top: 0.8rem; color: #4a5568; line-height: 1.5;">
                        {result['conclusion']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
            st.subheader("Detection Patterns")
            if result['patterns']:
                st.markdown("""
                <div style="margin-bottom: 1rem; padding: 0.8rem; background-color: #f7fafc; border-radius: 8px; font-size: 0.9rem; color: #4a5568;">
                    The following patterns were detected in the analyzed content. Each pattern contributes to the overall AI score.
                </div>
                """, unsafe_allow_html=True)
                
                for pattern in result['patterns']:
                    confidence_color = {
                        "High": "#e53e3e",
                        "Medium": "#dd6b20",
                        "Low": "#d69e2e"
                    }.get(pattern['confidence'], "#718096")
                    
                    confidence_bg = {
                        "High": "rgba(229, 62, 62, 0.1)",
                        "Medium": "rgba(221, 107, 32, 0.1)",
                        "Low": "rgba(214, 158, 46, 0.1)"
                    }.get(pattern['confidence'], "rgba(113, 128, 150, 0.1)")
                    
                    confidence_icon = {
                        "High": "🔴",
                        "Medium": "🟠",
                        "Low": "🟡"
                    }.get(pattern['confidence'], "⚪")
                    
                    with st.expander(f"{confidence_icon} {pattern['pattern']}"):
                        st.markdown(f"""
                        <div class="pattern-box">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                                <div style="font-weight: 600; color: #2d3748; font-size: 1.05rem;">{pattern['pattern']}</div>
                                <div style="padding: 0.2rem 0.8rem; border-radius: 1rem; font-size: 0.8rem; font-weight: 600; background-color: {confidence_bg}; color: {confidence_color};">
                                    {pattern['confidence']} Confidence
                                </div>
                            </div>
                            <p style="color: #4a5568; line-height: 1.6; margin-top: 0.5rem;">{pattern['description']}</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="padding: 1.5rem; text-align: center; background-color: #f7fafc; border-radius: 8px; color: #4a5568; border: 1px dashed #cbd5e0;">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔍</div>
                    <div style="font-weight: 600; margin-bottom: 0.5rem;">No Significant Patterns Detected</div>
                    <p style="color: #718096; font-size: 0.9rem;">The analysis did not find any significant AI-generated content patterns in the text.</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="padding: 2rem 1rem; text-align: center; height: 100%;">
                <div style="font-size: 4rem; color: #a0aec0; margin-bottom: 1.5rem;">📊</div>
                <h3 style="color: #4a5568; margin-bottom: 1rem; font-weight: 600;">No Analysis Results Yet</h3>
                <p style="color: #718096; max-width: 400px; margin: 0 auto; line-height: 1.6;">
                    Enter text or upload a file on the left panel to analyze and detect whether content was created by AI or written by a human.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

    # Initialize analyzer once
    analyzer = AIGeneratedAnalyzer()

    # Process text input form
    if 'analyze_text_button' in locals() and analyze_text_button:
        if len(text_input) < 200:
            st.error("Please input at least 200 characters for accurate analysis.")
            st.session_state.result = None
        else:
            with st.spinner("Analyzing text... Please wait."):
                try:
                    result = analyzer.analyze_text(text_input)
                    st.session_state.result = result
                    st.rerun()
                except Exception as e:
                    st.session_state.result = None
                    st.error(f"Analysis failed: {str(e)}")

    # Process file upload form
    if 'analyze_file_button' in locals() and analyze_file_button:
        if uploaded_file is None:
            st.error("Please upload a file first.")
            st.session_state.result = None
        else:
            with st.spinner("Processing file and analyzing content... Please wait."):
                extracted_text = extract_text_from_file(uploaded_file)
                if extracted_text and len(extracted_text) >= 200:
                    try:
                        result = analyzer.analyze_text(extracted_text)
                        st.session_state.result = result
                        st.rerun()
                    except Exception as e:
                        st.session_state.result = None
                        st.error(f"Analysis failed: {str(e)}")
                else:
                    st.error("Could not extract sufficient text (minimum 200 characters) from the file.")
                    st.session_state.result = None

if __name__ == "__main__":
    main()