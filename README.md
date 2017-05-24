# beforeairbnb

Keywords
- Python
- Airbnb API
- AWS Lambda
- Serverless
- Anima Plugin

# How To Use
1. Download this project.
2. Deploy this folder to lambda by using serverless. (sls deploy)
3. Call API and get JSON file, {result}.
 - Method : GET
 - Parameter : location
  - location is airbnb search_query such as 'Yeonnam-ro 3 gil, Seoul', '127.3829281, 36.2718111', '서울시 마포구 성산1동' and so on...
4. Distribute each information to frontend elements from {result}.
5. Enjoy!
