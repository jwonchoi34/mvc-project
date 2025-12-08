import streamlit as st
from streamlit_drawable_canvas import st_canvas

st.title("Cursor Tracking on Canvas")

# Create a big canvas
canvas_result = st_canvas(
    fill_color="rgba(0,0,0,0)",  # Transparent background
    stroke_width=2,
    stroke_color="#FF0000",
    background_color="#FFFFFF",
    update_streamlit=True,
    height=600,  # big height
    width=1000,  # big width
    drawing_mode="point",  # track points
)

# Display cursor coordinates
if canvas_result.json_data is not None:
    objects = canvas_result.json_data["objects"]
    if objects:
        # Get last point added
        last_point = objects[-1]
        x = last_point["left"]
        y = last_point["top"]
        st.write(f"Cursor/Point position: x={x:.1f}, y={y:.1f}")
    else:
        st.write("Move your cursor and click to track points.")
else:
    st.write("Move your cursor and click to track points.")



