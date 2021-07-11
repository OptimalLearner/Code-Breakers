from flask import *
import pymysql
from passlib.hash import sha256_crypt
import random
import json
from math import *
from datetime import date, datetime, timedelta
import csv

app = Flask(__name__)
app.secret_key = "wce"
app.config['JSON_SORT_KEYS'] = True

connection = pymysql.connect(host="localhost",user="root",passwd="",database="wce-hack")
cursor = connection.cursor()

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

@app.route('/')
@app.route('/login')
def loginPage():
    return render_template('login.html')

@app.route('/success')
def success():
    return render_template('main.html')

@app.route('/register')
def registerPage():
    return render_template('register.html')

@app.route('/checkLogin',methods=['POST'])
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

@app.route('/doRegister',methods=['POST'])
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

@app.route("/searchPage", methods=['GET', 'POST'])
def searchPage():
    return render_template('search-page.html')

@app.route('/addCard')
def addCard():
    card_no = '9876432112346789'
    exp_type = ['health', 'entertainment', 'meals', 'bills', 'others']
    query1 = "UPDATE users SET card_no='{0}', card_type='{1}' where email='{2}'".format(card_no, "Credit", session['user'])
    cursor.execute(query1)
    query2 = "INSERT INTO expenses(card_no) VALUES('{0}')".format(card_no)
    cursor.execute(query2)
    connection.commit()
    return '<h1> Card Details Added! </h1>'

@app.route('/addExpenses')
def addExpenses():
    exp_type = ['health', 'entertainment', 'meals', 'bills', 'others']
    card_no = '9876432112346789'
    res_json = {}
    for j in range(0, 5):
        exp_cost = []
        exp_cost.append(random.randint(10000, 40000))
        exp_cost.append(random.randint(1000, 5000))
        exp_cost.append(random.randint(800, 1500))
        exp_cost.append(random.randint(5000, 15000))
        exp_cost.append(random.randint(3000, 12000))
        res_json[months[j+2]] = {}
        for i in range(0,len(exp_type)):
            temp_date = "2021/" + str(j + 2) + "/01"
            res_json[months[j + 2]][exp_type[i]] = exp_cost[i]
    print(res_json)
    res_json = json.dumps(res_json)
    print(res_json)
    expQuery = "UPDATE expenses SET expense_details='{0}' where card_no='{1}'".format(res_json, card_no)
    cursor.execute(expQuery)
    connection.commit()

    return '<h1> Data Entered </h1>'

@app.route('/getTotalMonthCost',methods=['GET', 'POST'])
def getTotalMonthCost():
        if session.get('user') == False:
            return redirect(url_for('login'))

    #if request.method=='POST':
        startMonth = 'June' #request.form['first-month']
        month_index = months.index(startMonth)
        date_formed = "2021/"+ str(month_index+2)+"/01"
        print("Date: "+date_formed)
        card_no = ''
        result_exp = ''
        query1 = "SELECT card_no from users where email='{0}'".format(session['user'])
        cursor.execute(query1)
        result = cursor.fetchall()
        for row in result:
            card_no = row[0]

        print('Card: '+card_no)

        query2 = "SELECT expense_details FROM expenses where card_no='{0}'".format(card_no);
        cursor.execute(query2)
        result = cursor.fetchall()
        for row in result:
            result_exp = row[0]

        result_exp = json.loads(result_exp)
        res_cost = {}
        for i in range(5):
            c = 0
            for key, value in result_exp[months[i+2]].items():
                c += value
            res_cost[months[i+2]] = c

        print(res_cost)

        return render_template("chart_demo.html", res_cost = res_cost)

@app.route('/getTotalTypeCost',methods=['GET', 'POST'])
def getTotalTypeCost():
    #if request.method=='POST':
        exp_type = 'health' #request.form['first-month']
        card_no = ''
        result_exp = ''
        query1 = "SELECT card_no from users where email='{0}'".format(session['user'])
        cursor.execute(query1)
        result = cursor.fetchall()
        for row in result:
            card_no = row[0]

        print('Card: '+card_no)

        query2 = "SELECT expense_details FROM expenses where card_no='{0}'".format(card_no);
        cursor.execute(query2)
        result = cursor.fetchall()
        for row in result:
            result_exp = row[0]


        result_exp = json.loads(result_exp)
        res_cost = 0
        for key, value in result_exp.items():
            print(key, value)
            res_cost += value[exp_type]

        return '<h1> {0} </h1>'.format(res_cost)

@app.route('/getSavingsDiff', methods=['GET', 'POST'])
def getSavingsDiff():
    # if request.method=='POST':
        start_date = 'June'  # request.form['first-month']
        end_date = 'July'  # request.form['first-month']
        card_no = ''

        query1 = "SELECT card_no from users where email='{0}'".format(session['user'])
        cursor.execute(query1)
        result = cursor.fetchall()
        for row in result:
            card_no = row[0]

        print('Card: ' + card_no)
        result_json = {}
        query2 = "SELECT expense_details FROM expenses where card_no='{0}'".format(card_no);
        cursor.execute(query2)
        result = cursor.fetchall()
        for row in result:
            result_json = row[0]

        result_json = json.loads(result_json)
        result_exp_start = 0
        for key, value in result_json[start_date].items():
            result_exp_start += value

        result_exp_end = 0
        for key, value in result_json[end_date].items():
            result_exp_end += value

        return '<h1> {0} </h1>'.format((int(result_exp_end) - int(result_exp_start)))

