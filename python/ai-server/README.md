# **AI Server**

_ai-server-sdk_ is a python client SDK to connect to the AI Server

## Using this package you can:

- Inference with Models you have acces to within the server
- Create Pandas DataFrame from Databases connections
- Push files to, and pull files from, Storage engines
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
model.ask(command = 'What is the capital of France?')
# example output
# {'response': 'The capital of France is Paris.',
#  'messageId': '0a80c2ce-76f9-4466-b2a2-8455e4cab34a',
#  'messageType': 'CHAT',
#  'roomId': '28261853-0e41-49b0-8a50-df34e8c62a19',
#  'numberOfTokensInResponse': 6, 'numberOfTokensInPrompt': 6}

# stream the response
for chunk in model.stream_ask(command=command):
    print(chunk, end="", flush=True)

# instantiate a different model for embeddings, get embeddings for some text
model = ModelEngine(engine_id="e4449559-bcff-4941-ae72-0e3f18e06660", insight_id=server_connection.cur_insight)
model.embeddings(strings_to_embed=['text1','text2'])
# example output
# {'response': [[0.007663827, -0.030877046, ... -0.035327386]],
#  'numberOfTokensInPrompt': 8, 'numberOfTokensInResponse': 0}

# Integrate with langchain
model = ModelEngine(engine_id="2c6de0ff-62e0-4dd0-8380-782ac4d40245", insight_id=server_connection.cur_insight)
langchain_llm = model.to_langchain_chat_model()
command = 'What is the capital of France?'
output = langchain_llm.invoke(input = command)
# example output
# AIMessage(content='The capital of France is Paris.', additional_kwargs={}, response_metadata={'numberOfTokensInResponse': 6, 'numberOfTokensInPrompt': 6, 'messageType': 'CHAT', 'messageId': 'bd4f54fe-fd9b-4538-8531-696c4cdae01f', 'roomId': '57c03aae-5c10-498e-9a25-027201daa917'}, id='run-e9672e53-0cfd-4cb6-b9e4-3d5304314f73-0')

# stream the response
for chunk in langchain_llm.stream(command):
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

### Move files in and out of Storage engines

```python
# import the storage engine class for the ai_server package
from ai_server import StorageEngine

storage = StorageEngine(engine_id="68b7e856-2312-4106-ab7a-7d7bb006173a", insight_id=server_connection.cur_insight)

# list the root of the engine
storage.list(storagePath="/")
# example output
# ['reports/', 'college.csv']

# the same listing with details on each entry
storage.listDetails(storagePath="/reports")
# example output
# [{'Path': '/reports/q1.csv', 'Name': 'q1.csv', 'Size': 51049, 'MimeType': 'text/csv',
#   'ModTime': '2026-07-17T20:54:33.767Z', 'IsDir': False, 'Metadata': {'author': 'me'}}]
```

Paths are always relative to the root of the engine, and the `Path` on a listing entry can be handed straight back to any other method. Azure is the one engine where the root is the account rather than a single container, so its paths start with the container name, for example `mycontainer/reports/q1.csv`. Listing `/` there shows the containers you can reach.

```python
# copy one file, or a folder, up to storage
storage.copyToStorage(storagePath="/reports", localPath="/local/path/q1.csv", metadata={"author": "me"})

# and back down again
storage.copyToLocal(storagePath="/reports/q1.csv", localPath="/local/path")

# sync a whole local folder up, skipping files that are already there and unchanged
result = storage.syncLocalToStorage(storagePath="/reports", localPath="/local/reports")
# example output
# {'storagePath': 'reports', 'status': 'SUCCESS',
#  'uploadedFiles': ['reports/q1.csv'], 'skippedFiles': ['reports/q2.csv'], 'failedFiles': []}
```

`syncLocalToStorage` returns the outcome of the sync. A sync where some files failed comes back with a `status` of `PARTIAL` and the names in `failedFiles` **without raising**, so check the status to know that every file arrived:

```python
if result["status"] != "SUCCESS":
    print(f"{len(result['failedFiles'])} files did not make it: {result['failedFiles']}")
```

Engines that hand the whole transfer off in one call cannot name individual files, and report `SUCCESS` with empty lists. An empty `uploadedFiles` means "not reported", not "nothing uploaded".

```python
# pull a whole folder down
storage.syncStorageToLocal(storagePath="/reports", localPath="/local/reports")

# read a file without writing it to the insight workspace first
storage.getFileAsBase64(storagePath="/reports/q1.csv")

# replace the metadata on a file already in storage. This overwrites rather than
# merges, so pass every key the file should end up with
storage.updateFileMetadata(storagePath="/reports/q1.csv", metadata={"author": "someone else"})

# delete a file or a folder. leaveFolderStructure keeps the folder itself visible
storage.deleteFromStorage(storagePath="/reports/q1.csv")
storage.deleteFromStorage(storagePath="/reports", leaveFolderStructure=True)
```

On engines that keep versions (S3 style, with bucket versioning turned on) you can list them and pull a specific one:

```python
versions = storage.listVersions(storagePath="/reports/q1.csv")
# example output
# [{'versionId': 'CvV6ZQ...', 'lastModified': '2026-07-17T20:54:33.767Z',
#   'size': 51049, 'isLatest': True, 'key': 'reports/q1.csv'}]

storage.copyToLocal(storagePath="/reports/q1.csv", localPath="/local/path", version=versions[1]["versionId"])
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
# 'pixelReturn': [{'pixelId': '3',
#   'pixelExpression': '1 + 1 ;',
#   'isMeta': False,
#   'output': 2,
#   'operationType': ['OPERATION']}]}
```

### Upload / Download files to an Insight

```python
from ai_server import ServerClient

# define access keys
loginKeys = {"secretKey":"<your_secret_key>","accessKey":"<your_access_key>"}

# create connection object by passing in the secret key, access key and base url for the api
server_connection = ServerClient(access_key=loginKeys['accessKey'], secret_key=loginKeys['secretKey'], base='<Your deployed server Monolith URL>')

server_connection.upload_files(files=["path_to_local_file1", "path_to_local_file2"], project_id="your_project_id", insight_id="your_insight_id", path="path_to_upload_files_in_insight")

server_connection.download_file(file=["path_to_insight_file"], project_id="your_project_id", insight_id="your_insight_id",custom_filename="filename_for_download")
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
