import json
str = "{\"-par\": 2, \"-part\": 2, \"-maxet\": \"3 [hr]\",\"-ccl\": T:\\test\\ccls\\BluntBody3.ccl,}"
print str
dict = json.loads(str)
print dict