# @app.route('/getT',methods=['GET', 'POST'])
# def getT():
#     #if request.method=='POST':
#         start_date = 'June' #request.form['first-month']
#         end_date = 'July'  # request.form['first-month']
#         exp_type = 'all' #request.form['exp_type']
#         if exp_type=='all':
#             exp_type = '*'
#         card_no = ''
#         result_exp = ''
#         query1 = "SELECT card_no from users where email='{0}'".format(session['user'])
#         cursor.execute(query1)
#         result = cursor.fetchall()
#         for row in result:
#             card_no = row[0]
#
#         print('Card: '+card_no)
#
#         query2 = "SELECT sum(expense_cost) FROM expenses where card_no='{0}' and expenses_type='{1}'".format(card_no, exp_type);
#         cursor.execute(query2)
#         result = cursor.fetchall()
#         for row in result:
#             result_exp = row[0]
#         return '<h1> {0} </h1>'.format(result_exp)

def closest(list, Number):
    aux = []
    for valor in list:
        #print(Number, valor[-1])
        aux.append(abs(Number-float(valor[-1])))

    return aux.index(min(aux))

@app.route('/investmentPlanner',methods=['GET', 'POST'])
def investmentPlanner():
    # if request.method=='POST':
    amt_to_save = 100000 #request.form["amt-to-save"]
    tenure = 3 # request.form["tenure"] #in years
    upfront_amt = 10000 #request.form["upfront-amt"]
    if amt_to_save < upfront_amt:
        return "<h1> Amount to save less than upfront investment </h1>"
    X = amt_to_save - upfront_amt
    Y = (X/(tenure * 12))
    inflation_amt = amt_to_save + (amt_to_save *0.05 *3)

    with open('data_file.csv') as csv_file:
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

# def sip(investment, tenure, interest, amount=0, is_year=True, is_percent=True, show_amount_list=True):
#     tenure = tenure*12 if is_year else tenure
#     interest = interest/100 if is_percent else interest
#     interest /= 12
#     amount_every_month = {}
#     for month in range(tenure):
#         amount = (amount + investment)*(1+interest)
#         amount_every_month[month+1] = amount
#     return {'Amount @ Maturity': amount, 'Amount every month': amount_every_month} if show_amount_list else {'Amount @ Maturity': amount}
#
# x=sip(2102,3,11)
# print(x)

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

@app.route("/personalBudget", methods=['GET', 'POST'])
def personalBudget():
    #if request.method=='POST':
        monthly_income = 10000 #request.form['monthly-income']
        EMI = 500 #request.form['emi']
        future_goals = 'B'  # request.form['future-goals']
        age = 28 # request.form['age']
        priority = 4 # request.form['priority']

        future_goals_type = {
            'A': "Stable Life",
            'B': "Save More",
            'C': "Spend Lavishly"
        }

        total = monthly_income - EMI
        num_char = ["first", "second", "third", "fourth", "fifth", "sixth"]

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

@app.route("/demo")
def demo():
    import requests
    response = requests.get("https://api.mfapi.in/mf")
    json_data = response.json()
    json_data[0]

    schemeCode = list(map(lambda x: x['schemeCode'], json_data))
    schemeCode[0]
    list_of_schemes = []
    for code in range(0, 20):
        print(code)
        response1 = requests.get(f"https://api.mfapi.in/mf/{schemeCode[code]}")
        json_data1 = response1.json()
        date = list(map(lambda x: x['date'], json_data1['data']))
        if (date[0].find('2021') != -1):
            json_data1['data']
            list_of_schemes.append(json_data1['meta'])

    list_of_schemes = json.dumps(list_of_schemes)

    with open('templates/demo.json') as json_file:
        data = json.load(json_file)

    employee_data = data['intent']
    data_file = open('data_file_2.csv', 'w')

    csv_writer = csv.writer(data_file)
    count = 0

    for emp in employee_data:
        print(emp)
        if count == 0:
            header = emp.keys()
            csv_writer.writerow(header)
            count += 1

        csv_writer.writerow(emp.values())

    data_file.close()


    return "<h1> {0} </h1>".format("Done")


@app.route("/demoQ")
def demoQ():
    import requests
    with open('data_file.csv') as csv_file:
        csv_reader = csv.reader(csv_file)
        line_count = 0
        lst = []
        lst2 = []
        for row in csv_reader:
            row = list(row)
            if line_count == 0:
                line_count += 1
                pass
            else:
                mycode = row[3]
                response1 = requests.get(f"https://api.mfapi.in/mf/{mycode}")
                json_data1 = response1.json()
                first = 0
                second = 0
                for code in json_data1['data']:
                    if (code['date'] == '09-07-2021'):
                        first = code['nav']
                    elif(code['date']=='09-07-2018'):
                        second = code['nav']
                        break
                lst.append(str(float(first) - float(second)))
                lst2.append(first)

        print(lst)
        print(lst2)
        return "<h1> Done! </h1>"
if __name__ == '__main__':
    app.run(debug=True)