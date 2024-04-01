import streamlit as st
import av

from twilio.rest import Client
from streamlit_webrtc import webrtc_streamer, VideoHTMLAttributes
from detect import predict

def callback(frame):
    img = frame.to_ndarray(format="bgr24")
    predicted_image = predict(img)

    # img = cv2.cvtColor(cv2.Canny(img, 100, 200), cv2.COLOR_GRAY2BGR)
    return av.VideoFrame.from_ndarray(predicted_image, format="bgr24")


def main():
    with st.spinner('Setting up camera...'):
        st.subheader("Detection in Video")
        st.info('FPS can be fairly low, which necessitates further optimization of the program :)', icon="ℹ️")
        
        account_sid = st.secrets['ACCOUNT_SID']
        auth_token = st.secrets['AUTH_TOKEN']

        client = Client(account_sid, auth_token)

        token = client.tokens.create()

        ## Currently rerunning again and again after streamlit update
        webrtc_streamer(key="example", 
                        video_frame_callback=callback,
                        rtc_configuration={
                            "iceServers": token.ice_servers
                        },
                        video_html_attrs=VideoHTMLAttributes(
                            autoPlay=True, controls=True, style={"width": "100%"}, muted=True
                        ))

if __name__=="__main__":
    main()
### Implementation with pure openCV (only works in local) ###

# from detect import open_webcam

# def main():
#     st.subheader("Detection in Real Time")
#     if st.button("Start video"):
#         open_webcam()

# if __name__=="__main__":
#     main()