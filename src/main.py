import numpy as np
import json, operator, csv 
import fpdf
import subprocess
import sys
subprocess.check_call([sys.executable, "-m", "pip", "install", 'numpy'])
subprocess.check_call([sys.executable, "-m", "pip", "install", 'fpdf'])


max_no_of_days = 5

no_of_time_slots = 6

gamma = 0.4 #Change to provide a different coloring scheme

class Course:
    def __init__(self, id, code, student_list):
        self.id = id
        self.course_code = code
        self.student_list = student_list
        self.no_of_students = len(student_list)
        self.degree = 0
        self.flag = 1
        self.max_adjacency = 0
        self.adjacency_list = []
        self.color = None #Assign a color object here
        self.lecture_hall = []
        

    def ordered_adjacency_list(self):
        return sorted(self.adjacency_list, key = lambda course: (course.degree, course.max_adjacency), reverse = True)

    def assign_color(self, color):
        self.color = color
        color.courses.append(self)
        print( "Assigned : ", self.course_code,"day: ",color.day+1,"slot: ",color.slot,"students:",self.no_of_students)
        return None

    def get_hall_list(self):
        res = ""
        for i in self.lecture_hall:
            res = res + 'L% %' %(i[0].id, i[1])

    def __str__(self):
        return '%s' %(self.course_code)

class Color:
    def __init__(self, day, slot):
        self.lecture_halls = []
        self.day = day
        self.slot = slot
        self.courses = []

    def capacity_available(self):
        #Returns max students that can be accomodated
        capacity = 0
        for i in self.lecture_halls:
            capacity += i.availability()['total']
        return capacity

    def lecture_hall_list(self):

        available_halls = []
        for i in self.lecture_halls:
            if i.availability()['total']>0:
                available_halls.append(i)
        return available_halls

    def __str__(self):
        return 'color %s %s' %(self.day, self.color)

class LectureHall:
    def __init__(self, number, odd_capacity, even_capacity, color):
        self.number = number
        self.color = color
        
        color.lecture_halls.append(self)

        #O implies that odd/even seats are occupied. 
        #1 implies that odd/even seats are not occupied
        self.odd = 1
        self.even = 1

        self.odd_capacity = odd_capacity
        self.even_capacity = even_capacity

    def __str__(self):
        return '%s' %(self.number)

    def availability(self):
        if self.odd and self.even:
            return {
                "total": max(self.odd_capacity, self.even_capacity),
                "seats": (self.odd_capacity, self.even_capacity)
            }

        elif self.odd:
            return {
                "total" : self.odd_capacity,
                "seats" : (self.odd_capacity, 0)
            }

        elif self.even:
            return {
                "total" : self.even_capacity,
                "seats" : (0, self.even_capacity)
            }

        else:
            return {
                "total" : 0,
                "seats" : (0,0)
            }

class Student:
    def __init__(self, roll_no, courses):
        #self.name = name
        self.roll_no = roll_no
        self.courses_enrolled = courses

        #For count, key will be number of exams in one day
        #eg {1:4, 2:3} means that on 4 days, student has 1 exam, 
        #whereas on 3 days, students has 2
        self.count = {}


    def fairness_quotient(self):
        pass

def build_weight_matrix():
    with open('data/data_course.json') as data_file:
        course_data = json.load(data_file)

    course_index = {}
    courses=[]
    counter = 1
    for course_code, students in course_data.items():
        if len(students) == 0:
            continue
        
        crs = Course(counter, course_code, students)
        courses.append(crs)
        course_index[course_code] = crs
        counter+=1

    
    total = len(courses)
    graph = np.zeros([total, total])

    #Assigning weights to matrix
    for i in range(total):
        for j in range(i+1, total):
            graph[i,j] = calculate_common_students(courses[i], courses[j])
            graph[j,i] = graph[i,j]

    #To add adjacent courses for every courses in the adjacency list
    for i in range(total):
        courses[i].max_adjacency = max(graph[i])
        for j in range(i+1, total):
            if graph[i,j]:
                courses[i].adjacency_list.append(courses[j])
                courses[j].adjacency_list.append(courses[i])
    
    return graph, courses, course_index


def calculate_common_students(c1, c2):
    return len(list(set(c1.student_list).intersection(c2.student_list)))

def calculate_degree(matrix, courses):
    for i in range(len(courses)):
        courses[i].degree = np.sum(matrix[i]!= 0)

