# Gradio deployment
import gradio as gr
from pycaret.classification import *

# load pickled model
saved_final_dt = load_model("Final dt Model 26Nov2022")


# define predict function
def predict(model, sepal_length, sepal_width, petal_length, petal_width):
    # create dataframe for prediction
    df = pd.DataFrame.from_dict(
        {
            "sepal_length": [sepal_length],
            "sepal_width": [sepal_width],
            "petal_length": [petal_length],
            "petal_width": [petal_width],
        }
    )

    # predict on the new dataset and return prediction
    pred = predict_model(saved_final_dt, df, raw_score=True)

    # return prediction as a dictionary
    return {
        "Iris-setosa": pred["Score_Iris-setosa"][0].astype("float64"),
        "Iris-versicolor": pred["Score_Iris-versicolor"][0].astype("float64"),
        "Iris-virginica": pred["Score_Iris-virginica"][0].astype("float64"),
    }


# create the user interface using gradio
# Create example list
example = [
    ["5.1", "3.5", "1.4", "0.2"],
    ["6.4", "3.2", "4.5", "1.5"],
    ["6.9", "3.1", "5.4", "2.1"],
]
label = ["Iris-setosa", "Iris-versicolor", "Iris-virginica"]

# Create UI
set_int = gr.Interface(
    predict,
    title="Iris Flower Prediction",
    description="This app predicts the type of Iris flower based on the input parameters.",
    inputs=[
        gr.inputs.Slider(minimum=1, maximum=10, default=5.1, label="sepal_length"),
        gr.inputs.Slider(minimum=1, maximum=10, default=3.5, label="sepal_width"),
        gr.inputs.Slider(minimum=1, maximum=10, default=1.4, label="petal_length"),
        gr.inputs.Slider(minimum=1, maximum=10, default=0.2, label="petal_width"),
    ],
    outputs="label",
    examples=example,
    live=True,
)

# Run the app
set_int.launch()