import streamlit as st
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import seaborn as sns
from objectdetection import analyze_all_images
import time

def select_folder():
    """
    Use Streamlit's native file uploader to select folders
    """
    uploaded_files = st.file_uploader("Select Image Folder", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'gif', 'bmp'])
    return uploaded_files

def save_uploaded_files(uploaded_files):
    """
    Save uploaded files to a temporary directory
    """
    if not uploaded_files:
        return None
    
    # Create a temporary directory
    import tempfile
    temp_dir = tempfile.mkdtemp()
    
    # Save uploaded files
    file_paths = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        file_paths.append(file_path)
    
    return temp_dir

def main():
    # Set page config FIRST, before any other Streamlit commands
    st.set_page_config(page_title="Phone Usage Analyzer", layout="wide")
    
    # Apply custom CSS with animations
    st.markdown("""
    <style>
        /* Main theme colors */
        :root {
            --primary-color: #4361ee;
            --secondary-color: #3f37c9;
            --background-color: #f8f9fa;
            --card-bg-color: #ffffff;
            --text-color: #212529;
            --light-text: #6c757d;
            --success-color: #4cc9f0;
            --warning-color: #f72585;
        }
        
        /* Animation keyframes */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        @keyframes slideIn {
            from { transform: translateX(-20px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        @keyframes glow {
            0% { box-shadow: 0 0 5px rgba(67, 97, 238, 0.5); }
            50% { box-shadow: 0 0 20px rgba(67, 97, 238, 0.8); }
            100% { box-shadow: 0 0 5px rgba(67, 97, 238, 0.5); }
        }
        
        /* Overall page styling with animation */
        .main {
            background-color: var(--background-color);
            padding: 1rem;
            animation: fadeIn 0.8s ease-out;
        }
        
        /* Header styling with animation */
        h1 {
            color: var(--primary-color);
            font-weight: 700;
            margin-bottom: 1.5rem;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--primary-color);
            animation: slideIn 0.8s ease-out;
        }
        
        h2, h3, .subheader {
            color: var(--secondary-color);
            font-weight: 600;
            margin-top: 2rem;
            animation: slideIn 0.6s ease-out;
        }
        
        /* Custom card styling for sections with animation */
        .css-card {
            border-radius: 10px;
            background-color: var(--card-bg-color);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            animation: fadeIn 0.8s ease-out;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .css-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
        }
        
        /* Button styling with animation */
        .stButton>button {
            background-color: var(--primary-color);
            color: white;
            border-radius: 5px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            animation: fadeIn 1s ease-out;
        }
        
        .stButton>button:hover {
            background-color: var(--secondary-color);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            transform: translateY(-3px) scale(1.02);
        }
        
        .stButton>button:active {
            transform: translateY(1px);
        }
        
        /* File uploader styling with animation */
        .uploadedFile {
            border: 1px dashed var(--primary-color);
            border-radius: 5px;
            padding: 10px;
            animation: fadeIn 1s ease-out;
            transition: all 0.3s ease;
        }
        
        .uploadedFile:hover {
            border-color: var(--secondary-color);
            background-color: rgba(67, 97, 238, 0.05);
        }
        
        /* Progress bar styling with animation */
        .stProgress > div > div {
            background-color: var(--success-color);
            animation: glow 2s infinite;
        }
        
        /* DataFrame styling with hover effect */
        .dataframe {
            font-family: 'Arial', sans-serif;
            border-collapse: collapse;
            width: 100%;
            animation: fadeIn 1s ease-out;
        }
        
        .dataframe th {
            background-color: var(--primary-color);
            color: white;
            padding: 12px;
            text-align: left;
        }
        
        .dataframe td {
            padding: 12px;
            border-bottom: 1px solid #ddd;
            transition: background-color 0.2s ease;
        }
        
        .dataframe tr:hover td {
            background-color: rgba(67, 97, 238, 0.1);
        }
        
        .dataframe tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        
        /* Image preview container with animation */
        .image-preview {
            border-radius: 8px;
            overflow: hidden;
            border: 2px solid #e9ecef;
            animation: fadeIn 1s ease-out;
            transition: all 0.3s ease;
        }
        
        .image-preview:hover {
            transform: scale(1.02);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        /* Emoji animations */
        .emoji {
            display: inline-block;
            animation: bounce 2s infinite ease-in-out;
        }
        
        /* Status messages with animation */
        .success-message {
            background-color: #d1e7dd;
            color: #0f5132;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            animation: fadeIn 0.5s ease-out;
            border-left: 4px solid #0f5132;
        }
        
        .error-message {
            background-color: #f8d7da;
            color: #842029;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            animation: fadeIn 0.5s ease-out;
            border-left: 4px solid #842029;
        }
        
        .info-message {
            background-color: #cfe2ff;
            color: #084298;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            animation: fadeIn 0.5s ease-out;
            border-left: 4px solid #084298;
        }
        
        /* Download button styling with animation */
        .stDownloadButton>button {
            background-color: var(--success-color);
            color: white;
            border-radius: 5px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            animation: fadeIn 1s ease-out;
        }
        
        .stDownloadButton>button:hover {
            background-color: #3da8d8;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            transform: translateY(-3px);
        }
        
        /* Loading animation */
        .loading {
            display: inline-block;
            position: relative;
            width: 80px;
            height: 80px;
        }
        
        .loading div {
            position: absolute;
            border: 4px solid var(--primary-color);
            opacity: 1;
            border-radius: 50%;
            animation: loading 1s cubic-bezier(0, 0.2, 0.8, 1) infinite;
        }
        
        .loading div:nth-child(2) {
            animation-delay: -0.5s;
        }
        
        @keyframes loading {
            0% {
                top: 36px;
                left: 36px;
                width: 0;
                height: 0;
                opacity: 1;
            }
            100% {
                top: 0px;
                left: 0px;
                width: 72px;
                height: 72px;
                opacity: 0;
            }
        }
        
        /* Staggered fade-in for list items */
        .staggered-item-1 { animation: fadeIn 0.5s ease-out 0.1s both; }
        .staggered-item-2 { animation: fadeIn 0.5s ease-out 0.2s both; }
        .staggered-item-3 { animation: fadeIn 0.5s ease-out 0.3s both; }
        .staggered-item-4 { animation: fadeIn 0.5s ease-out 0.4s both; }
        
        /* Tooltip styling */
        .tooltip {
            position: relative;
            display: inline-block;
            border-bottom: 1px dotted var(--primary-color);
        }
        
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 120px;
            background-color: var(--text-color);
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -60px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Animated app loading
    with st.spinner('Loading app...'):
        time.sleep(0.5)  # Short delay to show loading effect
    
    # Title and description with animated emoji
    st.markdown("<h1><span class='emoji'>📱</span> Phone Usage Analyzer</h1>", unsafe_allow_html=True)
    
    # Animated appearance of intro card
    intro_placeholder = st.empty()
    time.sleep(0.2)  # Brief delay for staggered animation
    intro_placeholder.markdown("""
    <div class="css-card">
        <p class="staggered-item-1">Upload your smartphone screenshots and images to analyze your phone usage patterns and understand their context.</p>
        <p class="staggered-item-2">This tool uses advanced image recognition to identify how you use your phone.</p>
        <p class="staggered-item-3"><span class="emoji">✨</span> </p>
    </div>
    """, unsafe_allow_html=True)

    # File Upload Section with animated appearance
    upload_header = st.empty()
    time.sleep(0.3)  # Brief delay for staggered animation
    upload_header.markdown("<h3><span class='emoji'>📁</span> Upload Images</h3>", unsafe_allow_html=True)
    
    upload_card = st.empty()
    time.sleep(0.2)  # Brief delay for staggered animation
    upload_card.markdown('<div class="css-card">', unsafe_allow_html=True)
    
    uploaded_files = select_folder()

    # Preview Images with staggered animation
    if uploaded_files:
        st.markdown("<h4 class='staggered-item-1'><span class='emoji'>📷</span> Image Preview</h4>", unsafe_allow_html=True)
        preview_cols = st.columns(4)
        
        for i, uploaded_file in enumerate(uploaded_files[:4]):
            try:
                img = Image.open(uploaded_file)
                with preview_cols[i]:
                    # Staggered animation for each image
                    time.sleep(0.1)
                    st.markdown(f'<div class="image-preview staggered-item-{i+1}">', unsafe_allow_html=True)
                    st.image(img, caption=uploaded_file.name, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<div class="error-message">Error loading preview image {uploaded_file.name}: {e}</div>', unsafe_allow_html=True)
    
    # Analyze Button with enhanced styling and animation
    button_cols = st.columns([1, 2, 1])
    with button_cols[1]:
        time.sleep(0.3)  # Brief delay for animated appearance
        analyze_button = st.button("🔍 Analyze Images", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close the upload card

    # Analysis Logic with animated status updates
    if analyze_button:
        # Validate file upload
        if not uploaded_files:
            st.markdown('<div class="error-message"><span class="emoji">⚠️</span> Please upload images</div>', unsafe_allow_html=True)
            return

        # Progress indicators with animation
        analysis_card = st.empty()
        time.sleep(0.2)
        analysis_card.markdown('<div class="css-card">', unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Save uploaded files to a temporary directory
            image_folder = save_uploaded_files(uploaded_files)
            
            # Create a temporary compress folder
            compress_folder = os.path.join(image_folder, 'compressed')
            os.makedirs(compress_folder, exist_ok=True)
            
            # Animated analysis progress
            status_text.markdown("""
            <div style="color:#4361ee;font-weight:bold;">
                <div class="loading">
                    <div></div>
                    <div></div>
                </div>
                <span class="emoji">🔄</span> Analyzing images...
            </div>
            """, unsafe_allow_html=True)
            
            # Simulate progress updates for visual feedback
            for i in range(101):
                progress_bar.progress(i)
                time.sleep(0.01)  # Short delay for smoother animation
            
            # Run your actual analysis
            results = analyze_all_images(image_folder, compress_folder)
            
            # Animated completion notification
            status_text.markdown(f"""
            <div class="success-message">
                <span class="emoji">✅</span> Analysis complete! {len(results)} images analyzed.
            </div>
            """, unsafe_allow_html=True)

            # Display Results with animation
            results_df = []
            for image, data in results.items():
                results_df.append({
                    'Image': image,
                    'Phone Usage': data['answer'].capitalize(),
                    'Explanation': data['explanation']
                })

            results_df = pd.DataFrame(results_df)
            
            # Animated results section
            results_header = st.empty()
            time.sleep(0.3)
            results_header.markdown("<h3 class='staggered-item-1'><span class='emoji'>📊</span> Analysis Results</h3>", unsafe_allow_html=True)
            
            time.sleep(0.2)
            st.dataframe(results_df, use_container_width=True)

            # Generate Visualizations with animations
            viz_header = st.empty()
            time.sleep(0.3)
            viz_header.markdown("<h3 class='staggered-item-2'><span class='emoji'>📈</span> Analysis Visualizations</h3>", unsafe_allow_html=True)
            
            # Usage Distribution
            col1, col2 = st.columns(2)
            
            with col1:
                time.sleep(0.2)
                st.markdown('<div class="css-card">', unsafe_allow_html=True)
                st.markdown("<h4><span class='emoji'>📊</span> Phone Usage Distribution</h4>", unsafe_allow_html=True)
                usage_counts = results_df['Phone Usage'].value_counts()
                
                # Custom color palette
                colors = ['#4361ee', '#3a0ca3', '#4cc9f0', '#f72585', '#7209b7']
                
                fig1, ax1 = plt.subplots(figsize=(8, 6))
                wedges, texts, autotexts = ax1.pie(
                    usage_counts.values, 
                    labels=usage_counts.index, 
                    autopct='%1.1f%%',
                    startangle=90,
                    colors=colors[:len(usage_counts)]
                )
                
                # Customize pie chart
                plt.setp(autotexts, size=10, weight="bold")
                ax1.set_title('Phone Usage Types', fontsize=14, fontweight='bold')
                
                # Equal aspect ratio ensures that pie is drawn as a circle
                ax1.axis('equal')
                st.pyplot(fig1)
                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                time.sleep(0.3)  # Slight delay for staggered appearance
                st.markdown('<div class="css-card">', unsafe_allow_html=True)
                st.markdown("<h4><span class='emoji'>📏</span> Explanation Length Distribution</h4>", unsafe_allow_html=True)
                results_df['Explanation Length'] = results_df['Explanation'].str.len()
                
                fig2, ax2 = plt.subplots(figsize=(8, 6))
                sns.histplot(results_df['Explanation Length'], bins=10, kde=True, color='#4361ee', ax=ax2)
                ax2.set_xlabel('Explanation Length (characters)', fontsize=12)
                ax2.set_ylabel('Frequency', fontsize=12)
                ax2.set_title('Distribution of Explanation Lengths', fontsize=14, fontweight='bold')
                plt.tight_layout()
                st.pyplot(fig2)
                st.markdown('</div>', unsafe_allow_html=True)

            # Save Results Button with animation
            save_button = st.empty()
            time.sleep(0.4)  # Slight delay for staggered appearance
            save_button.markdown('<div class="css-card" style="text-align: center;">', unsafe_allow_html=True)
            save_results = st.download_button(
                label="<span class='emoji'>💾</span> Save Results as JSON",
                data=results_df.to_json(orient='records', indent=4),
                file_name="image_analysis_results.json",
                mime="application/json"
            )
            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.markdown(f'<div class="error-message"><span class="emoji">❌</span> An error occurred: {str(e)}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close the analysis card

def main_app():
    main()

if __name__ == "__main__":
    main_app()
