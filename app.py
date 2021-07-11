from flask import *
import pymysql
from passlib.hash import sha256_crypt
import random
import json
from math import *
from datetime import date, datetime, timedelta
import csv
from chatterbot import ChatBot
from chatterbot.response_selection import get_random_response
import random
import smtplib
#from chatterbot.trainers import ChatterBotCorpusTrainer
from botConfig import myBotName, chatBG, botAvatar, useGoogle, confidenceLevel

chatbotName = myBotName
print("Bot Name set to: " + chatbotName)
print("Confidence level set to " + str(confidenceLevel))

import logging
logging.basicConfig(level=logging.INFO)


connection = pymysql.connect(host="localhost",user="root",passwd="",database="wce-hack")
cursor = connection.cursor()

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

application = Flask(__name__)
application.secret_key = "wce"
@application.route("/")
def home():
    return render_template("index.html")

@application.route("/login", methods=['POST', 'GET'])
def login():
    return render_template("login.html")

@application.route("/signup")
def signup():
    return render_template("signup.html")

@application.route('/success')
def success():
    return render_template('index.html')
@application.route('/setagoal')
def setagoal():
    return render_template('setagoal.html')

@application.route('/doRegister',methods=['POST'])
def doRegister():
    if request.method == 'POST':
        entered_fname = request.form['first_name'].strip()
        entered_lname = request.form['last_name'].strip()
        entered_email = request.form['email'].strip()
        entered_password = request.form['password'].strip()
        entered_phone = request.form['phone'].strip()
        entered_dob = request.form['dob'].strip()

        sqlQuery = "SELECT `Email` FROM `users`"
        cursor.execute(sqlQuery)
        result = cursor.fetchall()
        for row in result:
            email = row[0]
            if entered_email == email:
                return redirect(url_for('login'))
            else:
                pass
        orgQuery = "INSERT INTO `users`(`f_name`, `l_name`, `email`, `password`, `phone_no`, `dob`) VALUES('{0}','{1}','{2}','{3}','{4}','{5}')".format(entered_fname, entered_lname, entered_email, sha256_crypt.hash(entered_password), entered_phone, entered_dob)
        cursor.execute(orgQuery)
        connection.commit()
        session['user'] = entered_email
    return redirect(url_for('success'))

@application.route('/checkLogin',methods=['GET', 'POST'])
def checkLogin():
    if request.method == 'POST':
        entered_email = request.form['email'].strip()
        entered_password = request.form['password'].strip()

        sqlQuery = "SELECT `email`, `password` FROM `users`"
        cursor.execute(sqlQuery)
        result = cursor.fetchall()
        for row in result:
            email = row[0]
            psw = row[1]
            if entered_email == email and sha256_crypt.verify(entered_password, psw):
                session['user'] = email
                return redirect(url_for('success'))
            else:
                pass
    return redirect(url_for('login'))

@application.route('/addCard',methods=['POST'])
def addCard():
	if session.get('user') is not None:
    
	    card_no = request.form['number'].strip()
	    card_no = card_no.replace(" ","");
	    exp_type = ['health', 'entertainment', 'meals', 'bills', 'others']
	    query1 = "UPDATE users SET card_no='{0}', card_type='{1}' where email='{2}'".format(card_no, "Credit", session['user'])
	    cursor.execute(query1)
	    query2 = "INSERT INTO expenses(card_no) VALUES('{0}')".format(card_no)
	    cursor.execute(query2)
	    connection.commit()
	    session["card_no"] = card_no
	    return redirect(url_for('addExpenses'))
	#return redirect(url_for('addExpenses'))

@application.route('/addExpenses')
def addExpenses():
	if session.get('card_no') is not None:
	    exp_type = ['health', 'entertainment', 'meals', 'bills', 'others']
	    card_no = session["card_no"]
	    res_json = {}
	    for j in range(0, 5):
	        exp_cost = []
	        exp_cost.append(random.randint(10000, 40000))
	        exp_cost.append(random.randint(1000, 5000))
	        exp_cost.append(random.randint(800, 1500))
	        exp_cost.append(random.randint(5000, 15000))
	        exp_cost.append(random.randint(3000, 12000))
	        res_json[months[j+3]] = {}
	        for i in range(0,len(exp_type)):
	            temp_date = "2021/" + str(j + 3) + "/01"
	            res_json[months[j + 3]][exp_type[i]] = exp_cost[i]
	    print(res_json)
	    res_json = json.dumps(res_json)
	    print(res_json)
	    expQuery = "UPDATE expenses SET expense_details='{0}' where card_no='{1}'".format(res_json, card_no)
	    cursor.execute(expQuery)
	    connection.commit()

	    return redirect(url_for('success'))

