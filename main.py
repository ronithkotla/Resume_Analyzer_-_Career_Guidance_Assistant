from groq import Groq
import streamlit as st
from pdfminer.high_level import extract_text
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
import requests
API_KEY="AIzaSyAY_vxL36U2L0qKSsvlMTEykeAEYqpQXDY"
SEARCH_ENGINE_ID="2475e772c459942ea"

if "start_page_completed" not in st.session_state:
    st.session_state.start_page_completed=False

if "resume_analyzer" not in st.session_state:
    st.session_state.resume_analyzer=False

if "career_guidance" not in st.session_state:
    st.session_state.career_guidance=False

if "career_submission_form" not in st.session_state:
    st.session_state.career_submission_form=False

if "resume_submission_form" not in st.session_state:
    st.session_state.resume_submission_form=False

if "resume" not in st.session_state:
    st.session_state.resume=""

if "job_desc" not in st.session_state:
    st.session_state.job_desc=""

if "messages" not in st.session_state:
    st.session_state.messages=[]

if "last_page" not in st.session_state:
    st.session_state.last_page=False

if "internet_on" not in st.session_state:
    st.session_state.internet_on=False

if "links" not in st.session_state:
    st.session_state.links=""

# Function to extract text from PDF
def extract_pdf_text(uploaded_file):
    try:
        extracted_text = extract_text(uploaded_file)
        return extracted_text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return "Could not extract text from the PDF file."

