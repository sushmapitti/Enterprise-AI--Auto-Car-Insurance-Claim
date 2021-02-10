from textblob.classifiers import NaiveBayesClassifier
pos_prob=[]
senti=[]
val=[]
train=[('I love this policy','pos'),
("Hii","pos"),
("hello everyone","pos"),
("hi all","pos"),
("yup","pos"),
("yeah","pos"),
("okay","pos"),
("okk I like it","pos"),
("ok","pos"),
("show me details","pos"),
("view my details","pos"),
("show policy details","pos"),
("can I view my policy details","pos"),
("Great application","pos"),
("Helloo","pos"),
("I need modifations","pos"),
("I want to change my details","pos"),
("I want to edit my details","pos"),
("view my policy details","pos"),
("Best experience","pos"),
("what is IDV","pos"),
("what is NBC","pos"),
("connect with me an agent","pos"),
("talk to an agent","pos"),
("need an agent to talk","pos"),
('I didn"t get the correct answer for my question','neg'),
('okay','pos'),
('Need help','pos'),
('Ít"s not the way to treat','neg'),
('view my details',"pos"),
("Best application","pos"),
("I don't like it",'neg'),
('your answering is bad','neg'),
('best','pos'),
('Not upto mark','neg'),
('Could be more better','neg'),
("It's good",'pos'),
('It given wrong results','neg'),
('Results were not acurate','neg'),
('helpful','pos'),
('not helpful','neg'),
(' very advantageous','pos'),
("It's disgusting",'neg'),
("Hi",'pos'),
('hello','pos'),
('How to claim','pos'),
('what is IDV','pos'),
('so long to reply','neg'),
('not worthy','neg'),
('worthy and helpful','pos'),
('update my details','pos'),
('Time taking','neg'),
("worse results",'neg'),
('not good','neg'),
('Modify policy','pos'),
('This bot is not good','neg'),
("hate",'neg'),
(" my policy id",'pos'),
("we regret to inform",'neg'),
("easy and simple",'pos'),
("hard and complex",'pos'),
("My car is damaged",'neg'),
("better results",'pos'),
('sorry for inconvenience','neg'),
("time taking",'neg'),
("time consuming",'neg'),
("bad",'neg'),
("worst results","neg"),
("wrong output","neg"),
('worse','neg'),
("result is not satisfactory",'neg'),
('not acurate results','neg'),
('bad application','neg'),
("improvement required",'neg'),
("I'm unhappy with the result",'neg'),
("the results does not make me happy",'neg'),
("long time",'neg'),
("Not the best",'neg'),
("not easy to use",'neg'),
("It takes alot of time for processing",'neg'),
("hard",'neg'),
("hard to use","neg")]

#sentimental analysis of conversation training data
c1=NaiveBayesClassifier(train)#training 
def trainin(Text):
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

