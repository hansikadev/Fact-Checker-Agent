import streamlit as st
import time
import pandas as pd
import plotly.express as px
import os
import sys

# Add root directory to sys path if running locally
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from frontend.utils.api import upload_document, get_status, get_report
st.set_page_config(page_title="Fact-Check Agent", page_icon="🕵️", layout="wide")

st.title("🕵️ Fact-Check Agent Web App")
st.markdown("Automatically extract and verify claims from your documents using AI and live web search. Specifically designed to handle **Trap Documents** with outdated statistics or fabricated claims.")

uploaded_file = st.file_uploader("Upload a PDF Document (e.g., Research Report, Pitch Deck)", type="pdf")

if uploaded_file is not None:
    if st.button("Start Verification"):
        with st.spinner("Uploading and starting extraction..."):
            try:
                res = upload_document(uploaded_file.getvalue(), uploaded_file.name)
                job_id = res['job_id']
                st.session_state['job_id'] = job_id
                st.session_state['completed'] = False
                st.success("Document uploaded successfully!")
            except Exception as e:
                st.error(f"Error uploading document: {e}")
                st.stop()

if 'job_id' in st.session_state:
    job_id = st.session_state['job_id']
    
    if not st.session_state.get('completed', False):
        # Status Polling
        status_placeholder = st.empty()
        progress_bar = st.progress(0)
        
        is_completed = False
        while not is_completed:
            try:
                status_data = get_status(job_id)
                current_status = status_data['status']
                progress_str = status_data['progress']
                
                status_placeholder.info(f"Status: **{current_status}** | Progress: {progress_str}")
                
                if current_status == "COMPLETED":
                    is_completed = True
                    st.session_state['completed'] = True
                    progress_bar.progress(100)
                elif current_status == "FAILED":
                    status_placeholder.error("Verification failed.")
                    st.stop()
                else:
                    time.sleep(3)
            except Exception as e:
                status_placeholder.warning(f"Waiting for server response... {e}")
                time.sleep(3)
    
    # Report generation
    if st.session_state.get('completed', False):
        st.success("Verification Complete!")
        report_data = get_report(job_id)
        
        # Dashboard metrics
        st.header("📊 Final Report Dashboard")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Claims", report_data['total_claims'])
        col2.metric("✅ Verified", report_data['verified_count'])
        col3.metric("⚠️ Inaccurate", report_data['inaccurate_count'])
        col4.metric("❌ False", report_data['false_count'])
        
        # Donut Chart
        if report_data['total_claims'] > 0:
            df_status = pd.DataFrame({
                'Status': ['Verified', 'Inaccurate', 'False'],
                'Count': [report_data['verified_count'], report_data['inaccurate_count'], report_data['false_count']]
            })
            fig = px.pie(df_status, values='Count', names='Status', hole=0.5, 
                         color='Status', color_discrete_map={'Verified':'green', 'Inaccurate':'orange', 'False':'red'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Claims Table
            st.subheader("Extracted Claims & Evidence")
            
            for claim in report_data['claims']:
                orig = claim['original_claim']
                status_color = "🟢" if claim['status'] == "VERIFIED" else "🟠" if claim['status'] == "INACCURATE" else "🔴"
                
                with st.expander(f"{status_color} {orig['claim_text']} [{claim['status']}]"):
                    st.markdown(f"**Type:** {orig['claim_type']} | **Entities:** {', '.join(orig['entities'])} | **Year:** {orig['year'] or 'N/A'}")
                    st.markdown(f"**Confidence Score:** {claim['confidence_score']}")
                    if claim['correct_value']:
                        st.markdown(f"**Correct Value:** `{claim['correct_value']}`")
                    st.markdown(f"**Explanation:** {claim['explanation']}")
                    
                    if claim['evidence_sources']:
                        st.markdown("### Evidence Sources")
                        for ev in claim['evidence_sources']:
                            st.markdown(f"- [{ev['source_title']}]({ev['source_url']}) (Score: {ev['credibility_score']})")
                            st.caption(f'"{ev["content_snippet"]}"')
