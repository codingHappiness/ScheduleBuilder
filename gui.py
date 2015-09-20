
#From http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/minimal-app.html
import random
import tkinter as tk
from tkinter import *
from backend import *

global schedNum 
schedNum = 0 #schedule counter
global schedules
global connection
connection = None

new = Tk() #instantiate new tk interface
new.title("Course Scheduler")

global term
global sortMethod

#term = ''
term = tk.IntVar()#records which term should be used
sortMethod = tk.IntVar()#records which term should be used

schedule=Tk() #second window for displaying the schedule
schedule.title("Schedule")

#Frame to fixup formatting
lilFrame = tk.Frame(new)

#due to the nature of tkinter, each course Entry field must have a unique
#StringVar variable associated with it in order to retrieve the contents
#of the field box. It is not possible to use a list.
course1 = tk.StringVar()
course2 = tk.StringVar()
course3 = tk.StringVar()
course4 = tk.StringVar()
course5 = tk.StringVar()
course6 = tk.StringVar()
course7 = tk.StringVar()
course8 = tk.StringVar()
course0 = tk.StringVar()

#each box creates an Entry Text field to submit a course to the scheduler.
box0 = Entry(new, textvariable = course0, width = 11 )
box1 = Entry(new, textvariable = course1, width = 11 ) 
box2 = Entry(new, textvariable = course2, width = 11 )
box3 = Entry(new, textvariable = course3, width = 11 )
box4 = Entry(new, textvariable = course4, width = 11 )
box5 = Entry(new, textvariable = course5, width = 11 )
box6 = Entry(new, textvariable = course6, width = 11 )
box7 = Entry(new, textvariable = course7, width = 11 )
box8 = Entry(new, textvariable = course8, width = 11 )

#variables to hold checkbox selections, 0 is unchecked, 1 is checked
filterClosed = IntVar()
filterMorning = IntVar()
filterEvening = IntVar()

#checkbox to decide whether or not schedules with 8:00AM courses should be shown
closedButton = Checkbutton(new, text="Filter closed classes?", variable = filterClosed)
morningButton = Checkbutton(new, text="Filter morning classes?", variable = filterMorning)
eveningButton = Checkbutton(new, text="Filter evening classes?", variable = filterEvening)

#Set the first six boxes to the fall term schedule second year comp e students.
box0.insert(0, "ECE 210")
box1.insert(0, "ECE 202")
box2.insert(0, "MATH 209")
box3.insert(0, "PHIL 325")
box4.insert(0, "MATH 201")
box5.insert(0, "ENGL 199")

#Titles to the left of course entry boxes
b0l = Label(new, text = "Course 1: ")
b1l = Label(new, text = "Course 2: ")
b2l = Label(new, text = "Course 3: ")
b3l = Label(new, text = "Course 4: ")
b4l = Label(new, text = "Course 5: ")
b5l = Label(new, text = "Course 6: ")
b6l = Label(new, text = "Course 7: ")
b7l = Label(new, text = "Course 8: ")
b8l = Label(new, text = "Course 9: ")

#instantiate main area for drawing the courses on the window
table = Canvas(schedule, width=680, height=470, bg="#FFFFFF")


#Convert four digit integer for time into pixel coordinates in Y direction
def timeLoca(time):
    hour = time // 100 #turns 1350 into 13 for 1PM
    minute = time % 100 #turns 1350 into 50 for :50 minutes

    return ( hour - 8 + minute/60) * 36  #36 is pixel per hour

#convert day of the week into proper X coordinate pixel value
def dayLoca(day):

    if day == 'M':
        return 136*0
    elif day == 'T':
        return 136*1
    elif day == 'W':
        return 136*2
    elif day == 'R':
        return 136*3
    elif day == 'F':
        return 136*4

#append courses entered in form as comma separated string of values
def getCourses():
    listing = ""
    
    if course0.get() != "":
        listing+=course0.get()
    
    if course1.get() != "":
        if listing!="":
            listing+=","
        listing+=course1.get()
    
    if course2.get() != "":
        if listing!="": 
            listing+=","
        listing+=course2.get()
    
    if course3.get() != "":
        if listing!="":
            listing+=","
        listing+=course3.get()
    
    if course4.get() != "":
        if listing!="":
            listing+=","
        listing+=course4.get()
    
    if course5.get() != "":
        if listing!="":
            listing+=","
        listing+=course5.get()
    
    if course6.get() != "":
        if listing!="":
            listing+=","
        listing+=course6.get()
    
    if course7.get() != "":
        if listing!="":
            listing+=","
        listing+=course7.get()
    
    if course8.get() != "":
        if listing!="":
            listing+=","
        listing+=course8.get()
    
    return listing

