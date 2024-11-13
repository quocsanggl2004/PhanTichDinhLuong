import json
import os
from pymongo import MongoClient

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["dtb_data"]
collection = db["clt_data"]

# Đọc file JSON
json_file_path = os.path.join(os.path.dirname(__file__), 'spiders', 'TLP.json')
print(json_file_path)
print(f"Đường dẫn tới tệp JSON: {json_file_path}")
# Kiểm tra xem tệp có tồn tại không
if not os.path.exists(json_file_path):
    print(f"Tệp {json_file_path} không tồn tại!")
else:
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
        # Chèn dữ liệu vào MongoDB
        collection.insert_many(data)

    print("Dữ liệu JSON đã được chèn vào MongoDB thành công!")