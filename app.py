import os
from flask import Flask, request, render_template
from datetime import date
import json
import swagger_client
from swagger_client.rest import ApiException
import requests

#Defining App
app = Flask(__name__)

#API Stuff
configuration = swagger_client.Configuration()
configuration.api_key['key'] = 'b527da88f72a457baaf22901231308'

api_instance = swagger_client.APIsApi(swagger_client.ApiClient(configuration))
q = 'Paris'
lang = 'English'

todayDateV1 = date.today().strftime("%m_%d_%y")
todayDateV2 = date.today().strftime("%d-%B-%Y")

#if tasks.txt not exist, then create it
if 'tasks.txt' not in os.listdir('.'):
    with open('tasks.txt', 'w') as f:
        f.write('')

#Grabs Location using API:
def get_ip():
    response = requests.get('https://api64.ipify.org?format=json').json()
    return response["ip"]


def get_location():
    ip_address = get_ip()
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    location_data = {
        "ip": ip_address,
        "city": response.get("city"),
        "region": response.get("region"),
        "country": response.get("country_name")
    }
    return location_data

#Grabs Weather Data From API
def getWeatherData():
    locationData = get_location()
    city = locationData["city"]
    #change to equal city l8r
    q = "Fremont"
    try:
        # Realtime API
        api_response = api_instance.realtime_weather(q, lang=lang)
        data = str(api_response)
        with open('test.json', 'w') as f:
            data = data.replace("'", '"')
            data = data.replace('None', '"None"')
            f.writelines(data)
        with open('test.json') as json_file:
            data = json.load(json_file)
        'All information needed'
        tempF = data["current"]["feelslike_f"]
        textWeather = data["current"]["condition"]["text"]
        imageAddressWeather = data["current"]["condition"]["icon"]
        return tempF, textWeather, imageAddressWeather
    except ApiException as e:
        print("Exception when calling APIsApi->realtime_weather: %s\n" % e)

#Task-Related fucntions:
def getTaskList(): #Returns all tasks in tasks.txt as a list
    with open('tasks.txt', 'r') as f:
        tasklist = f.readlines()
    return tasklist


def newTaskList(): #Deletes all previous tasks
    os.remove('tasks.txt')
    with open('tasks.txt', 'w') as f:
        f.write('')


def updateTaskList(tasklist): #Deletes all previous tasks and updates with new tasks
    os.remove('tasks.txt')
    with open('tasks.txt', 'w') as f:
        f.writelines(tasklist)

#Routing
@app.route('/') #Homepage routung
def index():
    weatherTemp, weatherText, weatherIcon = getWeatherData()
    return render_template('home.html', datetoday2=todayDateV2, tasklist=getTaskList(), l=len(getTaskList()), weatherIcon=weatherIcon, weatherText=weatherText, weatherTemp = weatherTemp)


@app.route('/clear') #Route to clear entire list
def clear_list():
    newTaskList()
    weatherTemp, weatherText, weatherIcon = getWeatherData()
    return render_template('home.html', datetoday2=todayDateV2, tasklist=getTaskList(), l=len(getTaskList()), weatherIcon=weatherIcon, weatherText=weatherText, weatherTemp = weatherTemp)


@app.route('/addtask', methods=['POST']) #Route to add item to list
def add_task():
    task = request.form.get('newtask')
    weatherTemp, weatherText, weatherIcon = getWeatherData()
    with open('tasks.txt', 'a') as f:
        f.writelines(task + '\n')
    return render_template('home.html', datetoday2=todayDateV2, tasklist=getTaskList(), l=len(getTaskList()),
                           weatherIcon=weatherIcon, weatherText=weatherText, weatherTemp=weatherTemp)


@app.route('/deltask', methods=['GET']) #Route to delete specific item of list
def remove_task():
    weatherTemp, weatherText, weatherIcon = getWeatherData()
    task_index = int(request.args.get('deltaskid'))
    tasklist = getTaskList()
    print(task_index)
    print(tasklist)
    if task_index < 0 or task_index > len(tasklist):
        return render_template('home.html', datetoday2=todayDateV2, tasklist=tasklist, l=len(tasklist),
                               mess='Invalid Index...',weatherIcon=weatherIcon, weatherText=weatherText, weatherTemp=weatherTemp)
    else:
        removed_task = tasklist.pop(task_index)
    updateTaskList(tasklist)
    return render_template('home.html', datetoday2=todayDateV2, tasklist=tasklist, l=len(tasklist), weatherIcon=weatherIcon, weatherText=weatherText, weatherTemp=weatherTemp)


#Run App
if __name__ == '__main__':
    app.run(debug=True)
