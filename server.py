from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO, emit
import time
import threading
timer_thread = None
app = Flask(__name__)
socketio = SocketIO(app)
settingData = {
    "home_team_score": 0,
    "visitor_team_score": 0,
    "home_team_score_2": 0,
    "visitor_team_score_2": 0,
    "totalscore_hometeam": 0,
    "totalscore_visitorteam": 0,
    "period_time_start_stop": False,
    "half":1,
    "game_name":"Game",
    "home_team_name":"Home Team",
    "visitor_team_name":"Opposition Team",
    "running_time":0,
    "period_time_minute":0,
    "period_time_second":0,
    "period_time_total":0,
    "background_color":"black",
    "gamename_color":"yellow",
    "hometeamname_color":"lightblue",
    "visitorteamname_color":"lightblue",
    "scores_color":"yellow",
    "timeofday_color":"red",
    "runningtime_color":"yellow",
}
@app.route('/')
def home():
    global settingData
    return render_template('index.html')

@app.route('/getInfo')
def getInfo():
    global settingData
    return jsonify(settingData)

@app.route('/control', methods=['GET'])
def control():
    global settingData
    action = request.args.get('action')
    if action == "point_plus":
        settingData['home_team_score_2'] += 1
        settingData['totalscore_hometeam'] +=1
    if action == "point_minus":
        if settingData['home_team_score_2']>0:
            settingData['home_team_score_2'] -= 1
            settingData['totalscore_hometeam'] -=1
    if action == "goal_plus":
        settingData['home_team_score'] += 1
        settingData['totalscore_hometeam'] += 3
    if action == "goal_minus":
        if settingData['home_team_score']>0:
            settingData['home_team_score'] -= 1
            settingData['totalscore_hometeam'] -= 3
    if action == "visitor_point_plus":
        settingData['visitor_team_score_2'] += 1
        settingData['totalscore_visitorteam'] +=1
    if action == "visitor_point_minus":
        if settingData['visitor_team_score_2']>0:
            settingData['visitor_team_score_2'] -= 1
            settingData['totalscore_visitorteam'] -=1
    if action == "visitor_goal_plus":
        settingData['visitor_team_score'] += 1
        settingData['totalscore_visitorteam'] += 3
    if action == "visitor_goal_minus":
        if settingData['visitor_team_score']>0:
            settingData['visitor_team_score'] -= 1
            settingData['totalscore_visitorteam'] -= 3
    if action == "period_time_start_stop":
        global timer_thread
        settingData['period_time_start_stop'] = not settingData['period_time_start_stop']
        
        if settingData['period_time_start_stop']:
            # Start the timer
            timer_thread = threading.Thread(target=run_timer)
            timer_thread.start()
        else:
            # Stop the timer
            settingData['period_time_start_stop'] = False
    if action == "half_plus":
        if settingData['half'] < 2:
            settingData['half'] += 1
            settingData['period_time_total'] = 0
            socketio.emit('time', {'time': 0})
    if action == "reset_clockbutton":
        if settingData['half'] < 2:
            settingData['half'] += 1
        settingData['period_time_total'] = 0
        socketio.emit('time', {'time': 0})
    if action == "half_minus":
        if settingData['half'] > 1:
            settingData['half'] -= 1
            settingData['period_time_total'] = 0
            socketio.emit('time', {'time': 0})
    if action == "game-name-color-box":
        settingData['gamename_color'] = request.args.get('data')
    if action == "home-team-color-box":
        settingData['hometeamname_color'] = request.args.get('data')
    if action == "visitor-team-color-box":
        settingData['visitorteamname_color'] = request.args.get('data')
    if action == "scores-color-box":
        settingData['scores_color'] = request.args.get('data')
    if action == "timeofday-color-box":
        settingData['timeofday_color'] = request.args.get('data')
    if action == "runningtime-color-box":
        settingData['runningtime_color'] = request.args.get('data')
    if action == "background-color-box":
        settingData['background_color'] = request.args.get('data')
    if action == "updateVisitorTeamName":
        if request.args.get('data') != "":
            settingData['visitor_team_name'] = request.args.get('data')
    if action == "updateHomeTeamName":
        if request.args.get('data') != "":
            settingData['home_team_name'] = request.args.get('data')
    if action == "updateGameName":
        settingData['game_name'] = request.args.get('data')
        settingData["home_team_score"] = 0
        settingData["visitor_team_score"] = 0
        settingData["home_team_score_2"] = 0
        settingData["visitor_team_score_2"] = 0
        settingData["totalscore_hometeam"] = 0
        settingData["totalscore_visitorteam"] = 0
        settingData["period_time_start_stop"] = False
        settingData["half"] = 1
        settingData["running_time"] = 0
        settingData["period_time_minute"] = 0
        settingData["period_time_second"] = 0
        settingData["period_time_total"] = 0
    if action == "updatePeriodHours":
        if request.args.get('data') != "":
            settingData['period_time_minute'] = request.args.get('data')
        # settingData['period_time_total'] = int(settingData['period_time_second']) + int(settingData['period_time_minute']) * 60
        # socketio.emit('time', {'time': settingData['period_time_total']})
    if action == "updatePeriodMinutes":
        if request.args.get('data') != "":
            settingData['period_time_second'] = request.args.get('data')
        # settingData['period_time_total'] = int(settingData['period_time_second']) + int(settingData['period_time_minute']) * 60
        # socketio.emit('time', {'time': settingData['period_time_total']})
    socketio.emit('settings', settingData)
    print(action, "action")
    return jsonify({'action': action})

