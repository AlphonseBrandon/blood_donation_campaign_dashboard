from flask import Flask, request, jsonify
import joblib
import pandas as pd
import os

app = Flask(__name__)

# --- Configuration and Setup ---
MODEL_FOLDER = 'models'
MODEL_FILENAME = 'RF_model.joblib'
OHE_FILENAME = 'RF_ohe.joblib'
X_TRAIN_FILENAME = 'RF_Xtrain.joblib'


# --- Load Model Components ---
current_directory = os.getcwd()
parent_directory = os.path.abspath(os.path.join(current_directory, '..'))
model_directory_path = os.path.join(parent_directory, MODEL_FOLDER)


if not os.path.exists(model_directory_path):
    print(f'Error: Model folder {model_directory_path} not found.')
    quit()


# Load trained model, one-hot encoder, and training data
trained_model = joblib.load(os.path.join(model_directory_path, MODEL_FILENAME))
one_hot_encoder = joblib.load(os.path.join(model_directory_path, OHE_FILENAME))
x_train_data = joblib.load(os.path.join(model_directory_path, X_TRAIN_FILENAME))


def predict_eligibility(input_data):
    """
    Predicts blood donation eligibility based on provided input features.

    This function preprocesses the input data by one-hot encoding categorical features,
    aligns the input columns with the training data columns, and then uses the loaded
    Random Forest model to predict the eligibility.
    """
    categorical_features = ['genre', 'chronic_diseases', 'transmissible_diseases']

    # --- One-Hot Encode Categorical Features ---
    missing_categorical_cols = set(categorical_features) - set(input_data.columns)
    if missing_categorical_cols:
        raise ValueError(f"Input data missing required categorical columns: {missing_categorical_cols}")

    encoded_categorical_features = one_hot_encoder.transform(input_data[categorical_features])
    encoded_categorical_df = pd.DataFrame(
        encoded_categorical_features,
        columns=one_hot_encoder.get_feature_names_out(categorical_features)
    )
    processed_input_data = pd.concat([input_data.drop(categorical_features, axis=1), encoded_categorical_df], axis=1)


    # --- Align Columns with Training Data ---
    missing_training_cols = set(x_train_data.columns) - set(processed_input_data.columns)
    if missing_training_cols:
        raise ValueError(f"Input data missing columns required for model training: {missing_training_cols}")

    aligned_input_data = processed_input_data.reindex(columns=x_train_data.columns)


    # --- Make Prediction ---
    prediction_class = trained_model.predict(aligned_input_data.values)[0] # .values to avoid feature name warnings
    eligibility_probability = trained_model.predict_proba(aligned_input_data.values)[0][1] # Probability of class 1 (eligible)

    return prediction_class, eligibility_probability



@app.route('/predict', methods=['POST'])
def predict_route():
    """
    API endpoint for predicting blood donation eligibility.
    """
    try:
        required_numeric_features = ['poids', 'taille', 'age']
        request_data = request.get_json()


        # --- Input Data Validation ---
        for feature_name in ['poids', 'taille', 'age', 'genre', 'chronic_diseases', 'transmissible_diseases']:
            if feature_name not in request_data:
                return jsonify({'error': f'Missing input key: {feature_name}'}), 400

        for numeric_feature in required_numeric_features:
            try:
                request_data[numeric_feature] = float(request_data[numeric_feature]) # Ensure numeric features are floats
            except ValueError:
                return jsonify({'error': f'Invalid numeric value for {numeric_feature}'}), 400


        # --- Prepare Input DataFrame and Predict ---
        input_df = pd.DataFrame([request_data])
        prediction_class, eligibility_probability = predict_eligibility(input_df)


        # --- Format and Return JSON Response ---
        response = {
            'prediction': str(prediction_class), 
            'probability': f'{eligibility_probability:.2f}' 
        }
        return jsonify(response)


    except ValueError as value_error:
        return jsonify({'error': str(value_error)}), 400 
    except Exception as server_error:
        return jsonify({'error': str(server_error)}), 500 



if __name__ == '__main__':
    app.run(debug=True) 