def writeLabel():
    #Displays which schedule you are viewing
    pString = str(schedNum + 1) + " / " + str(len(schedules))
    progress = Label(schedule, text=pString, padx = 10)
    progress.grid(row=14, column = 2)
   
def bumpup():#load next schedule
    global schedNum
    global schedules
    if schedNum < len(schedules) - 1:
        schedNum+=1
    drawSched()
    writeLabel()

def bumpdown():#load previous schedule
    global schedNum
    if schedNum > 0:
        schedNum-=1
    drawSched()
    writeLabel()

def fetchSched():#get schedule object to render on screen
    global schedules
    global connection
    global term
    global sortMethod
    global schedNum
    schedNum = 0
    
    if connection == None:
        connection = beginConnection()#this says hello to the server

        #get all the schedules. Here is where we interface with backend.py
    schedules = scheduleGenerator( getCourses(), str(term.get()), connection, noClosedSections = filterClosed.get(), no8AM = filterMorning.get(), noNight = filterEvening.get() )

    if sortMethod.get() == 1: #compactness
        schedules = sorted(schedules, key=lambda x : x.compactness() )
    elif sortMethod.get() == 2: #randomly
        schedules = sorted(schedules, key=lambda *args: random.random())
    elif sortMethod.get() == 3: # maximize sleeping in
        #first sort by compactness, as a tiebreaker
        schedules = sorted(schedules, key=lambda x : x.compactness() )
        schedules = sorted(schedules, key=lambda x : -x.sleepInTime() )
    elif sortMethod.get() == 4: #maximize lateness
        schedules = sorted(schedules, key=lambda x : x.compactness() )
        schedules = sorted(schedules, key=lambda x : x.lateness())


        
def error():
    error = Tk()
    error.title("No Schedules.")
    errorMessage = "There are no schedules for your selection options.\nTry again."
    Label(error, text=errorMessage).grid(row=0)
    Button(error, text="Oops..", command=error.destroy ).grid(row=1)

def submitHit():
    fetchSched()
    drawSched()
    writeLabel()



def drawSched():
#######################################3
    print(schedNum)
#############################################

    table.delete("all") #clear canvas before drawing to it again
    
    #Draw gridlines for schedule
    for i in range(0,680,136):
        table.create_line(i,0,i,470, fill="GRAY", dash=(1,4))
    for j in range(0,500,36):
        table.create_line(0,j, 680, j, fill="GRAY", dash=(1,4))

    textColor = ["#cc0000", "#00c957", "#000080", "#008000", "#6d21a3", "#0e207f",
                "#ff23eb", "#4c3c3c", "#660099", "#FF6600", "#CC0000", "#A04958"] 
                #holds colors for course text colors
    
    #constants for drawing to canvas
    pixelsPerHour = 36
    pixelsPerDay = 136
    textOffsetY = 18
    textOffsetX = 68

    #Generate all possible schedules and pass one to be drawn
    #schedules = scheduleGenerator( getCourses(), '1490' )
    global schedules
    try:
        schedule = schedules[schedNum]
    except IndexError:
        error() 
        schedule = 'null'
    
    colorCounter=0#gives each new course a different color from textColor
    
    for section in schedule.sections:
        for time in section.times:
            xLeft = dayLoca(time[0])
            xRight = xLeft + 136
            yTop = timeLoca(time[1])
            yBottom = timeLoca(time[2])
            
            #draw black box around each course to show time of course
            table.create_line(xLeft,yTop,xRight,yTop)
            table.create_line(xLeft,yTop,xLeft,yBottom)
            table.create_line(xLeft,yBottom,xRight,yBottom)
            table.create_line(xRight,yTop,xRight,yBottom)

            #draw each course title in a unique color
            table.create_text(xLeft + textOffsetX,
                              yTop + textOffsetY,
                              text = section.title, fill = textColor[colorCounter]
                              )
        #Move to next counter and account for running out of colors
        colorCounter+=1
        if colorCounter > 11:
            colorCounter = 0


#######################################################################
###############Formatting the GUI layout###############################
##\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/######

#button for updating/downloading course information
updateButton = Button(new, text = "Update Course Library", command = updateCourseListings)

table.grid(row=1, column=1,rowspan=13,columnspan=5,sticky=N+W)

#button to kill the program, accessible from the main window with fields
quitButton = tk.Button(new, text="Click to Exit", command = new.quit)
#button to process data entries and generate schedules
submitButton = tk.Button(new, text="Submit", command = submitHit )


