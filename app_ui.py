uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"], label_visibility="collapsed")
    
    if uploaded_file:
        btn_c1, btn_c2, btn_c3 = st.columns([1.2, 1, 1.2])
        with btn_c2:
            st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
            if st.button("🚀 Process & Build Embeddings", use_container_width=True):
                # Seek to start and read bytes directly (No empty file error)
                uploaded_file.seek(0)
                file_bytes = uploaded_file.read()
                
                if len(file_bytes) == 0:
                    st.error("Uploaded file is empty. Please select a valid PDF.")
                else:
                    parsed_data = parse_resume(file_bytes)
                    store_candidate_profile(parsed_data)
                    st.success("✅ Resume parsed and candidate embeddings initialized successfully!")
                    st.rerun()
