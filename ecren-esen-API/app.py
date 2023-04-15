from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
import cgi
import random


"""
restaurant API with http.server and json built-in python packages
 by Ecren Nur Esen
"""
# Veriyi önden tanımladım çünkü her request başına dosya açmasını istemedim
alldata = json.loads(open("data.json", "r").read())

categorized = json.loads(open("predataveg.json", "r").read())


def dictionarize(inputstring):
    output = {}
    allvalues = inputstring.split("&")
    for a in allvalues:
        splitter = a.split("=")
        name = splitter[0]
        value = splitter[1]
        output[name] = value
    return output


def getingredients(mealjson):
    output = []
    try:
        mealjson["ingredients"][0]

    except:
        return []

    for ing in mealjson["ingredients"]:
        for i in alldata["ingredients"]:
            if ing["name"] == i["name"]:
                output.append(i)
                break

    return output


def get_random_meal_by_budget(budget: int):
    meals = alldata["meals"]
    affordable_meals = []
    for meal in meals:
        total_price = 0
        ingredients = []
        for ingredient in meal["ingredients"]:
            ingredient_name = ingredient["name"]
            ingredient_quantity = ingredient["quantity"]
            quantity_type = ingredient["quantity_type"]
            isAffordable = True
            try:
                ingredient_options = [
                    i for i in alldata["ingredients"] if i["name"] == ingredient_name
                ][0]["options"]
                affordable_options = [
                    i
                    for i in ingredient_options
                    if i["price"] * ingredient_quantity * 0.001 <= budget
                ]

                if len(affordable_options) > 0:
                    option = random.choice(affordable_options)
                    ingredients.append(option)
                    optionPrice = option["price"] * ingredient_quantity * 0.001
                    total_price += optionPrice
                else:
                    isAffordable = False
            except:
                print("Ingredient does not found: ", ingredient_name)

        if isAffordable and total_price <= budget:
            meal["affordable_options"] = ingredients
            affordable_meals.append(meal)
    if len(affordable_meals) > 0:
        return random.choice(affordable_meals)
    else:
        return None