#format the location of text Entry labels, left hand side
b0l.grid(row = 0, column = 0, padx = 4, pady = 4)
b1l.grid(row = 1, column = 0, padx = 4, pady = 4)
b2l.grid(row = 2, column = 0, padx = 4, pady = 4)
b3l.grid(row = 3, column = 0, padx = 4, pady = 4)
b4l.grid(row = 4, column = 0, padx = 4, pady = 4)
b5l.grid(row = 5, column = 0, padx = 4, pady = 4)
b6l.grid(row = 6, column = 0, padx = 4, pady = 4)
b7l.grid(row = 7, column = 0, padx = 4, pady = 4)

#format entry boxes to the right of their corresponding labels
box0.grid(row = 0, column = 1, padx = 4, sticky=W)
box1.grid(row = 1, column = 1, padx = 4, sticky=W)
box2.grid(row = 2, column = 1, padx = 4, sticky=W)
box3.grid(row = 3, column = 1, padx = 4, sticky=W)
box4.grid(row = 4, column = 1, padx = 4, sticky=W)
box5.grid(row = 5, column = 1, padx = 4, sticky=W)
box6.grid(row = 6, column = 1, padx = 4, sticky=W)
box7.grid(row = 7, column = 1, padx = 4, sticky=W)

#format the checkbox under the label and entry columns
closedButton.grid(row = 8, columnspan = 2)
morningButton.grid(row = 9, columnspan = 2)
eveningButton.grid(row = 10, columnspan = 2)

"""
#Radio buttons to select the appropriate year / term
Radiobutton(new, text = "Fall 2014", textvariable = term, value = 1490).grid(row = 11, column = 0)
Radiobutton(new, text = "Winter 2014", textvariable = term, value = 1500).grid(row = 11, column = 1)
#These term values are guesses
Radiobutton(new, text = "Fall 2015", textvariable = term, value = 1530).grid(row = 12, column = 0)
Radiobutton(new, text = "Winter 2016", textvariable = term, value = 1540).grid(row = 12, column = 1)
Radiobutton(new, text = "Fall 2016", textvariable = term, value = 1570).grid(row = 13, column = 0)
Radiobutton(new, text = "Winter 2017", textvariable = term, value = 1580).grid(row = 13, column = 1)
"""

#Title for term radio buttons
Label(new, text = "\nTerm:").grid(row=11, columnspan=2, pady=4)

#Radio buttons to select the appropriate year / term
fall14=Radiobutton(new, text = "Fall 2014", variable = term, value = 1490)

winter15=Radiobutton(new, text = "Winter 2015", variable = term, value = 1500)
#These term values are guesses
"""
fall15=Radiobutton(new, text = "Fall 2015", variable = term, value = 1530)
winter16=Radiobutton(new, text = "Winter 2016", variable = term, value = 1540)
fall16=Radiobutton(new, text = "Fall 2016", variable = term, value = 1570)
winter17=Radiobutton(new, text = "Winter 2017", variable = term, value = 1580)
"""
#positioning the term selectors
fall14.grid(row = 12, column = 0)
fall14.select()
winter15.grid(row = 12, column = 1)
"""
fall15.grid(row = 13, column = 0)
winter16.grid(row = 13, column = 1)
fall16.grid(row = 14, column = 0)
winter17.grid(row = 14, column = 1)
"""

#Title for sorting section
Label(new, text='\nSorting:').grid(row = 15, columnspan = 2, pady=4)

##Radio buttons for sort method
sortNone=Radiobutton(new, text = 'No Sorting', variable = sortMethod, value = 0)
sortCompactness=Radiobutton(new, text = 'Sort by Compactness', variable = sortMethod, value = 1)
sortRandom=Radiobutton(new, text = 'Sort Randomly', variable = sortMethod, value = 2)
sortSleepInTime=Radiobutton(new, text = 'Maximize Sleep-in Time', variable = sortMethod, value = 3)
sortLateness=Radiobutton(new, text = 'Finish Early', variable = sortMethod, value = 4)

#position the radio buttons for sorting
sortNone.grid(row=16, columnspan=2, sticky=W)
sortNone.select()#Normally return methodically produced schedules
sortCompactness.grid(row = 17, columnspan = 2, sticky=W)
sortRandom.grid(row = 18, columnspan = 2, sticky=W)
sortSleepInTime.grid(row = 19, columnspan = 2, sticky=W)
sortLateness.grid(row = 20, columnspan = 2, sticky=W)

#position main buttons
quitButton.grid( row = 21, column=0, pady = 8, padx = 4)
submitButton.grid( row = 21, column=1, pady = 8, padx = 4)
updateButton.grid( row = 22, columnspan = 2)


