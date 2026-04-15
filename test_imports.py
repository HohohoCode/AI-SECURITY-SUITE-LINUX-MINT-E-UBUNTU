import sys
print("Python path:", sys.executable)
print("\nVerificando imports:")

try:
    import xgboost
    print("✅ XGBoost OK - versão:", xgboost.__version__)
except ImportError as e:
    print("❌ XGBoost:", e)

try:
    import lightgbm
    print("✅ LightGBM OK - versão:", lightgbm.__version__)
except ImportError as e:
    print("❌ LightGBM:", e)

try:
    from catboost import CatBoostClassifier
    print("✅ CatBoost OK")
except ImportError as e:
    print("❌ CatBoost:", e)

try:
    import sklearn
    print("✅ Scikit-learn OK - versão:", sklearn.__version__)
except ImportError as e:
    print("❌ Scikit-learn:", e)