def initiailize_colors(max_no_of_days, no_of_time_slots):
    color_matrix = [[0 for x in range(no_of_time_slots)] for x in range(max_no_of_days)] 

    for day in range(max_no_of_days):
        for slot in range(no_of_time_slots):
            new_color = Color(day, slot)
            color_matrix[day][slot] = new_color

    return color_matrix



def initialize_lecture_halls(color_matrix):
    with open('data/lecture_halls2.json') as data_file:
        data = json.load(data_file)

    lhc = []

    for j in range(max_no_of_days):
        for k in range(no_of_time_slots):
            color = color_matrix[j][k]
            for number, capacity in data.items():
                lec_hall = LectureHall(number, capacity[0], capacity[1], color)
                lhc.append(lec_hall)
                color.lecture_halls.append(lec_hall)
    return lhc

def initialize_students(course_index):
    with open('data/data_student.json') as data_file:
        data = json.load(data_file)

    student_list = []

    for roll, courses in data.items():
        course_objects = []
        for i in courses:
            if i in course_index.keys():
                course_objects.append(course_index[i])
                

        std = Student(roll, course_objects)
        student_list.append(std)

    print( std.roll_no, std.courses_enrolled)

    return student_list

def dis_1(color_1, color_2):
    #raises exception if days not same
    if color_1.day == color_2.day:
        return abs(color_1.slot - color_2.slot)
    else:
        return "NA"

def dis_2(color_1, color_2):
    return abs(color_1.day - color_2.day)

def dis_3(color_1, color_2):
    num_1 = (color_1.day)*(no_of_time_slots) + color_1.slot
    num_2 = (color_2.day)*(no_of_time_slots) + color_2.slot

    if abs(num_1 - num_2) < 4:
        return False

    return True


def total_dis(color_1, color_2):
    d2 = dis_2(color_1, color_2)
    d1 = dis_1(color_1, color_2)

    return gamma*d2 + d1

def binary_search(alist, item):
    first = 0
    last = len(alist) - 1
    found = False
    
    while first <= last and not found:
        midpoint = (first + last) // 2
        if alist[midpoint][1] == item:
            found = True
            last = midpoint-1
        else:
            if item < alist[midpoint][1]:
                last = midpoint - 1
            else:
                first = midpoint + 1
    return last+1

def get_lecture_hall(max_students, sorted_list):
    lecturehall_list=list(sorted_list)
    selected_lecture_halls = {}    
    while(max_students > 0):
        i = binary_search(lecturehall_list, max_students)
        if(i < 0):
            i = 0
        elif(i >= len(lecturehall_list)):
            i = len(lecturehall_list) - 1
        if(i<0):
            selected_lecture_halls={}
            break
        max_students = max_students - lecturehall_list[i][1]
        lecturehall_object =lecturehall_list[i][0][0]
        lecture_hall = lecturehall_object.number
        oe = lecturehall_list[i][0][1] #odd-even seating arrangement
        del lecturehall_list[i]
        selected_lecture_halls[lecturehall_object] = oe
        for j in range(len(lecturehall_list)):
            if(lecturehall_list[j][0][0].number==lecture_hall):
                del lecturehall_list[j]
                break
    return selected_lecture_halls
    

def select_lecture_hall(no_of_students, color):
    if no_of_students> color.capacity_available():
        return {}

    lecture_halls = color.lecture_hall_list()
    lecture_hall_dict = {}
    for i in lecture_halls:
        lecture_hall_dict[i]=i.availability()['seats']
    
    lecture_hall_tuple_list = {}

    for num, value in lecture_hall_dict.items():
        lecture_hall_tuple_list[(num,'odd-rows')] = value[0]
        lecture_hall_tuple_list[(num,'even-rows')] = value[1]
    sorted_list = sorted(lecture_hall_tuple_list.items(), key=operator.itemgetter(1))
    return get_lecture_hall(no_of_students, sorted_list)

def update_lecture_hall(hall_list, course, color):
    course.assign_color(color)
    if course.no_of_students > 10:

        course.lecture_hall = hall_list

        for hall, position in course.lecture_hall.items():
            if position=='odd-rows':
                hall.odd = 0
            elif position=='even-rows':
                hall.even = 0


def get_first_node_color(course, color_matrix):

    for j in range(max_no_of_days):
        for k in range(no_of_time_slots):
            hall_list = select_lecture_hall(course.no_of_students, color_matrix[j][k])
            if hall_list:
                return color_matrix[j][k], hall_list

    return None