@app.route('/newBoard', methods=['POST'])
def newBoard():
    global settingData
    settingData["home_team_score"] = 0
    settingData["visitor_team_score"] = 0
    settingData["home_team_score_2"] = 0
    settingData["visitor_team_score_2"] = 0
    settingData["totalscore_hometeam"] = 0
    settingData["totalscore_visitorteam"] = 0
    settingData["period_time_start_stop"] = False
    settingData["half"] = 1
    settingData["running_time"] = 0
    settingData["period_time_minute"] = 0
    settingData["period_time_second"] = 0
    settingData["period_time_total"] = 0
    
    return jsonify({'action': "new board"})

@app.route('/startNewGame', methods=['POST'])
def startNewGame():
    global settingData
    data = request.json
    settingData["home_team_score"] = 0
    settingData["visitor_team_score"] = 0
    settingData["home_team_score_2"] = 0
    settingData["visitor_team_score_2"] = 0
    settingData["totalscore_hometeam"] = 0
    settingData["totalscore_visitorteam"] = 0
    settingData["period_time_start_stop"] = False
    settingData["half"] = 1
    settingData["running_time"] = 0
    settingData["period_time_minute"] = 0
    settingData["period_time_second"] = 0
    settingData["period_time_total"] = 0
    settingData['game_name'] = data["game_name"]
    settingData['home_team_name'] = data["home_team_name"]
    settingData['visitor_team_name'] = data["visitor_team_name"]
    socketio.emit('settings', settingData)
    return jsonify({'message': 'Saved successfully!'})

@app.route('/saveTeamName', methods=['POST'])
def saveTeamName():
    data = request.json
    settingData['home_team_name'] = data["home_team_name"]
    settingData['visitor_team_name'] = data["visitor_team_name"]
    print(data)
    socketio.emit('settings', settingData)
    return jsonify({'message': 'Saved successfully!'})

@app.route('/savePeriodTime', methods=['POST'])
def savePeriodTime():
    global settingData
    data = request.json
    settingData['period_time_minute'] = data["minute"]
    settingData['period_time_second'] = data["second"]
    settingData['period_time_total'] = 0
    socketio.emit('time', {'time': settingData['period_time_total']})
    socketio.emit('settings', settingData)
    return jsonify({'message': 'Saved successfully!'})
def run_timer():
    global settingData
    while settingData['period_time_start_stop']> 0:
        send_time()
        time.sleep(1)

def send_time():
    global settingData
    total_second = settingData['period_time_total']
    settingData['period_time_total'] += 1
    # if settingData['period_time_total'] == (int(settingData['period_time_second']) + int(settingData['period_time_minute']) * 60)/2:
    #     settingData['half'] = 2
    #     socketio.emit('time', {'time': total_second})
    # else:
    socketio.emit('time', {'time': total_second})
    socketio.emit('settings', settingData)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2323)