@application.route("/payment")
def payment():
    return render_template("payment.html")

def ageWiseSavings(age):
    if age<18:
        return [0.8, 0.2]
    elif age>=18 and age<35:
        return [0.7, 0.3]
    elif age>=35 and age<50:
        return [0.6, 0.4]
    elif age>=50 and age<60:
        return [0.4, 0.6]
    elif age>=60:
        return [0.3, 0.7]


@application.route("/personalBudget", methods=['GET', 'POST'])
def personalBudget():
    #if request.method=='POST':
        monthly_income = int(request.form['monthly_income'])
        EMI = 500 #request.form['emi']
        future_goals = 'B'  # request.form['future-goals']
        age = int(request.form['age'])
        priority = 4 # request.form['priority']

        future_goals_type = {
            'A': "Stable Life",
            'B': "Save More",
            'C': "Spend Lavishly"
        }

        total = monthly_income - EMI
        num_char = ["Healthcare", "Entertainment", "Food", "Bills", "Transportation", "Child Expenses"]

        res_obj = {
            'emergency': 0,
            'investment': 0,
            'miscellaneous': 0
        }

        res_obj['miscellaneous'] = total * 0.1

        if future_goals=='A':
            savings = total * 0.25
            res_age = ageWiseSavings(age)
            res_obj['investment'] = savings * res_age[0]
            res_obj['emergency'] = savings * res_age[1]
        elif future_goals=='B':
            savings = total * 0.35
            res_age = ageWiseSavings(age)
            res_obj['investment'] = savings * res_age[0]
            res_obj['emergency'] = savings * res_age[1]
        elif future_goals=='C':
            savings = total * 0.10
            res_age = ageWiseSavings(age)
            res_obj['investment'] = savings * res_age[0]
            res_obj['emergency'] = savings * res_age[1]

        total_completed = 0.0
        for key in res_obj:
            total_completed += res_obj[key]

        total -= total_completed

        print(res_obj)

        priority_division = {
            "2": ["55", "45"],
            "3": ["50", "30", "20"],
            "4": ["35", "30", "20", "15"],
            "5": ["30", "25", "20", "15", "10"],
            "6": ["30", "25", "20", "10", "9", "6"]
        }


        res_obj['priority'] = {}
        for i in range(int(priority)):
            res_obj['priority'][num_char[i]] = total * int(priority_division[str(priority)][i])/100


        res_obj['monthlyIncome'] = monthly_income
        res_obj['EMI'] = EMI
        res_obj['future_goals'] = future_goals_type[future_goals],
        res_obj['age'] = age

        print(res_obj)
        return render_template("budget_result.html", data = res_obj)

def closest(list, Number):
    aux = []
    for valor in list:
        #print(Number, valor[-1])
        aux.append(abs(Number-float(valor[-1])))

    return aux.index(min(aux))

