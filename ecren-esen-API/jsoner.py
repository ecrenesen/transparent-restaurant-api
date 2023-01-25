"""
Author: Ecren Esen
Date:20th of January 2023
"""

import time
import json

starttime = time.time()
#Restaurant Data opened with json built-in json module
jsondata = json.loads(open("data.json","r").read())
readout = time.time()
alling = jsondata["ingredients"]
meals = jsondata["meals"]



"""
1 FOR VEGAN
0 FOR VEGETARIAN

"""

def getvegan_vegetarian(which):
    if which == 1:
        value = "vegan"
    if which == 0:
        value="vegetarian"

    output = []
    for a in meals:
        id__ = a["id"]
        ingredients = a["ingredients"]
        counter=0
        for ing in ingredients:
            current = {}
            for i in alling:
                if ing["name"] == i["name"]:
                    current = i
                    break

            #print(current)
            try:
                current["groups"].index(value)
                #output.append(current)
            except:

                counter+=1
        if counter == 0:
            output.append(a)
    return output



outputdata = {}
outputdata["vegetarian"] = getvegan_vegetarian(0)
outputdata["vegan"] = getvegan_vegetarian(1)
outputdata["both"] = outputdata["vegetarian"]+outputdata["vegan"]
open("predataveg.json","w").write(json.dumps(outputdata,indent=4,ensure_ascii=False))
endtime = time.time()
print("FILEOPEN as ms:",(readout-starttime)*1000)
print("OUTTIME as ms:",(endtime-starttime)*1000)
