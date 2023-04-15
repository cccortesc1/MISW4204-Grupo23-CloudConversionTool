from converter import converter
import os

if __name__ == "__main__":
    converter.run(host='0.0.0.0', port=5000, debug=os.environ.get('DEBUG'))