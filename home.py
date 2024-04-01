import streamlit as st

def main():
    _, col1, _ = st.columns(3)
    with col1:
        st.image("images/logo.png")
    
    st.markdown("<h2 style='text-align: center;'>The Third Eye</h2>", unsafe_allow_html=True)
    st.markdown('''
        Welcome to "**The Third Eye**", a free online tool that aims to offer various computer vision services.
                
        Currently though, there is only one functionality, **object detection**. Using our tool, you can detect objects from 
        videos and photos in real time or asynchronously. Click the sidebar to see them in action and have fun!
    ''')
    
    tab1, tab2, tab3 = st.tabs(["Functionality", "Implementation", "Learning"])
    with tab1:
        st.write("""
            Given a frame of video or a photo, our object detection model will detect 80 different classes if any. It means that the model will
            draw a bounding box on a particular detected object and identify its class, specifying its confidence. 
        """)
        with st.expander("What kind of objects does it detect?"):
            st.write("""
                Well, a lot!
                person, bicycle, car, motorbike, aeroplane, bus, train, truck, boat, traffic light, 
                fire hydrant, stop sign, parking meter, bench, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack, umbrella, handbag, 
                tie, suitcase, frisbee, skis, snowboard, sports ball, kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket, bottle, wine glass, 
                cup, fork, knife, spoon, bowl ,banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake, chair, sofa, potted plant, bed, diningtable, 
                toilet, tvmonitor, laptop, mouse, remote, keyboard, cell phone, microwave, oven, toaster, sink, refrigerator, book, clock, vase, scissors, teddy bear, hair drier, toothbrush
            """)
        st.write("Don't worry about the output image teeming with bounding boxes. No matter how many objects the model should detect in a frame or a photo, it will detect only 10 objects.")
    with tab2:
        st.markdown("""
            ### YOLO
            The model behind our tool is trained using [YOLO "You Only Look Once"](https://arxiv.org/abs/1506.02640) algorithm, a state-of-the-art algorithm, which achieves high accuracy while also being able to run in real time. 
            This algorithm "only looks once" at the image in the sense that it requires only one forward propagation pass through the network to make predictions. 
            
            Training a YOLO model takes a very long time and requires a fairly large dataset of labelled bounding boxes for a large range of target classes. Hence, we use an existing pre-trained Keras YOLO model, whose weights come 
            from the [official YOLO website](https://pjreddie.com/darknet/yolo/). 
            > Note that it is YOLOv2 that is used for our tool, and to put it into perspective, YOLOv7 has been available since July 2022, which is the latest cutting-edge object detector in the YOLO family. 
            With that said, you can observe that our model, despite being relatively old, still performs outstandingly. 

            ### WebRTC
            For the capturing and displaying of video frames in real time, we use [`streamlit_webrtc`](https://dev.to/whitphx/developing-web-based-real-time-videoaudio-processing-apps-quickly-with-streamlit-4k89). 
            WebRTC, itself, is an open framework for the web that enables Real-Time Communications (RTC) capabilities in the browser. 
            
            `streamlit_webrtc` uses WebRTC for its video and audio streaming. It has to access a “STUN server” in the global network for the remote peers (precisely, peers over the NATs) to establish WebRTC connections.
            However, even if the STUN server is properly configured, media streaming may not work in some network environments, either from the server or from the client. For example, if the server is hosted behind a proxy, 
            or if the client is on an office network behind a firewall, the WebRTC packets may be blocked (Streamlit Community Cloud is the case). In such environments, [TURN server](https://webrtc.org/getting-started/turn-server) is required.
            For setting up this server, we use [Twilio Network Traversal Service](https://www.twilio.com/docs/stun-turn).
        """)
    with tab3:
        st.markdown("""
            Here are powerful resources from which you can learn theoretical and pratical know-how to be able to build an objection detection tool like this by yourself.
            - [My Note for Detection Algorithms](https://www.notion.so/yethu/Detection-Algorithms-e82e4152c9004123bfc03cffce573aca?pvs=4)
            - [You Only Look Once: Unified, Real-Time Object Detection](https://arxiv.org/abs/1506.02640) (2015)
            - [Developing Web-based Real-time Video/Audio Processing Apps Quickly with Streamlit](https://dev.to/whitphx/developing-web-based-real-time-videoaudio-processing-apps-quickly-with-streamlit-4k89)
        """)

    col2, col3 = st.columns(2)
    with col2:
        st.subheader("📽️ Video Object Detection")
    with col3:
        st.subheader("📸 Photo Object Detection")

if __name__=="__main__":
    st.set_page_config(page_title="Third Eye",page_icon='images/logo.png')
    main()