class App(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(301)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        # NOTE KALITE KONTROL
        if "/quality" in self.path:
            arguments = dictionarize(
                self.rfile.read(int(self.headers["Content-Length"])).decode()
            )
            try:
                meal_id = arguments["meal_id"]
            except:
                meal_id = None
            try:
                currentmeal = alldata["meals"][int(meal_id.strip()) - 1]
            except:
                currentmeal = None

            if meal_id == None or currentmeal == None:
                self.wfile.write(
                    bytes(
                        json.dumps(
                            {"error": "Try to give a valid ID for a meal"},
                            indent=4,
                            ensure_ascii=False,
                        ),
                        "utf-8",
                    )
                )
            elif len(list(arguments.keys())) == 1 and meal_id != None:
                self.wfile.write(
                    bytes(
                        json.dumps({"quality": 30}, indent=4, ensure_ascii=False),
                        "utf-8",
                    )
                )

            totalofit = 0
            lengthofingredients = 0
            theingredients_given = []
            if len(list(arguments.keys())) > 1 and meal_id != None:
                for l in list(arguments.keys()):
                    if l == "meal_id":
                        continue
                    else:
                        theingredients_given.append(l)

                for i in currentmeal["ingredients"]:
                    equal = 0
                    for the in theingredients_given:
                        if the.strip().lower() in i["name"].strip().lower():
                            equal = 1
                            value = arguments[the]

                            if value == "low":
                                totalofit += 10
                            if value == "high":
                                totalofit += 30
                            if value == "medium":
                                totalofit += 20

                            break
                    if equal == 0:
                        totalofit += 30
                        lengthofingredients += 1

                output = totalofit / len(currentmeal["ingredients"])
                self.wfile.write(
                    bytes(json.dumps({"quality": output}, indent=4), "utf-8")
                )

        elif "/random" in self.path:
            arguments = dictionarize(
                self.rfile.read(int(self.headers["Content-Length"])).decode()
            )
            budget = int(arguments["budget"])
            meal = get_random_meal_by_budget(budget)

            if meal:
                self.wfile.write(
                    bytes(json.dumps(meal, indent=4, ensure_ascii=False), "utf-8")
                )
            else:
                self.wfile.write(
                    bytes(
                        json.dumps(
                            {"error": "There is no meal that fits your budget"},
                            indent=4,
                            ensure_ascii=False,
                        ),
                        "utf-8",
                    )
                )

        # NOTE FIYAT KONTROL
        elif "/price" in self.path:
            arguments = dictionarize(
                self.rfile.read(int(self.headers["Content-Length"])).decode()
            )
            try:
                meal_id = int(arguments["meal_id"])
            except:
                meal_id = None
            try:
                currentmeal = alldata["meals"][meal_id - 1]
            except:
                currentmeal = None

            if currentmeal == None or meal_id == None:
                self.wfile.write(
                    bytes(
                        json.dumps(
                            {"error": "Couldn't find meal"},
                            indent=4,
                            ensure_ascii=False,
                        ),
                        "utf-8",
                    )
                )
            else:
                if len(list(arguments.keys())) == 1:
                    counter = 0
                    for ing in currentmeal["ingredients"]:
                        for i in alldata["ingredients"]:
                            if ing["name"] == i["name"]:
                                parameter = i["options"][0]["price"]
                                quantity = ing["quantity"]
                                output = (quantity / 1000) * parameter
                                counter += output
                                break
                    self.wfile.write(
                        bytes(
                            json.dumps(
                                {"price": counter}, indent=4, ensure_ascii=False
                            ),
                            "utf-8",
                        )
                    )
                if len(list(arguments.keys())) > 1:
                    counter = 0
                    temproraryarguments = []
                    for a in arguments:
                        if a == "meal_id":
                            continue
                        else:
                            if (
                                arguments[a] == "low"
                                or arguments[a] == "high"
                                or arguments[a] == "medium"
                            ):
                                temproraryarguments.append({f"{a}": f"{arguments[a]}"})

                    for ing in currentmeal["ingredients"]:
                        for i in alldata["ingredients"]:
                            if ing["name"] == i["name"]:
                                default = 0
                                addition = 0
                                for arg in temproraryarguments:
                                    argstring = str(list(arg.keys())[0])
                                    if (
                                        argstring.lower().strip()
                                        in ing["name"].lower().strip()
                                    ):
                                        if arg[argstring] == "low":
                                            addition += 0.1
                                            default = 2
                                        if arg[argstring] == "medium":
                                            default = 1
                                            addition += 0.05
                                        break

                                parameter = i["options"][default]["price"]
                                quantity = ing["quantity"]
                                output = (quantity / 1000) * parameter
                                counter += output
                                counter += addition
                                break
                    self.wfile.write(
                        bytes(
                            json.dumps(
                                {"price": round(counter, 2)},
                                indent=4,
                                ensure_ascii=False,
                            ),
                            "utf-8",
                        )
                    )
        else:
            self.wfile.write(
                bytes(
                    json.dumps(
                        {"Author": "Ecren Esen", "Description": "Page "},
                        indent=4,
                    ),
                    "utf-8",
                )
            )

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        arguments = {}
        try:
            pathsplitter = self.path.split("?")[1]
            try:
                allarguments = pathsplitter.split("&")
                for a in allarguments:
                    pathsplitter = a
                    arguments[pathsplitter.split("=")[0]] = pathsplitter.split("=")[1]

            except:
                arguments[pathsplitter.split("=")[0]] = pathsplitter.split("=")[1]
        except:
            pass
        # print(arguments)

        if self.path == "/":
            self.wfile.write(
                bytes(
                    json.dumps(
                        {
                            "Author": "Ecren Esen",
                            "Description": "Hello this is the API I wrote for Transparent Restaurant",
                        },
                        indent=4,
                    ),
                    "utf-8",
                )
            )

        # MEAL listeleyici argümanlar çalışıyor
        elif "/listMeals" in self.path:
            try:
                is_vegetarian = arguments["is_vegetarian"]
            except:
                is_vegetarian = False
            try:
                is_vegan = arguments["is_vegan"]
            except:
                is_vegan = False

            if is_vegan == "false":
                is_vegan = False
            if is_vegetarian == "false":
                is_vegetarian = False
            if is_vegetarian == "true":
                is_vegetarian = True
            if is_vegan == "true":
                is_vegan = True

            if is_vegan == True and is_vegetarian == False:
                self.wfile.write(
                    bytes(
                        json.dumps(categorized["vegan"], indent=4, ensure_ascii=False),
                        "utf-8",
                    )
                )
            elif is_vegetarian == True and is_vegan == False:
                self.wfile.write(
                    bytes(
                        json.dumps(
                            categorized["vegetarian"], indent=4, ensure_ascii=False
                        ),
                        "utf-8",
                    )
                )
            elif is_vegetarian == True and is_vegan == True:
                self.wfile.write(
                    bytes(
                        json.dumps(categorized["both"], indent=4, ensure_ascii=False),
                        "utf-8",
                    )
                )
            else:
                self.wfile.write(
                    bytes(
                        json.dumps(alldata["meals"], indent=4, ensure_ascii=False),
                        "utf-8",
                    )
                )

        # id ile spesifik yiyecek alma
        elif "/getMeal" in self.path:
            try:
                meal_id = int(arguments["id"].strip())
                current_data = None
                try:
                    current_data = alldata["meals"][meal_id - 1]
                except:
                    pass

                if current_data == None:
                    self.wfile.write(
                        bytes(
                            json.dumps(
                                {"error": "The meal is not in the list"},
                                indent=4,
                                ensure_ascii=False,
                            ),
                            "utf-8",
                        )
                    )
                else:
                    self.wfile.write(
                        bytes(
                            json.dumps(current_data, indent=4, ensure_ascii=False),
                            "utf-8",
                        )
                    )

            except Exception as e:
                self.wfile.write(
                    bytes(
                        json.dumps(
                            {"error": "You didn't specified ID of the meal"},
                            indent=4,
                            ensure_ascii=False,
                        ),
                        "utf-8",
                    )
                )

        # search with GET
        elif "/search" in self.path:
            try:
                query = arguments["query"]
                results = []
                for m in alldata["meals"]:
                    if query.lower().strip() in m["name"].lower():
                        results.append(m)
                output = {"output": results}
                self.wfile.write(
                    bytes(json.dumps(output, indent=4, ensure_ascii=False), "utf-8")
                )
            except:
                self.wfile.write(
                    bytes(
                        json.dumps(
                            {"error": "We couldn't find what you are looking for."},
                            indent=4,
                            ensure_ascii=False,
                        ),
                        "utf-8",
                    )
                )

        else:
            self.wfile.write(
                bytes(
                    json.dumps(
                        {"Author": "Ecren Nur Esen", "Description": "None"},
                        indent=4,
                    ),
                    "utf-8",
                )
            )


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), App)
    print("Server is running on port 8080")
    server.serve_forever()
    server.server_close()
