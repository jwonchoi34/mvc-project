import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
import random

st.set_page_config(layout="wide")

# ----- Session State -----
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "target_generated" not in st.session_state:
    st.session_state.target_generated = False
if "canvas_key" not in st.session_state:
    st.session_state.canvas_key = 0

if not st.session_state.submitted:
    st.title("Aim Optimizer: Setup")
    
    with st.form("settings_form"):
        dpi = st.slider("Mouse DPI", 100, 1600, 800, step=100)
        reaction_ms = st.slider("Reaction Time (ms)", 0, 500, 250, step=1)
        screen_width = st.number_input(
            "Screen Width (px)", min_value=800, max_value=8000, value=2560
        )
        screen_height = st.number_input(
            "Screen Height (px)", min_value=600, max_value=6000, value=1600
        )
        submit = st.form_submit_button("Submit")
        
        if submit:
            st.session_state.submitted = True
            st.session_state.dpi = dpi
            st.session_state.reaction = reaction_ms / 1000
            st.session_state.screen_width = screen_width
            st.session_state.screen_height = screen_height
            st.rerun()

if st.session_state.submitted:
    st.title("Aim Optimizer")
    
    # Create two columns: canvas on left, results on right
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Click to Start Training")
        
        # Canvas dimensions for display
        canvas_width = st.session_state.screen_width / 2
        canvas_width = min(canvas_width, 1600)
        canvas_height = canvas_width * 0.6
        
        # Scaling factors to convert canvas coords to screen coords
        x_scale = st.session_state.screen_width / canvas_width
        y_scale = st.session_state.screen_height / canvas_height
        
        canvas = st_canvas(
            fill_color="rgba(0,0,0,0)",
            stroke_width=2,
            stroke_color="#ff0000",
            background_color="#ffffff",
            width=canvas_width,
            height=canvas_height,
            drawing_mode="point",
            update_streamlit=True,
            key=f"canvas_{st.session_state.canvas_key}"
        )
        
        st.info("🔴 Red dot = Your cursor position")
        
        # Display cursor position if clicked
        if canvas.json_data is not None and "objects" in canvas.json_data:
            objects = canvas.json_data["objects"]
            if len(objects) > 0:
                last = objects[-1]
                x_canvas = last["left"]
                y_canvas = last["top"]
                cx_display = x_canvas * x_scale
                cy_display = y_canvas * y_scale
                
                st.write("---")
                st.write("**🔴 Cursor Position (cx, cy):**")
                st.write(f"({cx_display:.1f}, {cy_display:.1f}) px")
        
        # Display target positions if generated
        if st.session_state.target_generated:
            T_x0 = st.session_state.T_x0
            T_y0 = st.session_state.T_y0
            s_x = st.session_state.s_x
            s_y = st.session_state.s_y
            r = st.session_state.reaction
            
            # Calculate target position after reaction time
            T_x_final = T_x0 + s_x * r
            T_y_final = T_y0 + s_y * r
            
            st.write("---")
            st.write("**🔵 Target Initial Position:**")
            st.write(f"({T_x0:.1f}, {T_y0:.1f}) px")
            
            st.write("**🟢 Target Position After Reaction Time:**")
            st.write(f"({T_x_final:.1f}, {T_y_final:.1f}) px")
    
    with col2:
        st.subheader("Optimal Movement Calculation")
        
        # Check if user clicked
        if canvas.json_data is not None and "objects" in canvas.json_data:
            objects = canvas.json_data["objects"]
            if len(objects) > 0:
                # Get last click (cursor position)
                last = objects[-1]
                x_canvas = last["left"]
                y_canvas = last["top"]
                
                # Convert to screen coordinates
                cx = x_canvas * x_scale
                cy = y_canvas * y_scale
                
                # Generate random target if not already generated
                if not st.session_state.target_generated:
                    # Generate target directly in canvas coordinate space
                    T_x0 = random.uniform(200, 1800)
                    T_y0 = random.uniform(200, 1400)
                    
                    # Randomly select movement pattern (9 options)
                    movement_patterns = [
                        ("Stationary", 0, 0),
                        ("Right", random.uniform(100, 300), 0),
                        ("Left", random.uniform(-300, -100), 0),
                        ("Up", 0, random.uniform(-100, -50)),
                        ("Down", 0, random.uniform(50, 100)),
                        ("Up-Right", random.uniform(100, 300), random.uniform(-100, -50)),
                        ("Up-Left", random.uniform(-300, -100), random.uniform(-100, -50)),
                        ("Down-Right", random.uniform(100, 300), random.uniform(50, 100)),
                        ("Down-Left", random.uniform(-300, -100), random.uniform(50, 100))
                    ]
                    
                    pattern_name, s_x, s_y = random.choice(movement_patterns)
                    
                    # Store in session state
                    st.session_state.target_generated = True
                    st.session_state.T_x0 = T_x0
                    st.session_state.T_y0 = T_y0
                    st.session_state.s_x = s_x
                    st.session_state.s_y = s_y
                    st.session_state.pattern_name = pattern_name
                    st.session_state.cx = cx
                    st.session_state.cy = cy
                    st.rerun()
                
                # Check if this is a new click (different from stored position)
                elif (cx, cy) != (st.session_state.cx, st.session_state.cy):
                    # New click detected - reset and regenerate
                    st.session_state.target_generated = False
                    st.session_state.canvas_key += 1  # Increment key to clear canvas
                    st.rerun()
                
                # Use stored values
                T_x0 = st.session_state.T_x0
                T_y0 = st.session_state.T_y0
                s_x = st.session_state.s_x
                s_y = st.session_state.s_y
                pattern_name = st.session_state.pattern_name
                k = st.session_state.dpi
                r = st.session_state.reaction
                
                # Calculate target position after reaction time
                T_x_final = T_x0 + s_x * r
                T_y_final = T_y0 + s_y * r
                
                # Calculate optimal mouse movement (in inches)
                # Note: Y is flipped so positive = up, negative = down (more intuitive)
                delta_x = (T_x_final - cx) / k
                delta_y = -((T_y_final - cy) / k)  # Flip Y so positive = up
                
                # Display information
                st.write("---")
                st.write(f"**Movement Pattern:** {pattern_name}")
                st.write(f"**Target Speed:** ({s_x:.1f}, {s_y:.1f}) px/s")
                st.write(f"**Reaction Time:** {r*1000:.0f} ms")
                st.write(f"**DPI (k):** {k}")
                
                st.write("---")
                st.write("### Mathematical Model")
                
                # Display equations
                st.latex(r"E = [c_x + k\Delta x - (T_{x0} + s_x \cdot r)]^2 + [c_y + k\Delta y - (T_{y0} + s_y \cdot r)]^2")
                
                st.write("**Partial Derivatives (set to 0):**")
                st.latex(r"\frac{\partial E}{\partial \Delta x} = 2k[c_x + k\Delta x - (T_{x0} + s_x \cdot r)] = 0")
                st.latex(r"\frac{\partial E}{\partial \Delta y} = 2k[c_y + k\Delta y - (T_{y0} + s_y \cdot r)] = 0")
                
                st.write("**Optimal Movement:**")
                st.latex(r"\Delta x = \frac{T_{x0} + s_x \cdot r - c_x}{k}")
                st.latex(r"\Delta y = \frac{T_{y0} + s_y \cdot r - c_y}{k}")
                
                st.write("---")
                st.write("### Results")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Δx (inches)", f"{delta_x:.3f}\"")
                with col_b:
                    st.metric("Δy (inches)", f"{delta_y:.3f}\"")
                
                # Total distance and angle
                total_distance = np.sqrt(delta_x**2 + delta_y**2)
                
                # Calculate angle (in degrees)
                angle_rad = np.arctan2(delta_y, delta_x)
                angle_deg = np.degrees(angle_rad)
                
                col_c, col_d = st.columns(2)
                with col_c:
                    st.metric("Total Distance", f"{total_distance:.3f} inches")
                with col_d:
                    st.metric("Movement Angle", f"{angle_deg:.1f}°")
                
                # Display direction in words
                if -22.5 <= angle_deg < 22.5:
                    direction = "Right"
                elif 22.5 <= angle_deg < 67.5:
                    direction = "Up-Right"
                elif 67.5 <= angle_deg < 112.5:
                    direction = "Up"
                elif 112.5 <= angle_deg < 157.5:
                    direction = "Up-Left"
                elif angle_deg >= 157.5 or angle_deg < -157.5:
                    direction = "Left"
                elif -157.5 <= angle_deg < -112.5:
                    direction = "Down-Left"
                elif -112.5 <= angle_deg < -67.5:
                    direction = "Down"
                else:  # -67.5 <= angle_deg < -22.5
                    direction = "Down-Right"
                
                st.write(f"**Direction:** {direction}")
                st.caption(f"Move your mouse {total_distance:.3f} inches at {angle_deg:.1f}° ({direction})")
                
                st.write("---")
                with st.expander("Position Details"):
                    st.write(f"**Cursor Start (cx, cy):** ({cx:.1f}, {cy:.1f}) px")
                    st.write(f"**Target Initial (T_x0, T_y0):** ({T_x0:.1f}, {T_y0:.1f}) px")
                    st.write(f"**Target Final:** ({T_x_final:.1f}, {T_y_final:.1f}) px")
        
        else:
            st.info("👆 Click on the canvas to set your cursor position and generate a target!")
    
    # Reset settings button
    if st.button("⚙️ Reset Settings"):
        st.session_state.submitted = False
        st.session_state.target_generated = False
        st.session_state.canvas_key = 0
        st.rerun()