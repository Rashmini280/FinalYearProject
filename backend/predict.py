import torch

# Load the file 
state_dict = torch.load('backend/Models/best_model.pth', map_location=torch.device('cpu'))

# Print the "Architecture Keys" (The names of the layers)
print("--- Model Layers Found ---")
for key in list(state_dict.keys())[:10]: # Just show the first 10 layers
    print(key)

# Print a tiny sample of the actual weights (The math)
print("\n--- Sample Weights from Layer 1 ---")
first_layer_key = list(state_dict.keys())[0]
print(state_dict[first_layer_key][0][:5])