@application.route('/investmentPlanner',methods=['GET', 'POST'])
def investmentPlanner():
    #if request.method=='POST':
	    #email = request.form["email"].strip()
	    amt_to_save = int(request.form["total_number_of_donors_in_year_1"].strip())
	    tenure = int(request.form["average_gift_size_in_year_1"].strip())
	    upfront_amt = int(request.form["total_number_of_donors_in_year_2"].strip())
	    if amt_to_save < upfront_amt:
	        return "<h1> Amount to save less than upfront investment </h1>"
	    X = amt_to_save - upfront_amt
	    Y = (X/(tenure * 12))
	    inflation_amt = amt_to_save + (amt_to_save *0.05 *3)

	    with open('data/funds_data.csv') as csv_file:
	        csv_reader = csv.reader(csv_file)
	        line_count = 0
	        lst = []
	        for row in csv_reader:
	            row = list(row)
	            if line_count == 0:
	                line_count += 1
	            else:
	                lst.append(row)

	    #print(lst)
	    lst.sort(key=lambda x: float(x[-1]))
	    debt_lst = list(n for n in lst if n[2][0:4] == 'Debt')
	    equi_lst = list(n for n in lst if n[2][0:4] == 'Equi')
	    hybrid_lst = list(n for n in lst if n[2][0:4] == 'Hybr')
	    other_lst = list(n for n in lst if n[2][0:4] == 'Othe')

	    res_funds = []
	    rate = 0.0
	    if Y <= 1000:
	        myrate = 8.0
	        x = closest(debt_lst, myrate)
	        res_funds.append(debt_lst[x])
	        rate += float(debt_lst[x][-1])
	        montly_rate_of_return = ((rate / 100) / 12)
	        SIP = round(X / (((pow(1 + montly_rate_of_return, tenure * 12) - 1) / montly_rate_of_return) * (
	                1 + montly_rate_of_return)))
	        res_funds[0].append(1* upfront_amt)
	        res_funds[0].append(str(SIP))
	    elif Y > 1000 and Y <= 2500:
	        myrate = 9.5
	        x = closest(hybrid_lst, myrate)
	        res_funds.append(hybrid_lst[x])
	        rate += float(hybrid_lst[x][-1])

	        x = closest(debt_lst, myrate)
	        rate += float(debt_lst[x][-1])
	        res_funds.append(debt_lst[x])
	        del debt_lst[x]
	        x = closest(debt_lst, myrate)
	        rate += float(debt_lst[x][-1])
	        res_funds.append(debt_lst[x])
	        rate /= 3
	        res_funds.sort(key=lambda x: abs(myrate - float(x[-1])))
	        montly_rate_of_return = ((rate / 100) / 12)
	        SIP = round(X / (((pow(1 + montly_rate_of_return, tenure * 12) - 1) / montly_rate_of_return) * (
	                1 + montly_rate_of_return)))
	        res_funds[0].append(0.45*upfront_amt)
	        res_funds[0].append(str(SIP))
	        res_funds[1].append(0.35 * upfront_amt)
	        res_funds[1].append("-")
	        res_funds[2].append(0.25 * upfront_amt)
	        res_funds[2].append("-")
	    elif Y > 2500 and Y <= 5000:
	        myrate = 10.6
	        x = closest(equi_lst, myrate)
	        res_funds.append(equi_lst[x])
	        rate += float(equi_lst[x][-1])

	        x = closest(debt_lst, myrate)
	        rate += float(debt_lst[x][-1])
	        res_funds.append(debt_lst[x])
	        del debt_lst[x]
	        x = closest(debt_lst, myrate)
	        rate += float(debt_lst[x][-1])
	        res_funds.append(debt_lst[x])
	        rate /= 3
	        res_funds.sort(key=lambda x: abs(myrate - float(x[-1])))
	        montly_rate_of_return = ((rate / 100) / 12)
	        SIP = round(X / (((pow(1 + montly_rate_of_return, tenure * 12) - 1) / montly_rate_of_return) * (
	                    1 + montly_rate_of_return)))
	        res_funds[0].append(0.45 * upfront_amt)
	        res_funds[0].append(str(SIP))
	        res_funds[1].append(0.35 * upfront_amt)
	        res_funds[1].append("-")
	        res_funds[2].append(0.25 * upfront_amt)
	        res_funds[2].append("-")
	    elif Y > 5000 and Y <= 10000:
	        myrate = 11.8
	        x = closest(equi_lst, myrate)
	        res_funds.append(equi_lst[x])
	        rate += float(equi_lst[x][-1])
	        x = closest(debt_lst, myrate)
	        res_funds.append(debt_lst[x])
	        rate += float(debt_lst[x][-1])

	        x = closest(hybrid_lst, myrate)
	        rate += float(hybrid_lst[x][-1])
	        res_funds.append(hybrid_lst[x])
	        del hybrid_lst[x]
	        x = closest(hybrid_lst, myrate)
	        rate += float(hybrid_lst[x][-1])
	        res_funds.append(hybrid_lst[x])
	        rate /= 4
	        res_funds.sort(key=lambda x: abs(myrate - float(x[-1])))
	        montly_rate_of_return = ((rate / 100) / 12)
	        SIP = round(X / (((pow(1 + montly_rate_of_return, tenure * 12) - 1) / montly_rate_of_return) * (
	                1 + montly_rate_of_return)))
	        res_funds[0].append(0.40 * upfront_amt)
	        res_funds[0].append(str(SIP))
	        res_funds[1].append(0.25 * upfront_amt)
	        res_funds[1].append("-")
	        res_funds[2].append(0.20 * upfront_amt)
	        res_funds[2].append("-")
	        res_funds[3].append(0.15 * upfront_amt)
	        res_funds[3].append("-")
	    elif Y > 10000:
	        myrate = 12.6
	        x = closest(debt_lst, myrate)
	        res_funds.append(debt_lst[x])
	        rate += float(debt_lst[x][-1])

	        x = closest(hybrid_lst, myrate)
	        rate += float(hybrid_lst[x][-1])
	        res_funds.append(hybrid_lst[x])
	        del hybrid_lst[x]
	        x = closest(hybrid_lst, myrate)
	        rate += float(hybrid_lst[x][-1])
	        res_funds.append(hybrid_lst[x])

	        x = closest(equi_lst, myrate)
	        res_funds.append(equi_lst[x])
	        rate += float(equi_lst[x][-1])
	        del equi_lst[x]
	        x = closest(equi_lst, myrate)
	        rate += float(equi_lst[x][-1])
	        res_funds.append(equi_lst[x])
	        rate /= 5
	        res_funds.sort(key=lambda x: abs(myrate - float(x[-1])))
	        montly_rate_of_return = ((rate / 100) / 12)
	        SIP = round(X / (((pow(1 + montly_rate_of_return, tenure * 12) - 1) / montly_rate_of_return) * (
	                1 + montly_rate_of_return)))
	        res_funds[0].append(0.35 * upfront_amt)
	        res_funds[0].append(str(SIP))
	        res_funds[1].append(0.25 * upfront_amt)
	        res_funds[1].append("-")
	        res_funds[2].append(0.20 * upfront_amt)
	        res_funds[2].append("-")
	        res_funds[3].append(0.11 * upfront_amt)
	        res_funds[3].append("-")
	        res_funds[4].append(0.9 * upfront_amt)
	        res_funds[4].append("-")

	    print("xD")

	    print(res_funds)
	    print(rate)
	    res_invest = {}
	    res_invest["funds_list"] = res_funds
	    res_invest["tenure"] = tenure
	    res_invest["upfront"] = upfront_amt
	    res_invest["inflation"] = inflation_amt
	    res_invest["SIP"] = SIP
	    #rate = (rate/100)
	    #montly_rate_of_return = ((rate/100)/12)
	    # total_money_invested = rate * tenure*12
	    # safety_net = upfront_amt * rate
	    print("<h1> {0} | {1} | {2} | {3} | {4} | {5}</h1>".format(X, Y, rate, montly_rate_of_return, SIP, inflation_amt))
	    return render_template("investment_result.html", data=res_invest)



