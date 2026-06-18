import joblib

encoders = joblib.load("models/encoders.pkl")

for key in encoders:
    print("=" * 50)
    print("Kolom :", key)
    print("Classes :", encoders[key].classes_)
    print()