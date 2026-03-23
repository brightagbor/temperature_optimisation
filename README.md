
# Smart Building Cooling Load Optimiser

An **interactive Streamlit application** for predicting and optimizing the cooling load of buildings based on key architectural and environmental features. The app leverages a **CatBoost regression model** and **Particle Swarm Optimization (PSO)** to provide both predictive insights and optimized building design recommendations.

---

## 📌 Project Overview

This project enables:

1. **Prediction of Cooling Load (Y2)**

   * Users input building features such as Relative Compactness, Surface Area, Wall Area, Roof Area, Overall Height, Orientation, Glazing Area, and Glazing Distribution.
   * The CatBoost model predicts the expected cooling energy demand.

2. **Real-time Optimisation of Building Features**

   * Users can set constraints for each feature (e.g., maximum surface area, glazing limits).
   * The system uses PSO to compute a **custom optimal design** that minimizes cooling load.
   * Results include both **optimal feature values** and the **minimum predicted cooling load**.

3. **Interactive Visualisation & Decision Support**

   * Compare user input predictions with optimized designs.
   * Supports architects, engineers, and energy planners in designing **energy-efficient buildings**.

---

## ⚙️ Features

* **User-friendly interface** built with Streamlit.
* **Pre-trained CatBoost regression model** for cooling load prediction.
* **PSO optimisation** for generating custom optimal building configurations.
* **Safe input bounds** based on training data statistics.
* **Scalable deployment** via Streamlit Cloud, AWS, or local machine.

---

## 🧩 Building Features (Input Variables)

| Feature | Description               | Units             |
| ------- | ------------------------- | ----------------- |
| X1      | Relative Compactness      | —                 |
| X2      | Surface Area              | m²                |
| X3      | Wall Area                 | m²                |
| X4      | Roof Area                 | m²                |
| X5      | Overall Height            | m                 |
| X6      | Orientation               | categorical (1–5) |
| X7      | Glazing Area              | fraction          |
| X8      | Glazing Area Distribution | categorical (0–5) |

**Target Variable**:

* **Y2**: Cooling Load (kWh/m²)

---

## 🛠️ Requirements

* Python 3.8+
* Streamlit
* CatBoost
* NumPy
* SciPy
* scikit-learn
* pyswarm

Install dependencies:

```bash
pip install streamlit catboost numpy scikit-learn pyswarm
```

---

## 🚀 How to Run

1. Clone this repository:

```bash
git clone https://github.com/yourusername/building-cooling-optimizer.git
cd building-cooling-optimizer
```

2. Ensure you have the following files:

   * `catboost_model.pkl` (pre-trained CatBoost model)
   * `scaler.pkl` (feature scaler used during training)

3. Launch the Streamlit app:

```bash
streamlit run app.py
```

4. Open the URL provided by Streamlit in your browser.

---

## 🧠 How It Works

1. **Prediction Mode**

   * Users enter building features.
   * The app scales the input features using the saved scaler.
   * The CatBoost model predicts the cooling load.

2. **Optimization Mode**

   * Users define upper and lower bounds for features.
   * PSO searches within scaled bounds to find a **feature combination that minimizes cooling load**.
   * Results are transformed back into **real-world units** and displayed along with the predicted minimum cooling load.

---

## ⚠️ Important Notes

* **Scaling:** All user inputs and PSO optimization are scaled using the same scaler as the training dataset to ensure consistent predictions.
* **Integer Features:** Orientation (X6) and Glazing Distribution (X8) are rounded to valid integer categories.
* **Bounded Inputs:** Sliders ensure feature values remain within realistic ranges derived from training data.
* **PSO Performance:** Real-time PSO may take a few seconds to run. For faster deployment, precomputed optimal solutions can be used.

---

## 📊 Benefits

* Quickly predicts cooling load for any building design.
* Provides **data-driven optimization** for energy-efficient design.
* Allows users to **experiment with constraints** and understand trade-offs in building features.

---

## 🔗 Deployment Options

* **Streamlit Cloud:** Ideal for cloud deployment and sharing
* **Local Machine:** For testing or offline use
* **AWS / GCP:** Scalable for production use

---

## 📌 References

1. CatBoost documentation: [https://catboost.ai](https://catboost.ai)
2. Particle Swarm Optimization: Kennedy & Eberhart, 1995
3. Dataset: Energy Efficiency Data Set (UCI Machine Learning Repository)

---

## 👩‍💻 Future Work

* Integrate **SHAP explanations** for feature contributions.
* Allow **multi-objective optimization** (cooling + heating load).
* Validate **user experience for decision support** with architects/engineers.

---