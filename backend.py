import json
import jsonpickle #this lets us store section listings in a file
import re #string ops
from ldap3 import Server, Connection, AUTH_SIMPLE, STRATEGY_SYNC, STRATEGY_ASYNC_THREADED, SEARCH_SCOPE_WHOLE_SUBTREE, GET_ALL_INFO

def beginConnection():
    """
    Opens an LDAP socket with the directory
    """
    s = Server('ldaps://directory.srv.ualberta.ca', port = 389, get_info = GET_ALL_INFO)  # define an unsecure LDAP server, requesting info on DSE and schema
    c = Connection(s, auto_bind = True, client_strategy = STRATEGY_SYNC)
    return s,c


def scheduleGenerator(coursesRequested, term, connection=None, load=0, noClosedSections = False, no8AM = False, noNight = False):
    """
    This is the main function of backend.py, which finds section times
    and generates the schedules. Returns a list of Schedules.
    """
    #coursesRequested is a string such as: 'ece 302,ece 311,ECE 325, ece 304'
    #term is a numeric string, such as '1490'
    if connection == None:
        s,c = beginConnection()

    else:
        s,c = connection

    #string = 'ece 302,ece 311,ece 325, ece 304'#input()
    #term = '1490'
    coursesRequested = coursesRequested.upper().split(',') #list
    for i in range(len(coursesRequested)):
        coursesRequested[i] = coursesRequested[i].strip()
        """
        if coursesRequested[i].count(' ') == 0: #see if space wasn't added
            firstNum = re.search('\d', coursesRequested[i]).start()
            coursesRequested[i] = (coursesRequested[:firstNum] + ' ' +
                                   coursesRequested[firstNum:] )
        """
    #sections is a list of lists of Section instances

    sections = getCourses(coursesRequested, term, c)


    #sections doesn't contain class times. Get them:
    getTimes(sections, term, c)

    
    #filter sections:
    mergeSimultaneous(sections)
    if noClosedSections: filterClosedSections(sections)
    if no8AM: filter8AM(sections)
    if noNight: filterNight(sections)

    schedules = makeSchedules(sections)

    if connection == None:#we opened the door, therefore we must close it.
        c.close()
    return schedules


def getCourses(courses, term, c):
    """
    Returns a list of lists of Sections.
    """
           
    f = open('sectionListingsTerm'+term+'.txt', 'r')
    pickled = f.read()
    courseDict = jsonpickle.decode(pickled)#converts to usable form

    sections = []

    for course in courses: #go through requested courses and make all schedules
        """
        lecture = [] #always assumes there is a lecture.
        seminar = [] #if a seminar is found, this will also be added to courses
        lab = [] #same for if a lab is found
        for section in allSections:
            if 'asString' in section['attributes'].keys():
                if section['attributes']['asString'][0].count(course):
                    
                    classID = section['attributes']['class'][0]
                    title=section['attributes']['asString'][0]
                    closed=section['attributes']['enrollStatus'][0]
                    
                    if closed == 'C': closed = True
                    else: closed = False
                    
                    newSection = Section(classID, title, closed)
                    if section['attributes']['asString'][0].count('SEM'):
                        seminar.append(newSection)
                    elif section['attributes']['asString'][0].count('LAB'):
                        lab.append(newSection)
                    else: #its probably a lecture, treat it as one
                        lecture.append(newSection)
        """
        if course in courseDict.keys():
            if courseDict[course]['lec']: sections.append(courseDict[course]['lec'])
            if courseDict[course]['lab']: sections.append(courseDict[course]['lab'])
            if courseDict[course]['sem']: sections.append(courseDict[course]['sem'])
        
    return sections

