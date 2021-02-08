import pymysql
import random
from flask import Flask,render_template,request,send_from_directory
from werkzeug.utils import secure_filename
import os
import time
import json
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import re
import yagmail
import smtplib
import imaplib
import email
from textblob import TextBlob
from textblob.classifiers import NaiveBayesClassifier
import numpy as np
from PIL import Image,ImageDraw
from ibm_watson import VisualRecognitionV4
from watson_developer_cloud import VisualRecognitionV3
from ibm_watson.visual_recognition_v4 import AnalyzeEnums, FileWithMetadata
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
app=Flask(__name__,template_folder='templates')
english_bot = ChatBot("Chatterbot",storage_adapter="chatterbot.storage.SQLStorageAdapter")
trainer = ChatterBotCorpusTrainer(english_bot)
#training chatbot 
trainer.train(r"C:\Users\sushma\AppData\Local\Programs\Python\Python38\Scripts\Inframind\data\claimProcedure.yml")
trainer.train(r"C:\Users\sushma\AppData\Local\Programs\Python\Python38\Scripts\Inframind\data\modify.yml")
trainer.train(r"C:\Users\sushma\AppData\Local\Programs\Python\Python38\Scripts\Inframind\data\Transfer.yml")
trainer.train(r"C:\Users\sushma\AppData\Local\Programs\Python\Python38\Scripts\Inframind\data\greet.yml")
trainer.train(r"C:\Users\sushma\AppData\Local\Programs\Python\Python38\Scripts\Inframind\data\FAQ.yml")
trainer.train(r"C:\Users\sushma\AppData\Local\Programs\Python\Python38\Scripts\Inframind\data\Handoff.yml")
path=r'C:\Users\sushma\AppData\Local\Programs\Python\Python38\Scripts\Inframind\static\\'
img_path=r'C:\Users\sushma\AppData\Local\Programs\Python\Python38\Scripts\Inframind\static\Req.jpeg'
def Estimation(k):
    #estimation cost 
    Estimate={"Bumper":3000,"Dent":2000,"Dome":15000,"Door":10000,"Light":1800,"Glass_Break":2000}
    s=0 
    Parts={}
    for j in k:
       s+=Estimate[j]
       Parts.update({j:Estimate[j]})
    Parts.update({"Scaled Total":s})
    return Parts #dictionary of damaged parts & its cost
def database_connection(PolicyId,status,image):
   con=pymysql.connect(host="localhost",user="root",password="",database="insurance")#database connection
   cursor=con.cursor()
   qu="select Policy_Amount,Status_Claim from claimdata where PolicyId="+PolicyId+";"
   cursor.execute(qu)#extracting data from database
   Am=cursor.fetchall()
   con.commit()
   if status=="Accepted" and (Am):
       image_path=path+image
      # up_image="Insert into claimdata(Damaged_Image) value(1,LOAD_FILE("+image_path+")) where PolicyId="+PolicyId+";"
       #cursor.execute(up_image)
       up_status="update claimdata set Status_Claim=1 where PolicyId="+str(PolicyId)+";" #updating claim status
       cursor.execute(up_status)
   con.commit()
   con.close()
   if Am[0][1]==1: #claim check
       return 0
   else:
       s=Am[0][0] # Policy Amount 
       return (int(s[0]))
pos_prob=[]
senti=[]
val=[]
train=[('I love this policy','pos'),('I didn"t get the correct answer for my question','neg'),('okay','pos'),('Need help','pos'),('Ít"s not the way to treat','neg'),('view my details',"pos"),("Best application","pos"),("I don't like it",'neg'),('your answering is bad','neg'),('best','pos'),('Not upto mark','neg'),('Could be more better','neg'),("It's good",'pos'),('It given wrong results','neg'),('Results were not acurate','neg'),('helpful','pos'),('not helpful','neg'),(' very advantageous','pos'),("It's disgusting",'neg'),("Hi",'pos'),('hello','pos'),('How to claim','pos'),('what is IDV','pos'),('so long to reply','neg'),('not worthy','neg'),('worthy and helpful','pos'),('update my details','pos'),('Time taking','neg'),("worse results",'neg'),('not good','neg'),('Modify policy','pos'),('This bot is not good','neg'),("hate",'neg'),( " my policy id",'pos'),("we regret to inform",'neg'),("easy and simple",'pos'),("hard and complex",'pos'),("My car is damaged",'neg'),("better results",'pos'),('sorry for inconvenience','neg'),("time taking",'neg'),("time consuming",'neg'),("bad",'neg'),("worst results","neg"),("wrong output","neg")]
#sentimental analysis of conversation training data
c1=NaiveBayesClassifier(train)#training 
def train(Text):
    global pos_prob,c1,senti,val
    ans=c1.prob_classify(Text)
    pos_prob.append(ans.prob('pos'))
    senti.append(c1.classify(Text))
    val.append(len(senti))
    if len(senti)<2:
        return False
    else:
        if senti[-1]=="neg" and senti[-2]=='neg':#checking 2 consecutive negative impulse from customer then human handoff
            return True
        else:
             return False