@application.route("/forum", methods=['GET', 'POST'])
def forum():
	return render_template("search.html")

@application.route("/budgetForm", methods=['GET', 'POST'])
def budgetForm():
	return render_template("budget.html")


@application.route("/goalsForm", methods=['GET', 'POST'])

def goalsForm():
	return render_template("goals.html")

@application.route("/home", methods=['GET', 'POST'])

def homee():
	return render_template("index.html")

@application.route("/chatbot")
def chatbot():
    return render_template("chatbot_index.html", botName = chatbotName, chatBG = chatBG, botAvatar = botAvatar)

@application.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    botReply = str(bot.get_response(userText))
    if botReply is "IDKresponse":
        botReply = str(bot.get_response('IDKnull'))
        if useGoogle == "yes":
            botReply = botReply + tryGoogle(userText)
    elif botReply == "getTIME":
        botReply = getTime()
        print(getTime())
    elif botReply == "getDATE":
        botReply = getDate()
        print(getDate())
    
    elif botReply.find("http") != -1:
        print("done")
        print(botReply.find("http"))
        endstring = botReply[botReply.find("http"):]
        print(endstring)
        botReply = link(endstring)
    return botReply

@app.route("/getOTP")
def getOTP():
	import smtplib

	smtp_ssl_host = 'smtp.gmail.com'
	smtp_ssl_port = 465


	Email = config.EMAIL
	Pass = config.PASSWORD

	from_addr = Email
	to_addrs = request.form["to"]
	subject = "OTP For PaisaPlanner"
	emailMessage = "Your PaisaPlanner OTP is " + otp


	message = MIMEText(emailMessage)
	message['subject'] = "OTP For PaisaPlanner"
	message['from'] = from_addr
	message['to'] = to_addrs 


	server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)

	server.login(Email, Pass)
	server.sendmail(from_addr, to_addrs, message.as_string())
	server.quit()

	return redirect(url_for('valOTP'))



if __name__ == "__main__":
    application.run(debug='True')
    #application.run(host='0.0.0.0', port=5000)