def updateCourseListings():
    """
    Updates course info from the server. Takes a few minutes to run.
    """
    s, c = beginConnection()#this says hello to the server

    terms = ['1490', '1500'] #fall 2014 and winter 2015 respectively

    for term in terms:
        print('Term '+term)
        allSections = []
        for char1 in '0123456789': #can't get all at once. must make 100 searches
            print(char1 + '0%')
            for char2 in '0123456789':

                c.search('ou=calendar, dc=ualberta, dc = ca', '(&(term='+term+')(class=*'+char1+char2+')(course=*))', SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['asString', 'class', 'enrollStatus']) #gets courses whose IDs end in char1 + char2

                allSections = allSections + c.response #append latest piece

        print('100%')

        courseDict = {} # this will relate course title to sections
        lecture = [] #this will store lab sections
        seminar = [] 
        lab = [] 
        for section in allSections:
            if 'asString' in section['attributes'].keys():
                classID = section['attributes']['class'][0]
                sectionTitle=section['attributes']['asString'][0]
                closed=section['attributes']['enrollStatus'][0]

                #find out what course this is by extracting "ECE 302" from
                #"ECE 302 SEM A1
                splitted = sectionTitle.split()
                i=0
                for word in splitted:#find the number location
                    if word.isnumeric():
                        numberIndex = i
                        break
                    i+=1
                courseTitle = ' '.join(splitted[:numberIndex + 1])
                if not (courseTitle in courseDict.keys()):
                    courseDict[courseTitle] = {'lec':[], 'lab':[], 'sem':[]}

                if closed == 'C': closed = True #convert from char to bool
                else: closed = False

                newSection = Section(classID, sectionTitle, closed)
                if section['attributes']['asString'][0].count('SEM'):
                    courseDict[courseTitle]['lab'].append(newSection)
                elif section['attributes']['asString'][0].count('LAB'):
                    courseDict[courseTitle]['sem'].append(newSection)
                else: #its probably a lecture, treat it as one
                    courseDict[courseTitle]['lec'].append(newSection)

        #store results for next time.
        f = open('sectionListingsTerm'+term+'.txt', 'w')
        pickled = jsonpickle.encode(courseDict)#now it can be stored:
        f.write(pickled)
        

def updateCourseListingsTest():
    """
    Updates course info from the server. Takes a few minutes to run.
    """

    s, c = beginConnection()#this says hello to the server

    terms = ['1490'] #fall 2014 and winter 2015 respectively

    for term in terms:
        allSections = []
        for i in range(100000):
            if not (i % 10000): print(i)
            c.search('ou=calendar, dc=ualberta, dc = ca', '(&(term='+term+')(class='+str(i)+')(course=*))', SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['asString', 'class', 'enrollStatus']) #gets courses whose IDs end in char1 + char2

            allSections = allSections + c.response #append latest piece

    print('100%')

    #store results for next time.
    f = open('sectionListingsTerm1490Test.txt', 'w')
    pickled = jsonpickle.encode(allSections)#now it can be stored:
    f.write(pickled)



def mergeSimultaneous(sections):
    """
    Merges sections that are simultanious and are the same course, such as
    CMPUT 274 A1 and CMPUT 274 EA1.
    """
    i = 0
    while i < len(sections):
        j = 0
        while j < len(sections[i]):
            k = j + 1
            while k < len(sections[i]):
                if sections[i][j].isSimultaneous(sections[i][k]):
                    #combine sectiontitles so information is not lost:
                    sections[i][j].sectionTitle += sections[i][k].sectionTitle
                    #consider open if any of the merged are open:
                    sections[i][j].closed &= sections[i][k].closed
                    sections[i].remove(sections[i][k])
                else:
                    k+=1
            j+=1
        i+=1

def filterClosedSections(sections):
    """
    Called depending on input. Filters sections with no vacancies.
    """
    for i in range(len(sections)):
        choppingBlock = []
        for section in sections[i]:
            if section.closed:
                choppingBlock.append(section)
        for closedSection in choppingBlock:
            sections[i].remove(closedSection)

def filter8AM(sections):
    
    """
    Called depending on input. Filters sections at 8AM.
    """
    for i in range(len(sections)):
        choppingBlock = []
        for section in sections[i]:
            if section.is8AM():
                choppingBlock.append(section)
        for closedSection in choppingBlock:
            sections[i].remove(closedSection)


def filterNight(sections):
    """
    Called depending on input. Filters sections after 5.
    """
    for i in range(len(sections)):
        choppingBlock = []
        for section in sections[i]:
            if section.isNightSection():
                choppingBlock.append(section)
        for closedSection in choppingBlock:
            sections[i].remove(closedSection)


