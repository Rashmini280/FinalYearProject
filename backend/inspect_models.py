import pickle
import joblib
import sys

def inspect(path):
    with open('model_info.txt', 'a', encoding='utf-8') as log:
        log.write(f"--- Inspecting {path} ---\n")
        try:
            try:
                with open(path, 'rb') as f:
                    obj = pickle.load(f)
            except:
                 obj = joblib.load(path)
            
            log.write(f"Type: {type(obj)}\n")
            log.write(f"Content: {str(obj)[:500]}\n")
            if hasattr(obj, 'get_params'):
                log.write(f"Params: {obj.get_params()}\n")
        except Exception as e:
            log.write(f"Error loading {path}: {e}\n")

# Clear file
with open('model_info.txt', 'w') as f: pass

inspect('Models/fake_news_classifier.pkl')
inspect('Models/text_scaler.pkl')
