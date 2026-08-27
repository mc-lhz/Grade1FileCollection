import tkinter as tk
import random,time
import threading
def countExcept4(l):
    sum = 0
    for i in l:
        if i != 4:
            sum += i
    return sum
def diceButton():
    zy = 0
    global auto
    string = ''
    words = ["",'一秀','二举','三红','状元','五红','六红']
    x=random.choices(range(1, 7), k=6)
    #x=[2,2,2,2,1,1]
    #重复6次从列表中的各个成员中选取一个数，各个成员出现概率基本持平。
    number.set(x)
    '''print(x)
    print(x[0],x[1])'''
    numcount = ["",0,0,0,0,0,0]
    print(numcount)
    for i in x:
        numcount[i] += 1
        print(numcount[4])
    print(numcount)
    if numcount == ["",1,1,1,1,1,1]:
        string = '对堂'
    elif 4 in numcount and numcount[4] != 4:
        string = '四进'
        if numcount[4] == 1:
            string += '带一秀'
        elif numcount[4] == 2:
            string += '带二举'
    elif 1<=numcount[4]<=6:
        if numcount[4] == 4 or numcount[4] == 5 and numcount[4] == 6:
            pass
        string = words[numcount[4]]
        if numcount[1] == 2 and numcount[4]  == 4:
            string += '插金花'
            zy=1
        if numcount[4] == 4 or numcount[4] == 5:
            w = countExcept4(x)
            string += ('带' + str(w))
    
    if zy == 1:
        auto = False
        

    #result.set('啥都没有')
    if string:
        result.set(string)
    else:
        result.set('啥都没有')
def autoDice():
    global auto
    auto = 1
    while auto:
        diceButton()
        time.sleep(0.03)
def stopDice():
    global auto
    auto = 0
global auto
app=tk.Tk()  #创建一个主窗口
app.geometry('400x300+450+250')
app.title("博饼")
app.config(background="white")
number= tk.StringVar()
result= tk.StringVar()
label1=tk.Label(app, textvariable=number, font=('黑体', 32), bg="white", fg='red')
label2=tk.Label(app, textvariable=result, font=('黑体', 32), bg="white", fg='red')
label1.place(x=80, y=50)
label2.place(x=100, y=150)
copyRight=tk.Label(app, text=" mc_lhz Software 2026 - "+str(time.localtime().tm_year)+' All rights reserved.', font=('黑体', 12), bg="white", fg='black')
copyRight.place(x=0, y=280)
Button1=tk.Button(app,width=7,height=1,text='博饼啦',fg='black',borderwidth=2,command=diceButton)
Button1.place(x=100, y=250)
autoButton=tk.Button(app,width=7,height=1,text='开始',fg='black',borderwidth=2,command=lambda: threading.Thread(target=autoDice, daemon=True).start())
autoButton.place(x=180, y=250)
stopAutoButton=tk.Button(app,width=7,height=1,text='停止',fg='black',borderwidth=2,command=stopDice)
stopAutoButton.place(x=250, y=250)
app.mainloop()     #程序一直循环，直到我们关闭窗口