def getTimes(sections, term, c):
    """
    Takes a list of lists of Section instances and defines the
    "section.times" parameter. The last step before actual
    schedules can be generated.
    """
    for course in sections:
        for section in course:
            classID = section.classID
            c.search('ou=calendar, dc=ualberta, dc = ca', '(&(term=' + term + ')(class=' + classID + ')(course=*)(classtime=*))', SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['*'])
            section.times = []
            for classtime in c.response:#this loop usually goes just once

                # get the location (if its there)
                if 'location' in classtime['attributes']:
                    location = classtime['attributes']['location'][0]
                else: location = None
                #get the day
                if 'day' in classtime['attributes']:
                    days = classtime['attributes']['day'][0]
                else: day = None
                #add the time, but only if start time is there
                if ('startTime' in classtime['attributes'] and
                    'endTime' in classtime['attributes'] ):
                    start=timeToInt(classtime['attributes']['startTime'][0])
                    end = timeToInt(classtime['attributes']['endTime'][0])
                    for day in days:
                        section.times.append( (day, start, end, location) )

                

def timeToInt(string):
    """
    Converts a time from a string to a number.

    >>>convertTime('9:00 AM')
    900
    >>>convertTime('1:00 PM')
    1300
    """
    time = string.replace(':','') #get rid of colon
    time = time.split()
    time[0] = int(time[0]) #convert to integer
    if time[1] == 'PM' and time[0] < 1200:
        time[0] += 1200
        
    return time[0]


def makeSchedules(sections):
    """
    Finds all valid schedules that can be constructed using the sections passed
    """

    schedules = []

    #search the 0th course for sections. This function will call itself
    #on the next course until it reaches the last course, at which point
    #a potential schedule has been found. This will be added to schedules.
    searchCourse(0, sections, [], schedules)

    return schedules


def searchCourse(iCourse, sections, prospect, winners):
    """
    Recursive function that will get called once per course the student
    needs to take. It explores the tree of possible schedules, not exploring
    branches with conflicts.
    """
    for section in sections[iCourse]:
        if not section.conflicts(prospect):
            if len(prospect) + 1 < len(sections):#look for next course:
                searchCourse(iCourse+1, sections, prospect + [section], winners)
            else: #the schedule now has all courses. add to winners.
                newSchedule = Schedule(prospect + [section])
                winners.append(newSchedule)


class Section:
    """
    This is a particular section, such as CMPUT 275 EA1. Some data is passed
    right away, note that the actual class times not added at initialization.
    """
    def __init__(self, classID, title, closed):
        self.classID = classID # 5 digit identifier
        self.title = title #ECE 302 SEM A1
        self.times = [] #tuple: ('M', 1200, 1250, 'ETLC 2-002')
        self.closed = closed #whether the course is open or not

        self.department = None #initialize these incase data is missing:
        self.type = None
        self.courseNumber = None
        self.sectionTitle = []

        splitTitle = title.split()
        i=0
        while i < len(splitTitle):
            if splitTitle[i].isnumeric():
                self.department = splitTitle[:i] # 'PHIL' or 'CH E'
                self.courseNumber = splitTitle[i] # '302'
                break
            i += 1
        if len(splitTitle) > i + 2: #make sure not at end of splitTitle
            self.type = splitTitle[i+1] # 'LEC' or 'SEM'
            self.sectionTitle = [splitTitle[i + 2]] # 'A1' or 'EA2'
    
    def isSimultaneous(self, otherSection):
        """
        Sees if two sections occur at the same time. Used by mergeSimultanious.
        """
        
        for myTime in self.times:
            timeMatchFound = False #each time must have a match
            for otherTime in otherSection.times:
                #check if day and times are the same
                if (myTime[0] == otherTime[0] and
                    myTime[1] == otherTime[1] and
                    myTime[2] == otherTime[2]):
                    timeMatchFound = True
            if timeMatchFound == False: return False

        return True #if we make it here, they're identical
            


    def conflicts(self, schedule):
        """
        Sees if this section conflicts with a list of sections, aka a schedule.
        """
        if self.times == []:
            #This implies that the times could not be found.
            return False #this section will not be used for any schedule

        for classA in self.times:
            for section in schedule:
                for classB in section.times:
                    if classA[0] == classB[0]: #same day
                        if ((classA[1] < classB[2] and classA[2] > classB[1]) or
                            (classB[1] < classA[2] and classB[2] > classA[1])):
                            #it both starts before other ends,
                            #and ends after the other starts. Conflict.
                            return True

        return False #if we make it here, no conflicts exist

    def is8AM(self):
        """
        sees if a section occurs at 8AM
        """
        for time in self.times:
            if time[1] == 800:
                return True
        return False

    def isNightSection(self):
        """
        sees if a section occurs after 5.
        """
        for time in self.times:
            if time[1] >= 1700:
                return True
        return False

