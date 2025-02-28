# Testing

## Unit Testing

The unit tests are designed to provide quick feedback and can easily be run from the terminal. The tests are written using the unittest module and are located in the tests directory. The tests are organized into separate files based on the module they are testing. The all_tests.py file is used to run all the tests at once.

1. Create an .env file in the tests directory. Use the .env.example file as a template and add your credentials.
2. If testing against a local server, open the variables.py file in the tests directory and update the local_creds object properties with your engine IDs. You will need to swap the active_creds variable to point to the local_creds object. You will also need to update the engine id's that you are using to test in the variables file.
3. Open a terminal from the tests directory
4. Make sure you have your virtual environment activated and have installed the package in editable mode. (see top level README.md for instructions)
5. To run the tests, execute the following command:
```
python -m unittest all_tests.py
```
**Note:** If you are having path issues you can try manually setting the path in the terminal `set PYTHONPATH=C:\workspace\sdk\python\ai-server\src` (replace the path with the path to your ai-server directory)

## Notebook Testing

The notebook tests are designed to provide more comprehensive testing of the SDK. They can easily be manipulated to test different scenarios and are located in the tests/notebooks directory. These can also be used as examples of how to use the different SDK features.

(Instructions for VSCode)
1. Make sure you have the Jupyter extension installed.
2. Update the .env file in the tests directory with your credentials.
3. Update cell 4 in the notebook with your engine IDs (if testing locally). Then swap the active_connection variable in cell 3 to point to the local_creds object (if testing locally). 
4. Either run the cells individually or use the "Run All Cells" command to run the entire notebook.
5. You should not need to run the first 4 cells more than once unless you make changes.