def get_smallest_available_color(course, color_matrix, constraints):
    adj_list = course.adjacency_list
    for j in range(max_no_of_days):
        for k in range(no_of_time_slots):
            valid = True

            assigned_lh = select_lecture_hall(course.no_of_students, color_matrix[j][k])

            if not assigned_lh:
                valid= False
                continue

            for r in range(len(adj_list)):
                color = adj_list[r].color
                if color:
                    if color.day!= j or color.slot!=k:
                        if "check_dis_3" in constraints:
                            if not dis_3(color, color_matrix[j][k]):
                                valid = False
                                break

                        if "check_consecutive" in constraints:
                            if dis_2(color, color_matrix[j][k]) == 0:
                                if dis_1(color, color_matrix[j][k]) <= 1:
                                    valid = False
                                    break
                        if "check_three_exams" in constraints:   
                            if check_three_exams_constraint(course, color_matrix[j][k], j, color_matrix) == False:
                                valid = False
                                break
                    else:
                        valid = False
                        break
                else:
                    continue

            if valid == True:
                if color_matrix[j][k]:
                    return color_matrix[j][k], assigned_lh
                
    return None    

def check_three_exams_constraint(course, color_jk, j, color_matrix):
    students = course.student_list

    for r in range(len(students)):
        counter = 0
        for q in range(no_of_time_slots):
            course_list = color_matrix[j][q].courses
            for u in range(len(course_list)):
                students_u = course_list[u].student_list
                if students[r] in students_u:
                    counter+=1
                    if counter == 2:
                        return False

    return True

def schedule_exam(sorted_courses,constraints,count):
    num_colored_courses=0 
    for course in sorted_courses:
        if num_colored_courses == len(sorted_courses):
            break
    
        if not course.color and course.flag:
    
            if sorted_courses.index(course)==0 and count==0:
                r_ab, hall_list = get_first_node_color(course, color_matrix)
                if r_ab == None:
                    print( "No schedule is possible")
                    break
        
            else:
                res = get_smallest_available_color(course, color_matrix,constraints)
                if res:
                    r_ab, hall_list = res
                else:
                    r_ab = None
                    course.flag = 0

            if r_ab:
                num_colored_courses+=1 
                if hall_list:
                    update_lecture_hall(hall_list, course, r_ab)
    
        m = course.ordered_adjacency_list()
        for adj_course in m:
            if not adj_course.color and adj_course.flag:
                res = get_smallest_available_color(adj_course, color_matrix,constraints)
                if res:
                    r_cd, hall_list = res
                else:
                    r_cd = None
                    adj_course.flag= 0
 
                if r_cd:
                    num_colored_courses+=1
                    if hall_list:
                        update_lecture_hall(hall_list, adj_course, r_cd)
    alloted_courses = []
    for i in range(max_no_of_days):
        for j in range(no_of_time_slots):
            for k in color_matrix[i][j].courses:
                alloted_courses.append(k)
    print( len(alloted_courses))
    unalloted_courses=list(set(sorted_courses)-set(sorted_courses).intersection(alloted_courses))
    for c in unalloted_courses:
        c.flag=1
    return sorted(unalloted_courses, key = lambda course: (course.degree, course.max_adjacency), reverse = True)

def hard_schedule(unalloted_courses):
    constraints=["check_consecutive","check_three_exams", "check_dis_3"]

    unalloted_courses=schedule_exam(unalloted_courses, constraints,0)
    constraints =["check_three_exams"]

    unalloted_courses=schedule_exam(unalloted_courses, constraints,1)
    constraints =["check_dis_3"]

    unalloted_courses=schedule_exam(unalloted_courses, constraints,1)
    constraints =["check_consecutive"]

    unalloted_courses=schedule_exam(unalloted_courses, constraints,2)
    constraints =[""]
    
    unalloted_courses=schedule_exam(unalloted_courses, constraints,3)
    return len(unalloted_courses)

def color_num(color, TIME_SLOTS):
	return (color.day)*(TIME_SLOTS) + color.slot

def test_for_clash(students, TIME_SLOTS):
	clash = []

	for student in students:
		a = []
		for crs in student.courses_enrolled:
			if crs.color:
				a.append(color_num(crs.color, TIME_SLOTS))
				if len(a)!=len(set(a)):
					clash.append(student.roll_no)

