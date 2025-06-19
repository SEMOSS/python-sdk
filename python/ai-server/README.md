# **AI Server**

_ai-server-sdk_ is a python client SDK to connect to the AI Server

## Using this package you can:

- Inference with Models you have acces to within the server
- Create Pandas DataFrame from Databases connections
- Pull Storage objects
- Run pixel and get the direct output or full json response.
- Pull data products from an existing insight using REST API.

## **Install**

    pip install ai-server-sdk

or

    pip install ai-server-sdk[full]

_Note_: The `full` option installs optional dependencies for langchain support.

## **Usage**

To interract with an ai-server instance, import the `ai_server` package and connect via ServerClient.

### Setup

```python
from ai_server import ServerClient

# define access keys
loginKeys = {"secretKey":"<your_secret_key>","accessKey":"<your_access_key>"}

# create connection object by passing in the secret key, access key and base url for the api
server_connection = ServerClient(base='<Your deployed server Monolith URL>', access_key=loginKeys['accessKey'], secret_key=loginKeys['secretKey'])

# if you are logged in with OAuth, a bearer token can be provided
server_connection = ServerClient(base='<Your deployed server Monolith URL>', bearer_token="bearer_token_value")

```

### Inference with different Model Engines

```python
# import the model engine class for the ai_server package
from ai_server import ModelEngine

model = ModelEngine(engine_id="2c6de0ff-62e0-4dd0-8380-782ac4d40245", insight_id=server_connection.cur_insight)

# if your model is for text-generation, ask a question
model.ask(question = 'What is the capital of France?')
# example output
# {'response': 'The capital of France is Paris.',
#  'messageId': '0a80c2ce-76f9-4466-b2a2-8455e4cab34a',
#  'roomId': '28261853-0e41-49b0-8a50-df34e8c62a19',
#  'numberOfTokensInResponse': 6, 'numberOfTokensInPrompt': 6}

# stream the response
for chunk in model.stream_ask(question=question):
    print(chunk, end="", flush=True)

# instantiate a different model for embeddings, get embeddings for some text
model = ModelEngine(engine_id="e4449559-bcff-4941-ae72-0e3f18e06660", insight_id=server_connection.cur_insight)
model.embeddings(strings_to_embed=['text1','text2'])
# example output
# {'response': [[0.007663827, -0.030877046, ... -0.035327386]],
#  'numberOfTokensInPrompt': 8, 'numberOfTokensInResponse': 0}

# integrate with langchain
model = ModelEngine(engine_id="2c6de0ff-62e0-4dd0-8380-782ac4d40245", insight_id=server_connection.cur_insight)
langchain_llm = model.to_langchain_chat_model()
question = 'what is the capital of france?'
output = langchain_llm.invoke(input = question)
# example output
# AIMessage(content='The capital of France is Paris.', additional_kwargs={}, response_metadata={'numberOfTokensInResponse': 6, 'numberOfTokensInPrompt': 6, 'messageType': 'CHAT', 'messageId': 'bd4f54fe-fd9b-4538-8531-696c4cdae01f', 'roomId': '57c03aae-5c10-498e-9a25-027201daa917'}, id='run-e9672e53-0cfd-4cb6-b9e4-3d5304314f73-0')

# stream the response
for chunk in langchain_llm.stream(question):
    print(chunk.content, end="", flush=True)

```

### Interact with a Vector Database by adding document(s), querying, and removing document(s)

```python
# import the vector engine class for the ai_server package
from ai_server import VectorEngine

# initialize the connection to the vector database
vectorEngine = VectorEngine(engine_id="221a50a4-060c-4aa8-8b7c-e2bc97ee3396", insight_id=server_connection.cur_insight)

# Add document(s) that have been uploaded to the insight
vectorEngine.addDocument(file_paths = ['fileName1.pdf', 'fileName2.pdf', ..., 'fileNameX.pdf'])

# Add Vector CSV File document(s) that have been uploaded to the insight
vectorEngine.addVectorCSVFile(file_paths = ['fileName1.csv', 'fileName2csv', ..., 'fileNameX.csv'])

# Perform a nearest neighbor search on the embedded documents
vectorEngine.nearestNeighbor(search_statement = 'Sample Search Statement', limit = 5)

# List all the documents the vector database currently comprises of
vectorEngine.listDocuments()

# Remove document(s) from the vector database
vectorEngine.removeDocument(file_names = ['fileName1.pdf', 'fileName2.pdf', ..., 'fileNameX.pdf'])

# integrate with langchain
vector = VectorEngine(engine_id = "221a50a4-060c-4aa8-8b7c-e2bc97ee3396", insight_id=server_connection.cur_insight)
langhchain_vector = vector.to_langchain_vector_store()
langhchain_vector.listDocs()
langhchain_vector.addDocs(file_paths = ['file1.pdf','file2.pdf',...])
langhchain_vector.removeDocs(file_names = ['file1.pdf','file2.pdf',...])
langhchain_vector.similaritySearch(query = 'Sample Search Statement', k=5)
```

### Connect to Databases and execute create, read, and delete operations

#### Run the passed string query against the engine. The query passed must be in the structure that the specific engine implementation.

```python
# import the database engine class for the ai_server package
from ai_server import DatabaseEngine

# Create an relation to database based on the engine identifier
database = DatabaseEngine(engine_id="4a1f9466-4e6d-49cd-894d-7d22182344cd", insight_id=server_connection.cur_insight)
database.execQuery(query='SELECT PATIENT, HEIGHT, WEIGHT FROM diab LIMIT 4')
```

