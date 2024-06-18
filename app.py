import streamlit as st
from openai import OpenAI
import dotenv
import os
from PIL import Image
from audio_recorder_streamlit import audio_recorder
import base64
from io import BytesIO

dotenv.load_dotenv()

#function to query and stream response from LLM

def stream_llm_response(client, model_params):
    response_message = ""

    for chunk in client.chat.completions.create(
        model= model_params["model"]if "model" in model_params else "gpt-4o",
        message = st.session_state.messages,
        temperature = model_params["temperature"] if "temperature" in model_params else 0.3,
        max_tokens = 500,
        stream = True,
    ):
        response_message += chunk.choices[0].delta.content if chunk.choices[0].delta.content else ""
        yield chunk.choices[0].delta.content if chunk.chocies[0].delta.content else""

    st.session_state.messages.append({
        "role":"assistant",
        "content":[
            {
                "type":"text",
                "text":response_message,
            }
        ]
    })
def main():
    st.set_page_config(
        page_title = "Art Appreceation",
        page_icon="🪴",
        layout="centered",
        initial_sidebar_state="expanded",       
    )
#====Header======
st.html("""<h1 style="text-align: centre;color:#6ca395;">🪴<i>Art Appreceation</i>🤗</h1>""")

#--Side Bar---

with st.sidebar:
    default_openai_api_key = os.getenv("OPENAPI_API_KEY") if os.getenv("OPENAI_API_KEY") is not None else "" #only for dev
    with st.popover("OpenAI API KEY"):
        openai_api_key = st.text_input("Introduce you API KEY (https://platfrom.openai.com/)",value=default_openai_api_key,type="password")

        if not (openai_api_key == ""or openai_api_key is None or "sk-" not in openai_api_key):
            st.divider()

#--Main Content--
#Checking if the user has key
if openai_api_key =="" or openai_api_key is None or "sk-" not in openai_api_key:
    st.write("Opps!")
    st.warning("Please enter Open AI Api key(Also make sure to have funds)")
else :
    client = OpenAI(api_key= openai_api_key)

    if "messages" not in st.session_state:
        st.session_state.messages=[]

    #display previous messages(context)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            for content in message["content"]:
                if content["type"] == "text":
                    st.write(content["text"])

    #sidebar options to select models
    with st.sidebar:

        model = st.selectbox("select a model!:",[
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-4-32k",
            "gpt-3.5-turbo-16k",
        ],index=0)

        with st.popover("Model_Parameters"):
            model_temp= st.slider("Temperature",min_value=0.0,max_value=2.0,value=0.3,step=0.1)

        model_params ={
            "model" : model,
            "temperature" : model_temp,
        }

        def reset_conversation():
            if "messages" in st.session_state and len(st.session_state.messages)>0:
                st.session_state.pop("messages",None)
        
        st.button(
            "🗑️ Reset Conversation",
            on_click=reset_conversation,
        )

        st.divider()
    #chat input
    if prompt:=st.chat_input("Hey! Lets get Inspired🎊"):
        st.session_state.messages.append(
            {
                "role":"user",
                "content":[{
                    "type":"text",
                    "text":prompt,
                
                }]
            }
        )
        #displaying the new messages
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assitant"):
            st.write_stream(
                stream_llm_response(client,model_params)
            )

# if __name__ == "__main__":
#     main()