def database(PolicyID):  
     con=pymysql.connect(host="localhost",user="root",password="",database="insurance")
     cursor=con.cursor()
     req_Det="select Policy_Amount,PolicyName,start_Date,End_Date,Status_Claim from  claimdata where PolicyId="+str(PolicyID)+";"
     cursor.execute(req_Det)
     Details=cursor.fetchall()
     con.commit()
     con.close()
     return Details
def receive():
   mail = imaplib.IMAP4_SSL('imap.gmail.com')
   mail.login('insurancebheema@gmail.com', 'inframind')
   mail.list()
   mail.select("inbox") # connecting to inbox.
   result, data = mail.search(None, "ALL")#filtering emails
   ids = data[0] # data is a list.
   id_list = ids.split() # ids is a space separated string
   latest_email_id =id_list[-1] # get the latest
   result, data = mail.fetch(latest_email_id, "(RFC822)") 
   for response_part in data:
       if isinstance(response_part,tuple):
           message=email.message_from_bytes(response_part[1])
           if message.is_multipart():
               mail_content=''
               for part in message.get_payload():
                   if part.get_content_type()=='text/plain':
                       mail_content+=part.get_payload()
           else:
               mail_content=message.get_payload()
           return (mail_content)
def send(txt): 
  yag=yagmail.SMTP(user="insurancebheema@gmail.com",password="inframind")#Email connection
  yag.send("sushmapitti45@gmail.com","User Query",txt) #sending email
i=0
conv={}
Data=()
@app.route("/get")
def get_bot_response():
     userText = request.args.get("msg")#User Query in chatbot
     userText=userText.lower()
     global i,conv,Data
     res=train(userText)
     Data=database(polid)
     #Database checking from the userInput 
     handoff=["sure","yes,connect it","okay","ok","yup","ok,make it fast","done"]
     date=["start date","policy starts","date of commencement"]
     Am=["policy amount","amount","My idv","total amount","policy value"]
     close=["close date","end date","last date","ends at"]
     view=["view","show my policy details","display my policy","details about my policy","policy information"]
     tot=handoff+date+Am+close+view 
     if (userText) in tot:
       for d in date:
        if d in userText:
          return ("Your policy start date is "+str(Data[0][3]))
       for i in Am:
        if i in userText:
          return ("Your IDV is "+Data[0][0])
       for cl in close:
        if cl in userText:
          return ("Your policy ends at "+str(Data[0][4]))
       for vi in view:
        if vi in userText:
          return ("IDV - "+Data[0][0]+"</p><p class='botText'><span>Start Date - "+str(Data[0][2])+"<span></p><p class='botText'><span>End Date - "+str(Data[0][3])+"</span></p><p class='botText'><span> Status Claim -"+str(Data[0][4]))
     for x in handoff:
        if (x in userText) or (i==1) or res :
          send(userText)
          time.sleep(20)# time setting for agent to reply
          s=receive()
          i=1
          conv.update({userText:s})# convo update-storage for next sentiment analysis
          return s
     resp=str(english_bot.get_response(userText))
     if len(resp)>30 and len(resp)<60:
         r=len(resp[:30].rsplit(' ', 1)[0])
         response=resp[:r]+"</span></p><p class='botText'><span>"+resp[r:] #response multiline making
     elif(len(resp)>60):
         r=len(resp[:30].rsplit(' ', 1)[0])
         response=resp[:r]+"</span></p><p class='botText'><span>"+resp[r:60]+"</span></p><p class='botText'><span>"+resp[60:]
     else:
         response=resp[:]
     conv.update({userText:response})
     return response #bot response
