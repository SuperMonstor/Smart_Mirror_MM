
import todoist
api = todoist.TodoistAPI('eaa65fe252147686becffe233381ee0a92232d29')
api.sync()
full_name = api.state['user']['full_name']
print(api.state)
print(full_name)



for items in api.state['items']:
     print(items['content'])