def display_messages():
    chat_container = st.container()

    with chat_container:
        for msg in st.session_state.messages:
            if msg['role'] == 'user':
                st.markdown(f"""
                <div style='
                    display: flex; 
                    justify-content: flex-end; 
                    margin-bottom: 15px;
                    width: 100%;
                '>
                    <div style='
                        background-color: #414A4C; 
                        color: white;
                        border-radius: 15px;
                        padding: 12px 15px;
                        max-width: 80%;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                        border-bottom-right-radius: 5px;
                    '>
                        <div style='
                            font-weight: 600; 
                            margin-bottom: 5px; 
                            color: #A0A0A0;
                            font-size: 0.8em;
                        '>You</div>
                        {msg['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            elif msg['role'] == 'assistant':
                st.markdown(f"""
                <div style='
                    display: flex; 
                    justify-content: flex-start; 
                    margin-bottom: 15px;
                    width: 100%;
                '>
                    <div style='
                        background-color: #000000; 
                        color: white;
                        border-radius: 15px;
                        padding: 12px 15px;
                        max-width: 80%;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                        border-bottom-left-radius: 5px;
                    '>
                        <div style='
                            font-weight: 600; 
                            margin-bottom: 5px; 
                            color: #A0A0A0;
                            font-size: 0.8em;
                        '>Career Guidance Assistant</div>
                        {msg['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
        st.session_state.internet_on=st.toggle("Search Internet")


def get_bot_response():
    client = Groq(
    api_key="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",
    )
    
    st.session_state.messages[0]["content"] += st.session_state.links


    chat_completion = client.chat.completions.create(
        messages=st.session_state.messages,
        model="llama-3.3-70b-versatile",
    )
    bot_response=chat_completion.choices[0].message.content
    
    if bot_response:
        # Add user message to chat history
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
    st.session_state.links=""
    # Call the function to render messages
    display_messages()


def initialize_prompt():
    prompt=f"""
    # Context :
    - You are a Career Guidance Assistant, who help candidates with any doubts regarding there career and Studies only, Provide Suggestions and clear there doubts.
    - You will be given Candidate's resume, Job description, Provide Guidance based on these.

    # Instruction:

    - Donot provide guidance until the candidate ask for it.
    - Stick to your context donot provide answers related to queries that donot concern to your context, Kindly reject them.
    - Provide guidance, suggestions,advice keeping in mind the resume and job description on which feilds he can improve and how.
    - Always provide a simple and easy to understand responses.
    - If you have any links and titles from Internet output those links along with description of whats in it, if the user is asking for that information only.
    - Strictly Reject any queries that are not related to career or studies, Even if you have the information and links reject the query.
    # Inputs:
    - Candidate's resume : {st.session_state.resume}
    ---
    - Job Description : {st.session_state.job_desc}

    """
    st.session_state.messages.append({"role": "system", "content": prompt})

    

# Career guidance page
def career_guidance():
    st.title("Career Guidance Assistant🎯")
    st.write(" Ask your doubts and improve your career growth. ")
    if user_input := st.chat_input("Enter your answer or Type 'exit' to end the interview"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})

        if st.session_state.internet_on:
            search_query=user_input
            url="https://www.googleapis.com/customsearch/v1"

            params={
                'q': search_query,
                'key': API_KEY,
                'cx': SEARCH_ENGINE_ID,
                'gl': "in",
                'hl': "en",
                'num': 5,
                'cr':'countryIN',
                'sort':"date",  

            }

            response=requests.get(url,params=params)
            results=response.json()

            # Normal Search Results
            if 'items' in results:
                st.session_state.links+="Use these Information taken from Internet to respond any related query the user asks."
                for i in results['items']:
                    if all(key in i for key in ["title", "snippet", "link"]):
                        st.session_state.links=f"{st.session_state.links} , Title of webpage:{i["title"]}, Link :{i["link"]}, Short Snippet:{i["snippet"]}"
            

            
        if user_input=="exit":
            st.session_state.start_page_completed=False
            st.session_state.last_page=False

            st.session_state.resume_analyzer=False

            st.session_state.career_guidance=False

            st.session_state.career_submission_form=False

            st.session_state.resume=""

            st.session_state.job_desc=""

            st.session_state.messages=[]

            st.session_state.resume_submission_form=False

            st.session_state.internet_on=False

            st.session_state.links=""
            st.rerun()


    get_bot_response()
    

# Function to calculate similarity with SBERT
def calculate_similarity_bert(text1, text2):
    ats_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    # Encode the texts directly to embeddings
    embeddings1 = ats_model.encode([text1])
    embeddings2 = ats_model.encode([text2])
    
    # Calculate cosine similarity without adding an extra list layer
    similarity = cosine_similarity(embeddings1, embeddings2)[0][0]
    return similarity

def get_report(resume,job_desc):
    client = Groq(
    api_key="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",
    )
    report_prompt=f"""
    # Context:
    - You are a AI Report generator, you will be given Candidate's resume, Job Description.

    # Instruction:
    - Analyze candidate's resume based on the possible points that can be extracted from job description,and give your evaluation on each point with the criteria below:  
    - Consider all points like required skills, experience, etc that are needed for the job role.
    - Each point should be given a score (example: 3/5).  
    - Calculate the score to be given (out of 5) for every pattern based on evaluation at the beginning of each point with an explanation.  
    - Always provide a clear, consistent rationale for your assessment.  
    - If the resume aligns with the job description point, mark it with ✅ and provide a detailed explanation.  
    - If the resume doesn't align with the job description point, mark it with ❌ and provide a reason.  
    - If a clear conclusion cannot be made, use a ⚠️ sign with a reason.  

    # Inputs:
    Candidate Resume: {resume}
    ---
    Job Description: {job_desc}

    # Output:
    - Report with scores and emoji at the beginning of each point and then explanation.
    """
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": report_prompt}],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

def extract_scores(text):
    # Regular expression pattern to find scores in the format x/5, where x can be an integer or a float
    pattern = r'(\d+(?:\.\d+)?)/5'
    # Find all matches in the text
    matches = re.findall(pattern, text)
    # Convert matches to floats
    scores = [float(match) for match in matches]
    return scores
# Starting Page 
if not st.session_state.start_page_completed:
    st.title("📈 Resume Analyzer and Career Guidance Assistant")

    st.subheader("Select the option you want:")
    st.write("")
    col1,col2=st.columns(2)
    with col1:
        st.write("Generate scores and reports using AI")

        if st.button("📝 Resume Analyzer"):
            st.session_state.resume_analyzer=True
            st.session_state.start_page_completed=True
            st.rerun()
    with col2:
        st.write("Need help regarding your career?")

        if st.button("🎯Career Guidance"):
            st.session_state.career_guidance=True
            st.session_state.start_page_completed=True
            st.rerun()

if st.session_state.start_page_completed and st.session_state.career_guidance:
    if not st.session_state.career_submission_form:
        with st.form("career guidance submission"):
            try:
                uploaded_file=st.file_uploader("Upload your resume",type="pdf")
            except:
                st.info("Error uploading")
            st.write("Job descrition:")
            job_desc=st.text_area("Enter your job description here...")

            submitted=st.form_submit_button("Submit")
            if submitted:
                if uploaded_file is not None:
                    with st.spinner("Processing PDF..."):
                        st.session_state.resume = extract_pdf_text(uploaded_file)
                st.session_state.job_desc=job_desc
                st.session_state.career_submission_form=True
                st.session_state.last_page=True
                initialize_prompt()
                st.rerun()

            not_submitted=st.form_submit_button("Proceed without uploading")
            if not_submitted:
                st.session_state.resume="Proceed without Resume"
                st.session_state.job_desc="Proceed without job description"
                st.session_state.career_submission_form=True
                st.session_state.last_page=True
                initialize_prompt()

                st.rerun()
            

        
if st.session_state.start_page_completed and st.session_state.resume_analyzer:
    if not st.session_state.resume_submission_form:
        with st.form("resume analyzer submission"):
            try:
                uploaded_file=st.file_uploader("Upload your resume",type="pdf")
            except:
                st.info("Error uploading")
            st.write("Job descrition:")
            job_desc=st.text_area("Enter your job description here...")

            submitted=st.form_submit_button("Submit")
            if submitted:
                if (uploaded_file is not None) and job_desc != "":
                    with st.spinner("Processing PDF..."):
                        st.session_state.resume = extract_pdf_text(uploaded_file)
                    st.session_state.job_desc=job_desc
                    st.session_state.resume_submission_form=True
                    st.rerun()
    if st.session_state.resume_submission_form:
        st.title("Resume Analyzer")
        score_place=st.info("Generating Scores...")
        ats_score=calculate_similarity_bert(st.session_state.resume,st.session_state.job_desc)

        col3,col4=st.columns(2,border=True)
        with col3:
            st.write("Few ATS uses this score to shortlist candidates, Similarity Score:")
            st.subheader(str(ats_score))
        report=get_report(st.session_state.resume,st.session_state.job_desc)
        report_scores=extract_scores(report)
        avg_score=sum(report_scores)/(5*len(report_scores))
        with col4:
            st.write("Total Average score according to our AI report:")
            st.subheader(str(avg_score))
        score_place.success("Scores generated successfully!")

        st.subheader("AI Generated Report:")
        st.markdown(f"""
                <div style='text-align: left; background-color: #000000; padding: 10px; border-radius: 10px; margin: 5px 0;'>
                 {report}
                </div>
                """, unsafe_allow_html=True)
        col5,col6=st.columns(2)
        with col5:
            st.write("Download your report here:")
        with col6:
            st.download_button(
                label="Download Report",
                data=report,
                file_name="report.txt",
                icon=":material/download:",
                )
        st.write(" ")
        st.write(" ")
        col7,col8=st.columns(2)
        with col7:
            st.write("Need assistance regarding career growth ?")
        with col8:
            if st.button("Career Guidance Assistant"):
                st.session_state.last_page=True
                prompt=f"""
                # Context :
                - You are a Career Guidance Assistant, who help candidates with any doubts regarding there career only, Provide Suggestions and clear there doubts.
                - You will be given Candidate's resume, JOb description, Ai generated report, and scores. Provide Guidance based on these.

                # Instruction:

                - Donot provide guidance until the candidate ask for it.
                - Stick to your context donot provide answers related to queries that donot concern to your context, Kindly reject them.
                - Provide guidance, suggestions,advice keeping in mind the resume and job description on which feilds he can improve and how.
                - Always provide a simple and easy to understand responses.
                - If you have any links and titles from Internet output those links along with description of whats in it, if the user is asking for that information only.

                - Strictly reject any queries that are not related to career or studies.Even if you have the information and links reject the query.

                # Inputs:
                - Candidate's resume : {st.session_state.resume}
                ---
                - Job Description : {st.session_state.job_desc}
                ---
                - AI generated Report: {report}
                ---
                - Cosine Similairty score: {ats_score}
                ---
                - Total Average score according to AI generated report: {avg_score} 
                """
                st.session_state.messages.append({"role": "system", "content": prompt})
                st.rerun()
if st.session_state.last_page:
    
    career_guidance()