@app.route('/login')
def login():
    return render_template("login.html") #rendering login details
@app.route('/Claim_Request',methods=['GET','POST'])
def Claim_Request():
    global polid
    if request.method=="POST":
        username=request.form['UserName']
        passw=request.form['PassWord']#Getting user details for validation
        con=pymysql.connect(host="localhost",user="root",password="",database="insurance")
        cursor=con.cursor()
        req_Det="select PolicyId  from  %s  where UserName=%%s AND Password=%%s""" %("claimdata",)
        cursor.execute(req_Det,((username,passw)))
        Details=cursor.fetchall()
        if not Details:
            return "<script>alert('password is incorrect');</script>" 
        polid=Details[0][0]
    return render_template('Claim_Form.html',pid=polid)
def detection(img_path):
    global severity_Class
    severity_Class=""
    severity = VisualRecognitionV3(version='2019-02-11', iam_apikey='qCsWsFfybkglG76TBdjwqYEr3bkD2lHv-Aihok8e3yht')
    try:
      with open(img_path, 'rb') as images_file:
       classes =severity.classify(images_file,threshold='0.6',classifier_ids='severityclassify_705178400').get_result()
       severity_Class=(((((((classes["images"])[0])['classifiers'])[0])['classes'])[0])['class'])
    except:
        return {}
    authenticator = IAMAuthenticator('50qOrFZOconfI30gPSNJ2Z5hDYmANuAft0Riu5fD__CT')#watson visual recognition model
    visual_recognition = VisualRecognitionV4(version='2019-02-11',authenticator=authenticator)
    visual_recognition.set_service_url('https://api.us-south.visual-recognition.watson.cloud.ibm.com/instances/5dfa5dd9-abf6-4768-82ea-a19f68dd475a')
    try:
      with  open(img_path, 'rb') as dice_file:
        result = visual_recognition.analyze(collection_ids=["5393993e-9c07-4939-abf5-622539267e8d"],
        features=[AnalyzeEnums.Features.OBJECTS.value],
        images_file=[FileWithMetadata(dice_file)],threshold=0.15).get_result()
        k=result['images']
        t=((k[0])["objects"])
        s=t["collections"]
        z=((s[0])['objects'])
        img_analysis={}
        for i in z:
            a,b=i['object'],i['location']
            img_analysis.update({a:b})#Model result-Damaged parts and its location
        return img_analysis 
    except:
        return {}       
@app.route('/Request_Result',methods=['GET','POST'])
def Request_Result(): 
    if request.method == 'POST':
        f=request.files['Image']
        p=request.form['policy_id']
        f.save(os.path.join(app.root_path,img_path)) #damaged image saving
        analy=detection(img_path)
        if len(analy)==0:
            status="Rejected"
        else:
            status="Accepted"
        im=Image.open(img_path)
        img1=ImageDraw.Draw(im) #location of damaged part drawing
        color=["red","blue","green","yellow","white"]
        m=0
        for i in analy.values():
            img1.rectangle(((i['left'],i['top']),((i['left']+i['width']),(i['top']+i['height']))),fill=None,outline=color[m],width=3)
            m=m+1
        new_name="Result"+str(time.time())+".jpeg"
        for filename in os.listdir((path)):
            if filename.startswith('Result_'):
                os.remove(path+filename)
        im.save(r'C:\Users\sushma\AppData\Local\Programs\Python\Python38\Scripts\Inframind\static\\'+ new_name)#Damaged vehicle with location image save
        policy_am=database_connection(p,status,new_name)
        if policy_am==0:
           return "<h1>Claim Completed</h1>"
        Result=Estimation(analy.keys())
        total=(Result["Scaled Total"]+policy_am)*0.5
        if severity_Class=="Severe_Damage":
            total=total*4
        elif(severity_Class=="Moderate_Damage"):
            total=total*3
        elif(severity_Class=="Minor_Damage"):
            total=total*2
        Result["Scaled Total"]=total #estimating scaled total
        return render_template("Request_Result.html",name=new_name,result=Result,Status=status,intensity=severity_Class)#
app.run(host='localhost', port=5000) 