class Schedule:
    """
    Basically just a list of sections, but with a few methods.
    """
    def __init__(self, sectionList):
        self.sections = sectionList

    def displayTimes(self):
        for section in self.sections:
            print(section.title + str(section.times))

    def has8AM(self):
        for section in self.sections:
            for slot in section.times:
                if slot[1] == 800:
                    return True
        return False

    def hasNight(self):
        for section in self.sections:
            for slot in section.times:
                if slot[1] >= 1700:
                    return True
        return False

    def compactness(self):
        """
        Returns the amount of time the student must spend at school.
        Used for sorting, so the best schedules are displayed.
        """
        compactness = 0
        for day in 'MTWRFSN':
            dayStart = 2400
            dayEnd = 800
            for section in self.sections:
                for time in section.times:
                    if time[0] == day:
                        dayStart = min(time[1], dayStart)
                        dayEnd = max(time[2], dayEnd)
            if dayStart < dayEnd:#this makes sure the day has at least one course
                compactness += dayEnd - dayStart
            
        return compactness
        
    def sleepInTime(self):
        """
        Returns a number corresponsing to how late a schedule
        begins. Specifically, the number of hours after 8AM
        before classes start. Used for sorting.
        """
        sleepInTime = 0
        for day in 'MTWRFSN':
            dayStart = 1700 #assume the best case to start
            for section in self.sections:
                for time in section.times:
                    if time[0] == day:
                        dayStart = min(time[1], dayStart)
            sleepInTime += dayStart - 800

        return sleepInTime

    def lateness(self):
        """
        Returns the weekly number of hours after 8AM before the
        student can go home.
        """
        lateness = 0
        for day in 'MTWRFSN':
            dayEnd = 800 #start by assuming best case
            for section in self.sections:
                for time in section.times:
                    if time[0] == day:
                        dayEnd = max(time[2], dayEnd)
            lateness += dayEnd - 800

        return lateness
        

    def isIdentical(self, herSchedule):
        #sees if another schedule has all the same sections
        for mySection in self.sections:
            #see if all my sections also appear in his
            matchFound = False
            for herSection in herSchedule.sections:
                if mySection.title == herSection.title:
                    matchFound = True
                    break
            if matchFound == False: return False #not identical
            
        return True #if we make it here, they're identical

    def isSimilar(self, herSchedule):
        #sees if another schedule has only different section titles,
        #but otherwise has the same times and everything
        for mySection in self.sections:
            #see if all my sections also appear in his
            matchFound = False
            for herSection in herSchedule.sections:
                 if (mySection.department == herSection.department and
                     mySection.courseNumber == herSection.courseNumber and
                     mySection.type == herSection.type):
                    #these courses are basically the same (excluding section.sectionTitle)
                     #see if times are the same:
                     sameTimes = True
                     for myTime in mySection.times:
                         timeMatchFound = False
                         for herTime in herSection.times:
                             if (myTime[0] == herTime[0] and
                                 myTime[1] == herTime[1] and
                                 myTime[2] == herTime[2]):
                                 timeMatchFound = True
                         if timeMatchFound == False:
                             sameTimes = False
                     if sameTimes == True:                     
                         matchFound = True

            if matchFound == False: return False #not identical
            
        return True #if we make it here, they're identical


        



