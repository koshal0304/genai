import streamlit as st
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import seaborn as sns
from objectdetection import analyze_all_images

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
    st.set_page_config(page_title="Phone Usage Analyzer", layout="wide")
    
    # Title and description
    st.title("🖼️ Image Usage Analyzer")
    st.markdown("Analyze your images and understand their context.")

    # File Upload
    st.subheader("Upload Images")
    uploaded_files = select_folder()

    # Preview Images
    if uploaded_files:
        # Display preview images
        preview_cols = st.columns(4)
        for i, uploaded_file in enumerate(uploaded_files[:4]):
            try:
                img = Image.open(uploaded_file)
                preview_cols[i].image(img, caption=uploaded_file.name, use_container_width=True)
            except Exception as e:
                st.error(f"Error loading preview image {uploaded_file.name}: {e}")

    # Analyze Button
    analyze_button = st.button("Analyze Images")

    # Analysis Logic
    if analyze_button:
        # Validate file upload
        if not uploaded_files:
            st.error("Please upload images")
            return

        # Progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Save uploaded files to a temporary directory
            image_folder = save_uploaded_files(uploaded_files)
            
            # Create a temporary compress folder
            compress_folder = os.path.join(image_folder, 'compressed')
            os.makedirs(compress_folder, exist_ok=True)
            
            # Run analysis
            status_text.info("Analyzing images...")
            results = analyze_all_images(image_folder, compress_folder)
            
            # Update progress
            progress_bar.progress(100)
            status_text.success(f"Analysis complete. {len(results)} images analyzed.")

            # Display Results
            results_df = []
            for image, data in results.items():
                results_df.append({
                    'Image': image,
                    'Phone Usage': data['answer'].capitalize(),
                    'Explanation': data['explanation']
                })

            results_df = pd.DataFrame(results_df)
            st.dataframe(results_df)

            # Generate Visualizations
            st.subheader("Analysis Visualizations")
            
            # Usage Distribution
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("Phone Usage Distribution")
                usage_counts = results_df['Phone Usage'].value_counts()
                fig1, ax1 = plt.subplots()
                ax1.pie(usage_counts.values, labels=usage_counts.index, autopct='%1.1f%%')
                st.pyplot(fig1)

            with col2:
                st.write("Explanation Length Distribution")
                results_df['Explanation Length'] = results_df['Explanation'].str.len()
                fig2, ax2 = plt.subplots()
                ax2.hist(results_df['Explanation Length'], bins=10)
                ax2.set_xlabel('Explanation Length')
                ax2.set_ylabel('Frequency')
                st.pyplot(fig2)

            # Save Results Button
            save_results = st.download_button(
                label="Save Results as JSON",
                data=results_df.to_json(orient='records', indent=4),
                file_name="image_analysis_results.json",
                mime="application/json"
            )

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

def main_app():
    main()

if __name__ == "__main__":
    main_app()
