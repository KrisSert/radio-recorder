import os

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to token.pickle using the script's directory
token_path = os.path.join(script_dir, 'token.pickle')
