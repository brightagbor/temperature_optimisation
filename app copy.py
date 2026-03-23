import streamlit as st
import numpy as np
import pickle
from pyswarm import pso

# ---------------------------
# Load model and scaler
# ---------------------------
model = pickle.load(open("results/catboost_best_model.pkl", "rb"))
scaler = pickle.load(open("results/scaler.pkl", "rb"))

st.title("Smart Building Cooling Load Optimizer")

# ---------------------------
# User Inputs
# ---------------------------
st.subheader("Enter Building Features")

X1 = st.number_input("Relative Compactness (X1)", 0.62, 0.98, 0.75)
X2 = st.number_input("Surface Area (X2)", 514.5, 808.5, 672.0)
X3 = st.number_input("Wall Area (X3)", 245.0, 416.5, 318.5)
X4 = st.number_input("Roof Area (X4)", 110.25, 220.5, 183.75)
X5 = st.number_input("Overall Height (X5)", 3.5, 7.0, 5.25)
X6 = st.selectbox("Orientation (X6)", [2, 3, 4, 5])
X7 = st.number_input("Glazing Area (X7)", 0.0, 0.4, 0.25)
X8 = st.selectbox("Glazing Distribution (X8)", [0,1,2,3,4,5])

user_input = np.array([[X1,X2,X3,X4,X5,X6,X7,X8]])

# ---------------------------
# Scale Input
# ---------------------------
user_input_scaled = scaler.transform(user_input)

# ---------------------------
# Predict Cooling Load
# ---------------------------
if st.button("Predict Cooling Load"):
    pred = model.predict(user_input_scaled)[0]
    st.success(f"Predicted Cooling Load (Y2): {pred:.4f}")

# ---------------------------
# Real-time Optimization with Constraints
# ---------------------------
st.subheader("Optional: Run Real-time Optimization")
st.markdown("""
Adjust constraints for each feature to search for a custom optimal design.
""")

# Sliders for optimization bounds
X1_min, X1_max = st.slider("Relative Compactness (X1)", 0.62, 0.98, (0.62, 0.98))
X2_min, X2_max = st.slider("Surface Area (X2)", 514.5, 808.5, (514.5, 808.5))
X3_min, X3_max = st.slider("Wall Area (X3)", 245.0, 416.5, (245.0, 416.5))
X4_min, X4_max = st.slider("Roof Area (X4)", 110.25, 220.5, (110.25, 220.5))
X5_min, X5_max = st.slider("Overall Height (X5)", 3.5, 7.0, (3.5, 7.0))
X6_min, X6_max = st.slider("Orientation (X6)", 2, 5, (2,5))
X7_min, X7_max = st.slider("Glazing Area (X7)", 0.0, 0.4, (0.0, 0.4))
X8_min, X8_max = st.slider("Glazing Distribution (X8)", 0, 5, (0,5))

def objective(x):
    x = np.array(x).reshape(1, -1)
    return model.predict(x)[0]  # minimize Y2

if st.button("Run Optimization"):
    # Scale bounds
    lb_scaled = scaler.transform(np.array([[X1_min,X2_min,X3_min,X4_min,X5_min,X6_min,X7_min,X8_min]]))[0]
    ub_scaled = scaler.transform(np.array([[X1_max,X2_max,X3_max,X4_max,X5_max,X6_max,X7_max,X8_max]]))[0]

    # PSO
    best_x_scaled, best_y = pso(objective, lb_scaled, ub_scaled, swarmsize=30, maxiter=50)

    # Convert back to original units
    best_x_actual = scaler.inverse_transform(best_x_scaled.reshape(1, -1))[0]
    
    # Round integer features
    best_x_actual[5] = round(best_x_actual[5])
    best_x_actual[7] = round(best_x_actual[7])

    # Display results
    st.subheader("Custom Optimal Design")
    feature_names = ["X1","X2","X3","X4","X5","X6","X7","X8"]
    for name, value in zip(feature_names, best_x_actual):
        st.write(f"{name}: {value:.4f}")
    st.write(f"Minimum Cooling Load (Y2): {best_y:.4f}")