|     | PATIENT | HEIGHT | WEIGHT |
| --: | ------: | -----: | -----: |
|   0 |   20337 |     64 |    114 |
|   1 |    3750 |     64 |    161 |
|   2 |   40785 |     67 |    187 |
|   3 |   12778 |     72 |    145 |

#### Run query operations against the engine. Query must be in the structure that the specific engine implementation

```python
# insert statement
database.insertData(query = 'INSERT INTO table_name (column1, column2, column3, ...) VALUES (value1, value2, value3, ...)')
# update statement
database.updateData(query = 'UPDATE table_name set column1=value1 where age=19')
# delete statement
database.removeData(query='DELETE FROM diab WHERE age=19')

# integrate with langchain
database = DatabaseEngine(engine_id="4a1f9466-4e6d-49cd-894d-7d22182344cd", insight_id=server_connection.cur_insight)
langhchain_db = database.to_langchain_database()
langhchain_db.executeQuery(query = 'SELECT * FROM table_name')
langhchain_db.insertQuery(query = 'INSERT INTO table_name (column1, column2, column3, ...) VALUES (value1, value2, value3, ...)')
langhchain_db.updateQuery(query = 'UPDATE table_name set column1=value1 WHERE condition')
langhchain_db.removeQuery(query = 'DELETE FROM table_name WHERE condition')
```

### Run Function Engines

```python
# import the function engine class for the ai_server package
from ai_server import FunctionEngine

# initialize the connection ot the function engine
function = FunctionEngine(engine_id="f3a4c8b2-7f3e-4d04-8c1f-2b0e3dabf5e9", insight_id=server_connection.cur_insight)
function.execute({"lat":"37.540","lon":"77.4360"})
# example output
# '{"cloud_pct": 2, "temp": 28, "feels_like": 27, "humidity": 20, "min_temp": 28, "max_temp": 28, "wind_speed": 5, "wind_degrees": 352, "sunrise": 1716420915, "sunset": 1716472746}'
```

### Using REST API to pull data product from an Insight

```python
# define the Project ID
projectId = '30991037-1e73-49f5-99d3-f28210e6b95c'

# define the Insight ID
inishgtId = '26b373b3-cd52-452c-a987-0adb8817bf73'

# define the SQL for the data product you want to query within the insight
sql = 'select * FROM DATA_PRODUCT_123'

# if you dont provide one of the following, it will ask you to provide it via prompt
diabetes_df = server_connection.import_data_product(project_id = projectId, insight_id = inishgtId, sql = sql)
diabetes_df.head()
```

|     | AGE | PATIENT | WEIGHT |
| --: | --: | ------: | -----: |
|   0 |  19 |    4823 |    119 |
|   1 |  19 |   17790 |    135 |
|   2 |  20 |    1041 |    159 |
|   3 |  20 |    2763 |    274 |
|   4 |  20 |    3750 |    161 |

### Get the output or JSON response of any pixel

```python
# run the pixel and get the output
server_connection.run_pixel('1+1')
2

# run the pixel and get the entire json response
server_connection.run_pixel('1+1', full_response=True)
# example output
# {'insightID': '8b419eaf-df7d-4a7f-869e-8d7d59bbfde8',
# 'sessionTimeRemaining': '7196',
# 'pixelReturn': [{'pixelId': '3',
#   'pixelExpression': '1 + 1 ;',
#   'isMeta': False,
#   'output': 2,
#   'operationType': ['OPERATION']}]}
```

### Upload files to an Insight

```python
from ai_server import ServerClient

# define access keys
loginKeys = {"secretKey":"<your_secret_key>","accessKey":"<your_access_key>"}

# create connection object by passing in the secret key, access key and base url for the api
server_connection = ServerClient(access_key=loginKeys['accessKey'], secret_key=loginKeys['secretKey'], base='<Your deployed server Monolith URL>')

server_connection.upload_files(files=["path_to_local_file1", "path_to_local_file2"], project_id="your_project_id", insight_id="your_insight_id", path="path_to_upload_files_in_insight")
```

### Using tools via langchain

```python

import ai_server
from ai_server import ServerClient
from ai_server import ModelEngine
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

loginKeys = {"secretKey":"<your_secret_key>","accessKey":"<your_access_key>"}

# create connection object by passing in the secret key, access key and base url for the api
server_connection = ServerClient(base='<Your deployed server Monolith URL>', access_key=loginKeys['accessKey'], secret_key=loginKeys['secretKey'])

model = ModelEngine(
    engine_id="4acbe913-df40-4ac0-b28a-daa5ad91b172",
    insight_id=server_connection.cur_insight,
)

langchain_model = model.to_langchain_chat_model()

@tool
def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Adds a and b.

    Args:
        a: first int
        b: second int
    """
    return a + b


@tool
def divide(a: int, b: int) -> float:
    """Divide a and b.

    Args:
        a: first int
        b: second int
    """
    return a / b


tools = [add, multiply, divide]

query = "What is 3 * 12?"
messages = [HumanMessage(query)]

langchain_chat_with_tools = langchain_model.bind_tools(tools)
result = langchain_chat_with_tools.invoke(messages)
messages.append(result)

for tool_call in result.tool_calls:
    selected_tool = {"add": add, "multiply": multiply}[tool_call["name"].lower()]
    tool_msg = selected_tool.invoke(tool_call)
    messages.append(tool_msg)

final_output = langchain_chat_with_tools.invoke(messages)
print(final_output)

```

---
