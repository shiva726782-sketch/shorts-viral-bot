import streamlit as st
from pinecone import Pinecone
import google.generativeai as genai
import os

# सर्वर से AI की चाबियां लोड करना
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
PINECONE_KEY = os.environ.get("PINECONE_API_KEY", "")

# AI मॉडल्स को सेट करना
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
if PINECONE_KEY:
    pc = Pinecone(api_key=PINECONE_KEY)

# ऐप की डिज़ाइन
st.set_page_config(page_title="Shorts Viral AI", page_icon="🚀", layout="centered")

# मुख्य स्क्रीन (ChatGPT जैसा ढांचा)
st.title("🚀 Shorts Viral AI Expert Bot")
st.write("शॉर्ट्स वीडियो वायरल करने का करोड़ों का डेटा अब एक क्लिक पर!")

# साइडबार - जहाँ से आप नया डेटा अपलोड करेंगे
with st.sidebar:
    st.header("📂 AI डेटा अपलोड पैनल")
    st.write("नया वायरल डेटा या टिप्स यहाँ डालें:")
    
    new_tips = st.text_area("नया डेटा यहाँ टाइप या पेस्ट करें:", height=150)
    
    if st.button("डेटा अपलोड करें"):
        if new_tips.strip():
            if PINECONE_KEY:
                try:
                    assistant = pc.assistant.Assistant(name="shorts-assistant")
                    assistant.upload_text(text=new_tips.strip())
                    st.success("✅ डेटा सफलतापूर्वक करोड़ों के डेटाबेस में जुड़ गया!")
                except Exception as e:
                    st.error("डेटाबेस में अपलोड फेल हुआ।")
            else:
                st.error("Pinecone API Key सेटअप नहीं है।")
        else:
            st.error("कृपया पहले कुछ डेटा टाइप करें।")

# चैटिंग सिस्टम का ढांचा (Chat History)
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# यूज़र का नया सवाल (चैट इनपुट बॉक्स)
if user_input := st.chat_input("शॉर्ट्स वायरल कैसे करें? अपना सवाल पूछें..."):
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    ai_reply = ""
    if GEMINI_KEY and PINECONE_KEY:
        try:
            # 1. Pinecone से जानकारी खोजना
            assistant = pc.assistant.Assistant(name="shorts-assistant")
            search_context = assistant.chat(messages=[{"role": "user", "content": user_input}])
            data_context = search_context.choices.message.content
            
            # 2. गूगल AI से फाइनल जवाब बनवाना
            prompt = f"""
            तुम शॉर्ट्स वीडियो वायरल करने के महा-एक्सपर्ट AI हो। तुम्हें सिर्फ नीचे दिए गए डेटाबेस के आधार पर यूज़र के सवाल का पॉइंट-टू-पॉइंट और बेहतरीन जवाब देना है। 
            अगर जवाब डेटाबेस में नहीं है, तो सीधे बोलो कि इसकी जानकारी उपलब्ध नहीं है।

            डेटाबेस जानकारी:
            {data_context}

            यूज़र का सवाल: {user_input}
            सटीक जवाब (हिंदी में सुंदर पॉइंट्स बनाकर):
            """
            
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            ai_reply = response.text
        except Exception as e:
            ai_reply = "माफ़ कीजिये, डेटाबेस से कनेक्ट करने में कुछ समस्या आ रही है।"
    else:
        ai_reply = "App backend setup is incomplete. Please add API Keys."

    with st.chat_message("assistant"):
        st.write(ai_reply)
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
