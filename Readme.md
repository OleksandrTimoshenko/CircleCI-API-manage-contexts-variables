 # Circle CI API
 ## Use the script main.py to manage CircleCI variables
 ```
mkdir -p ./files/values
mkdir -p ./files/variables
cp .env.example .env
# Paste correct CIRCLE_CI_TOKEN and ORGANIZATION_ID from your CircleCi
```
## In the values folder create files with context names and variable lists
### !!!ATTENTION!!! Only those variables that are written in the files ./files/value/<context_name>.txt will be affected
 ```
Examples:
python3 ./main.py -c my_context_1,my_context_2 -v -ap  - update my_context_1 and my_context_2 contexts with auto approve and detailed output
python3 ./main.py -c my_context -del                   - delete variables from my_context context
python3 ./main.py -a -l                                - write variables names list to the file and update all variables in all contexts
python3 ./main.py -c my_context -l                     - write variables names from the my_context context to the file and update all variables into my_context context
 ```