def check_three_exam_constraint(student, courses):
	days = []

	for i in courses:
		days.append(i.color.day)

	b = list(set(days))

	c = []
	for i in b:
		c.append(days.count(i))

	count = {}
	for i in c:
		if i in count.keys():
			count[i] +=1
		else:
			count[i] = 1

	student.count = count

	if 3 in count.keys():
		return False
	
	return True

def slot_difference(student, courses, TIME_SLOTS):

	color_number = [color_num(i.color, TIME_SLOTS) for i in courses].sort()

	diff = []
	if not color_number:
		return 0
	for i in range(len(color_number) - 1):
		diff.append(color_number[i+1] - color_number[i])

	res = [i>=3 for i in diff]
	failed = res.count(False)
	student.slot_diff = failed

	return failed



def test_constraints(students, TIME_SLOTS):
	not_alloted = []
	three_fails = []
	slot_fails = []
	for student in students:
		flag = 0
		courses = []
		for crs in student.courses_enrolled:
			if crs.color:
				courses.append(crs)
			else:
				not_alloted.append(crs)
			check1 = check_three_exam_constraint(student, courses)

			if not check1:
				three_fails.append(student)			

			if courses:
				check2 = slot_difference(student, courses, TIME_SLOTS)
				if check2:
					flag = 1
		if flag:
			slot_fails.append(student)



if __name__ == "__main__":

    graph, course_list, course_index = build_weight_matrix()
    calculate_degree(graph, course_list)    
    print ("Total Courses : ", len(course_list))
    
    pdf2 = fpdf.FPDF( )
    pdf2.add_page()
    pdf2.set_font('Courier',size = 14)

    pdf = fpdf.FPDF( )
    pdf.add_page()
    pdf.set_font('Courier',size = 14)


    sorted_courses = sorted(course_list, key = lambda course: (course.degree, course.max_adjacency), reverse = True)
    course = sorted(course_list, key = lambda course: (course.course_code))
    deg = []

    color_matrix = initiailize_colors(max_no_of_days, no_of_time_slots)

    student_list = initialize_students(course_index)

    lh_list = initialize_lecture_halls(color_matrix)
    no_ofunscheduled_courses=hard_schedule(sorted_courses)
    if(no_ofunscheduled_courses!=0):
        print( "Increase days or slots.",no_ofunscheduled_courses, " courses remains unscheduled")
        pdf.write(5,"Increase days or slots,")
        pdf.write(5,str(no_ofunscheduled_courses))
        pdf.write(5," courses remains unscheduled")
        pdf.ln()
        pdf.ln()
        pdf2.write(5,"Increase days or slots,")
        pdf2.write(5,str(no_ofunscheduled_courses))
        pdf2.write(5," courses remains unscheduled")
        pdf2.ln()
        pdf2.ln()
        
    count=0
    num = 0    
  
    for i in course:
        if i.lecture_hall:
            res = i.course_code + " :: " + "Day " + str((i.color.day)+1) + " Slot " + str((i.color.slot)+1) + ", Rooms :"
            for key, val in i.lecture_hall.items():
                res+= " LH0" + str(key.number) + " " + val + ","
            res += " Strength: " + str(i.no_of_students) + "\n"

            print (res)
            print( "\n")
            pdf2.write(5,str(res))
            pdf2.ln()
            pdf2.ln()
    print( "\n")
    pdf2.ln()
    pdf2.output("course-slot.pdf")

    alloted_courses = []
    for i in range(max_no_of_days):
        for j in range(no_of_time_slots):
            l = []
            num = 0
            for k in color_matrix[i][j].courses:
                count+=1
                num+=k.no_of_students
                alloted_courses.append(k)
                l.append(k.course_code)
            
            print ("Day ", i+1, " Slot ", j+1, " : ", "Courses : ", l, "students : ", num, "\n\n")
            pdf.write(5,"Day ")
            pdf.write(5,str(i+1))
            pdf.write(5 ," Slot ")
            pdf.write(5, str(j+1))
            pdf.ln()
            pdf.ln()
            pdf.write(5," Courses :: ")
            pdf.write(5, str(l) )
            pdf.write(5, " Students ")
            pdf.write(5,str(num))
            pdf.ln()
            pdf.ln()

    print ("Total Courses assigned a slot in Timetable : ", count)
 
    pdf.output("slot-course.pdf")
    test_for_clash(student_list, no_of_time_slots)
    test_constraints(student_list, no_of_time_slots)
   