#Table for displaying the schedule
corner= Label(schedule, text="Fall/Winter 20XX")
corner.config(bd=3, bg="white", relief="ridge", justify="left", width=16)
corner.grid(row=0, column=0)

t8a=Label(schedule, text="8:00 AM")
t8a.grid(row=1, column=0)
t8a.config(bd=3, bg="white", relief="ridge", justify="left", width=16, height = 2)

t9a=Label(schedule, text="9:00 AM")
t9a.grid(row=2, column=0)
t9a.config(bd=3, bg="white", relief="ridge", justify="left", width=16, height = 2)

t10a=Label(schedule, text="10:00 AM")
t10a.grid(row=3, column=0)
t10a.config(bd=3, bg="white", relief="ridge", justify="left", width=16, height = 2)

t11a=Label(schedule, text="11:00 AM")
t11a.grid(row=4, column=0)
t11a.config(bd=3, bg="white", relief="ridge", justify="left", width=16, height = 2)

t12p=Label(schedule, text="12:00 PM")
t12p.grid(row=5, column=0)
t12p.config(bd=3, bg="white", relief="ridge", justify="left", width=16, height = 2)

t1p=Label(schedule, text="1:00 PM")
t1p.grid(row=6, column=0)
t1p.config(bd=3, bg="white", relief="ridge", justify="left", width=16, height = 2)

t2p=Label(schedule, text="2:00 PM")
t2p.grid(row=7, column=0)
t2p.config(bd=3, bg="white", relief="ridge", justify="left", width=16, height = 2)

t3p=Label(schedule, text="3:00 PM")
t3p.grid(row=8, column=0)
t3p.config(bd=3, bg="white", relief="ridge", justify="left", width=16, height = 2)

t4p=Label(schedule, text="4:00 PM")
t4p.grid(row=9, column=0)
t4p.config(bd=3, bg="white", relief="ridge", justify="left", width=16, height = 2)

t5p=Label(schedule, text="5:00 PM")
t5p.grid(row=10, column=0)
t5p.config(bd=3, bg="white", relief="ridge", justify="left", width=16, height = 2)

t6p=Label(schedule, text="6:00 PM")
t6p.grid(row=11, column=0)
t6p.config(bd=3, bg="white", relief="ridge", justify="left", width=16, height = 2)

t7p=Label(schedule, text="7:00 PM")
t7p.grid(row=12, column=0)
t7p.config(bd=3, bg="white", relief="ridge", justify="left", width=16, height = 2)

t8p=Label(schedule, text="8:00 PM")
t8p.grid(row=13, column=0)
t8p.config(bd=3, bg="white", relief="ridge", justify="left", width=16, height = 2)

monday = Label(schedule, text="Monday")
monday.grid(row=0, column= 1)
monday.config(bd=3, bg="white", relief="ridge", justify="left", width=16)

tuesday = Label(schedule, text="Tuesday")
tuesday.grid(row=0, column= 2)
tuesday.config(bd=3, bg="white", relief="ridge", justify="left", width=16)

wednesday = Label(schedule, text="Wednesday")
wednesday.grid(row=0, column= 3)
wednesday.config(bd=3, bg="white", relief="ridge", justify="left", width=16)

thursday = Label(schedule, text="Thursday")
thursday.grid(row=0, column= 4)
thursday.config(bd=3, bg="white", relief="ridge", justify="left", width=16)

friday = Label(schedule, text="Friday")
friday.grid(row=0, column= 5)
friday.config(bd=3, bg="white", relief="ridge", justify="left", width=16)

quit2 = Button(schedule, text="Quit", command=schedule.quit)
quit2.grid(row=14, column=0)

#Schedule Navigation Buttons
previous = Button(schedule, text="Previous", command=bumpdown)
previous.grid(row=14, column = 1)


next = Button(schedule, text="Next", command=bumpup)
next.grid(row=14, column = 3)

#Generate lines for table intersections
for i in range(0,680,136):
    table.create_line(i,0,i,470, fill="GRAY", dash=(1,4))
#    table.create_text(i+68,38, text="Testing\nLine 2", fill="RED", anchor=N)
for j in range(0,500,36):
    table.create_line(0,j, 680, j, fill="GRAY", dash=(1,4))
#    table.create_text(68,76+j, text="Math 201 LAB\n54802", fill="BLUE", anchor=N)

#For writing to each individual cell,
#Horizontal X values:
#Monday=68, Tuesday=68*2, Wednesday=68*3, Thursday=68*4, Friday=68*5
#Vertical Y values:
#8:00AM=0, 9:00AM=38, 10:00AM=38*2, 11:00AM=38*3... aka 38*(time-8) for 24 hour


#contains a variety of beautiful colors to differentiate classes by.

new.mainloop()
