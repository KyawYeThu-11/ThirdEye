import streamlit as st
import numpy as np
from detect import predict
from PIL import Image

def detect_objects(image_file):
    img = Image.open(image_file)
    img_array = np.array(img)
    predicted_image = predict(img_array)

    return predicted_image

def main():
    st.subheader("Detection in Photo")
    tab1, tab2 = st.tabs(["Upload picture", "Take picture"])

    with tab1:
        uploaded_file = st.file_uploader("Choose an image file.", type=['jpg', 'png'])
        if uploaded_file is not None:
            st.image(detect_objects(uploaded_file))
        
        st.write("You can also see the detection in action with our sample images. Click to download.")
        col1, col2, col3 = st.columns(3)
        with col1:
            with open("images/test1.jpg", "rb") as file:
                st.download_button(
                        label="Sample Image 1",
                        data=file,
                        file_name="traffic.jpg",
                        mime="image/jpg"
                    )
        with col2:
            with open("images/test2.jpg", "rb") as file:
                st.download_button(
                        label="Sample Image 2",
                        data=file,
                        file_name="desk.jpg",
                        mime="image/jpg"
                    )
        with col3:
            with open("images/test3.jpg", "rb") as file:
                st.download_button(
                        label="Sample Image 3",
                        data=file,
                        file_name="giraffe&zebra.jpg",
                        mime="image/jpg"
                    )

    with tab2:
        picture = st.camera_input("Take a photo to detect objects within it.")
        if picture:
            st.image(detect_objects(picture))

if __name__=="__main__":
    main()