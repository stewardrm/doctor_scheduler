import copy
import random
import math
import pandas as pd

class DoctorScheduling:
    def __init__(self, num_days_in_month, doctor_shifts, days_unavail, allow_day_night_double, allow_night_day_double, max_days_in_row, req_days_off, ideal_num_shifts, shift_type_pref, prev_month=None):
        self.num_days_in_month = num_days_in_month
        self.doctor_shifts = doctor_shifts
        self.days_unavail = days_unavail
        self.allow_day_night_double = allow_day_night_double
        self.allow_night_day_double = allow_night_day_double
        self.max_days_in_row = max_days_in_row
        self.req_days_off = req_days_off
        self.ideal_num_shifts = ideal_num_shifts
        self.shift_type_pref = shift_type_pref
        self.prev_month=prev_month
        self.tot_prev_shifts={}
        self.calendar, self.scheduler, self.tot_prev_shifts = self.initialize_monthly_scheduler()

    def initialize_monthly_scheduler(self):
        calendar = {day: ["Day1", "Day2", "Night"] for day in range(1, self.num_days_in_month + 1)}
        scheduler = {}

        if self.prev_month is None:
            for doctor in self.doctor_shifts:
                scheduler[doctor] = {"Day1": [], "Day2": [], "Night": []}
                self.tot_prev_shifts[doctor] = 0
        else:
            scheduler, self.tot_prev_shifts = self.modify_prev_month(self.prev_month)

        return calendar, scheduler, self.tot_prev_shifts


    def modify_prev_month(self):
        if not self.prev_month:
            return {}, {}

        converted_prev_month = copy.deepcopy(self.prev_month)
        tot_prev_shifts = {doctor: 0 for doctor in self.doctor_shifts}  # Initialize for all doctors
        largest = 0

        # Find the largest day number in the previous month's schedule
        for shifts in converted_prev_month.values():
            for days in shifts.values():
                if days:
                    largest = max(largest, max(days))

        # Adjust the days and count the shifts for each doctor
        for doctor, shifts in converted_prev_month.items():
            num_shifts = 0
            for shift_type, days in shifts.items():
                adjusted_days = [day - largest for day in days if day > largest - 6]
                num_shifts += len(adjusted_days)
                converted_prev_month[doctor][shift_type] = adjusted_days
            tot_prev_shifts[doctor] = num_shifts

        return converted_prev_month, tot_prev_shifts

#def assign_shifts(calendar, scheduler, doctor_shifts, days_unavail,tot_prev_shifts):
    def assign_shifts(self):
        
        for i in range(10000):
            remaining_shifts = [(day, shift) for day in self.calendar for shift in self.calendar[day]]
            self.calendar, self.scheduler, self.tot_prev_shifts = self.initialize_monthly_scheduler()
            while remaining_shifts:
                day, shift_type = random.choice(remaining_shifts)
                docs_below = self.doctors_below_minimum(self.doctor_shifts, self.scheduler,self.tot_prev_shifts)
                eligible_doctors = []
                for doctor in docs_below:
                    too_many_straight_shifts=False
                    flattened=self.flatten_schedule(self.scheduler)
                    flattened_doc=flattened[doctor]
                    temp=copy.deepcopy(flattened_doc)
                    temp.append(day)
                    temp.sort()             
                    if self.check_max_consec_days(temp, self.max_days_in_row):
                            too_many_straight_shifts=True
                    
                    if too_many_straight_shifts==True:
                        continue
                    elif (self.count_total_shifts(self.scheduler[doctor])-self.tot_prev_shifts[doctor]) > self.doctor_shifts[doctor][1]:
                        continue
                    elif  self.has_3consecutive_shifts_single_doctor(self.scheduler[doctor], day, shift_type):
                        continue
                    elif shift_type.startswith("Day"):
                        if day in self.scheduler[doctor]["Day1"] or day in self.scheduler[doctor]["Day2"]:
                            continue
                        elif day in self.days_unavail[doctor]["Day"] and shift_type.startswith("Day"):  # Check if the day and shift are unavailable for the doctor
                            continue
                        elif day in self.days_unavail[doctor]["Night"] and shift_type=="Night":  # Check if the day and shift are unavailable for the doctor
                            continue
                        elif self.allow_day_night_double==False and day in self.scheduler[doctor]['Night']:
                            continue
                        elif self.allow_night_day_double==False and (day-1) in self.scheduler[doctor]['Night']:
                                continue
                        else:
                            eligible_doctors.append(doctor)
                    else:
                        if day in self.scheduler[doctor][shift_type]:
                            continue
                        elif day in self.days_unavail[doctor][shift_type]:  # Check if the day and shift are unavailable for the doctor
                            continue
                        elif self.allow_day_night_double==False and (day in self.scheduler[doctor]["Day1"] or day in self.scheduler[doctor]["Day2"]):
                            continue   #don't allow a night followed by day double
                        elif self.allow_night_day_double==False and (day+1 in self.scheduler[doctor]["Day1"] or day+1 in self.scheduler[doctor]["Day2"]):
                            continue   #don't allow a night followed by day double
                        else:
                            eligible_doctors.append(doctor)
                
                if eligible_doctors == []:
                    for doctor in self.doctor_shifts:
                        too_many_straight_shifts=False
                        flattened=self.flatten_schedule(self.scheduler)
                        flattened_doc=flattened[doctor]
                        temp=copy.deepcopy(flattened_doc)
                        temp.append(day)
                        temp.sort()             
                        if self.check_max_consec_days(temp, self.max_days_in_row):
                                too_many_straight_shifts=True
                                
                        if too_many_straight_shifts==True:
                            continue                        
                        elif (self.count_total_shifts(self.scheduler[doctor])-self.tot_prev_shifts[doctor]) >= self.doctor_shifts[doctor][1]:
                            continue
                        elif  self.has_3consecutive_shifts_single_doctor(self.scheduler[doctor], day, shift_type):
                            continue
                        elif shift_type.startswith("Day"):
                            if day in self.scheduler[doctor]["Day1"] or day in self.scheduler[doctor]["Day2"]:
                                continue
                            elif day in self.days_unavail[doctor]["Day"] and shift_type.startswith("Day"):  # Check if the day and shift are unavailable for the doctor
                                continue
                            elif day in self.days_unavail[doctor]["Night"] and shift_type=="Night":  # Check if the day and shift are unavailable for the doctor
                                continue
                            elif self.allow_day_night_double==False and day in self.scheduler[doctor]['Night']:
                                continue
                            elif self.allow_night_day_double==False and (day-1) in self.scheduler[doctor]['Night']:
                                continue
                            else:
                                eligible_doctors.append(doctor)
                        else:
                            if day in self.scheduler[doctor][shift_type]:
                                continue
                            elif day in self.days_unavail[doctor][shift_type]:  # Check if the day and shift are unavailable for the doctor
                                continue
                            elif self.allow_day_night_double==False and (day in self.scheduler[doctor]["Day1"] or day in self.scheduler[doctor]["Day2"]):
                                continue   #don't allow a night followed by day double
                            elif self.allow_night_day_double==False and (day+1 in self.scheduler[doctor]["Day1"] or day+1 in self.scheduler[doctor]["Day2"]):
                                continue   #don't allow a night followed by day double
                            else:
                                eligible_doctors.append(doctor)

                if eligible_doctors == []:
                    schedule_created=False
                    break
                else:
                    schedule_created=True

                doctor = random.choice(eligible_doctors)
                self.scheduler[doctor][shift_type].append(day)
                remaining_shifts.remove((day, shift_type))

            if schedule_created==True:
                print("Scheduler initialized successfully.")
                return

        print("Too many constraints.  Unable to initialize schedule.")


    def is_schedule_legal(self,schedule,display=False,tot_prev_shifts=None):
        if tot_prev_shifts==None:
            tot_prev_shifts={}
            for doc in schedule:
                tot_prev_shifts[doc]=0       
        if self.has_consecutive_shifts(schedule):
            return False, f"Doctor scheduled for three consecutive shifts."
        flattened=self.flatten_schedule(schedule)
        for flattened_sched in flattened.values():
            if self.check_max_consec_days(flattened_sched, self.max_days_in_row):
                return False,f"Doctor scheduled for too many straight days shifts."
        for doctor, shifts in schedule.items():
            # Check for two day shifts on the same day
            day_shifts = shifts['Day1'] + shifts['Day2']
            if len(day_shifts) != len(set(day_shifts)):
                return False, f"Doctor {doctor} is scheduled for two day shifts on the same day."
            
            #if day_night_double not allowed check if this exists
            if self.allow_day_night_double==False:
                if set(day_shifts).intersection(shifts['Night']):
                    return False, f"Day Night Doubles not allowed."
            if self.allow_night_day_double==False:
                temp_days=[x - 1 for x in day_shifts]
                if set(temp_days).intersection(shifts['Night']):
                    return False, f"Night Day Doubles not allowed."
            # Check if the total shifts for the doctor are within the min and max range
            total_shifts = len(day_shifts) + len(shifts['Night'])
            min_shifts, max_shifts = self.doctor_shifts[doctor]
            if (total_shifts-tot_prev_shifts[doctor]) < min_shifts or (total_shifts-tot_prev_shifts[doctor]) > max_shifts:
                return False, f"Doctor {doctor} has an invalid number of shifts."
                
            # Check if the doctor is scheduled for shifts they are unavailable on
            for shift_type, days in shifts.items():
                #print(shift_type," ",days)
                for day in days:
                    if shift_type.startswith("Day"):
                        shft_tmp="Day"
                    else:
                        shft_tmp="Night"
                    if day_type := self.days_unavail[doctor][shft_tmp]:
                        if day in day_type:
                            return False, f"Doctor {doctor} is scheduled for an unavailable shift on day {day}."
        if display==True:
            if self.allow_day_night_double==False:
                print("No day to night double shifts scheduled")
            if self.allow_night_day_double==False:
                print("No night to day double shifts scheduled")
            print("No one scheduled for more than ",self.max_days_in_row," in a row")
            print("No one scheduled on their unavailable day")
            print("all shift number constraints are complied with")
        return True, "Schedule is legal."


    def doctors_below_minimum(self, doctor_shifts, scheduler, tot_prev_shifts):
        below_minimum = []
        for doctor, shifts_range in doctor_shifts.items():
            min_shifts, _ = shifts_range
            total_shifts = sum(len(scheduler[doctor][shift_type]) for shift_type in scheduler[doctor])-tot_prev_shifts[doctor]
            if total_shifts < min_shifts:
                below_minimum.append(doctor)
        return below_minimum

    def flatten_schedule(self,scheduler):
        flattened_schedule = {}
        for doctor, shifts in scheduler.items():
            work_days = []
            for shift_type in ['Day1', 'Day2', 'Night']:
                work_days.extend(shifts.get(shift_type, []))
            work_days.sort()
            flattened_schedule[doctor] = work_days
        return flattened_schedule


    def check_max_consec_days(self, numbers, max_days_in_row):  #takes in value of the flatten_schedule dictionary output individually
        start=min(numbers)
        consecutive_count = 0
        gap_count = 0
        consecutive_counts = []
        gap_counts = []

        last_number = start - 1

        for number in numbers:
            if number - last_number <= 1:
                consecutive_count += 1
            else:
                if consecutive_count > 0:
                    consecutive_counts.append(consecutive_count)
                consecutive_count = 1

                gap_count = number - last_number - 1
                if gap_count > 0:
                    gap_counts.append(gap_count)

            last_number = number
            if consecutive_count>max_days_in_row:
                return True
        return False    

    def count_total_shifts(self, doctor_schedule):
        total_shifts = sum(len(shifts) for shifts in doctor_schedule.values())
        return total_shifts

    def has_3consecutive_shifts_single_doctor(self, doctor_schedule, proposed_day, proposed_shift_type):
        day_shifts = doctor_schedule["Day1"] + doctor_schedule["Day2"]
        night_shifts = doctor_schedule["Night"]
        if proposed_shift_type == "Day1":
            if proposed_day in night_shifts and (proposed_day + 1 in day_shifts):
                return True
            elif proposed_day-1 in night_shifts and proposed_day in night_shifts:
                return True
            elif proposed_day-1 in night_shifts and proposed_day-1 in day_shifts:
                return True 
        elif proposed_shift_type == "Day2":
            if proposed_day in night_shifts and proposed_day + 1 in day_shifts:
                return True
            elif proposed_day-1 in night_shifts and proposed_day in night_shifts:
                return True
            elif proposed_day-1 in night_shifts and proposed_day-1 in day_shifts:
                return True
        elif proposed_shift_type == "Night":
            if (proposed_day in day_shifts and proposed_day + 1 in day_shifts):
                return True
            if (proposed_day-1 in night_shifts and proposed_day  in day_shifts):
                return True 
            if (proposed_day in night_shifts and proposed_day+1  in day_shifts):
                return True 
            if (proposed_day+1 in night_shifts and proposed_day+1  in day_shifts):
                return True 
        return False

    def has_consecutive_shifts(self, schedule):
        for doctor, shifts in schedule.items():
            for day in shifts['Day1']:
                if day in shifts['Night']:
                    if (day+1) in shifts['Day1'] or (day+1) in shifts['Day2']:
                        return True
                    if (day-1) in shifts['Night']:
                        return True
            for day in shifts['Day2']:
                if day in shifts['Night']:
                    if (day+1) in shifts['Day1'] or (day+1) in shifts['Day2']:
                        return True
                    if (day-1) in shifts['Night']:
                        return True
            for day in shifts['Night']:
                if (day+1) in shifts['Day1'] or (day+1) in shifts['Day2']:
                    if (day+1) in shifts['Night']:
                        return True
                if day in shifts['Day1'] or day in shifts['Day2']:
                    if (day-1) in shifts['Night']:
                        return True
        return False

    def print_horizontal(self, doctor_schedules):
        # Create a DataFrame with the required structure
        df = pd.DataFrame(index=doctor_schedules.keys(), columns=range(1, self.num_days_in_month + 1))

        # Fill the DataFrame based on the schedule
        for doctor, shifts in doctor_schedules.items():
            for day in range(1, self.num_days_in_month + 1):
                shift_types = []
                if day in shifts.get('Day1', []):
                    shift_types.append('D1')
                if day in shifts.get('Day2', []):
                    shift_types.append('D2')
                if day in shifts.get('Night', []):
                    shift_types.append('N')

                df.at[doctor, day] = 'DB' if len(shift_types) > 1 else ''.join(shift_types) or '·'

        # Styling function to apply colors
        def color_schedule(val):
            if val == 'D1':
                color = 'green'
            elif val == 'D2':
                color = 'blue'
            elif val == 'N':
                color = 'red'
            elif val == 'DB':
                color = 'purple'
            else:
                color = 'black'
            return f'color: {color}'

        return df.style.applymap(color_schedule)

    def calculate_percentage_days_off(self, schedule):
        percentages = {}
        for doctor in schedule:
            # Initialize counts
            total_requested_days = 0
            days_off_matched = 0

            # Count total requested days and matched days off
            for shift_type in schedule[doctor]:
                if shift_type in ['Day1', 'Day2']:  # Day shifts
                    day_type = 'Day'
                else:  # Night shifts
                    day_type = 'Night'

                requested_days = self.req_days_off[doctor][day_type]
                total_requested_days += len(requested_days)
                days_off_matched += len([day for day in requested_days if day not in schedule[doctor][shift_type]])

            # Calculate percentage
            if total_requested_days > 0:
                percentage_off = (days_off_matched / total_requested_days) * 100
            else:
                percentage_off = 0  # Avoid division by zero

            percentages[doctor] = round(percentage_off, 2)  # Rounded to 2 decimal places
        for each in percentages:
            print(each," percent or requested days off actually off:",percentages[each])

    def actual_vs_requested_shifts(self,schedule):
        self.count_total_shifts(schedule['A'])
        for each in schedule:   
            print(each," req:",self.ideal_num_shifts[each]," actual shifts:",self.count_total_shifts(schedule[each])-self.tot_prev_shifts[each])

    def percentage_of_preferred_shift(self,schedule):
        for each in schedule:
            night_count=len([x for x in schedule[each]['Night'] if x > 0])
            d1_count=len([x for x in schedule[each]['Day1'] if x > 0])
            d2_count=len([x for x in schedule[each]['Day2'] if x > 0])

            if self.shift_type_pref[each]=="Night":
                per=night_count/(night_count+d1_count+d2_count)
            else:
                per=(d1_count+d2_count)/(night_count+d1_count+d2_count)

            print(each," percent of preferred shifts to actual shifts: ",per)

    def mountain_climber(self,iterations,weight=None):
        if weight==None:
            weight={"pattern":.25,"days_off":.25,"num_shifts":.25,"shift_type":.25}
        pattern_loss = self.schedule_pattern_loss(self.scheduler)
        req_daysoff_loss=self.req_daysoff_score(self.scheduler)
        num_shift_var_loss=self.shift_variation_score(self.scheduler)
        prefer_shift_loss=self.shifttype_pref_score(self.scheduler)
        cur_loss=weight["pattern"]*(pattern_loss-35)/(235-35)+weight["days_off"]*req_daysoff_loss/25+weight["num_shifts"]*num_shift_var_loss/25+weight["shift_type"]*prefer_shift_loss/3.5
        print(cur_loss)

        # Total iterations and initial modifications
        total_iterations = iterations
        initial_modifications = 10

        for i in range(total_iterations):
            doctor_schedules_copy = copy.deepcopy(self.scheduler)

            # Calculate the current number of modifications (simulated annealing effect)
            modifications = initial_modifications - (initial_modifications - 1) * i // total_iterations
            for j in range(modifications):
                sched_update = self.modify_schedule(doctor_schedules_copy)
            #print(is_schedule_legal(sched_update, doctor_shifts, days_unavail, max_days_in_row,False,tot_prev_shifts)[0])

            if self.is_schedule_legal(sched_update,False,self.tot_prev_shifts)[0]:
                #print("here")
                pattern_loss = self.schedule_pattern_loss(sched_update)
                req_daysoff_loss=self.req_daysoff_score(sched_update)
                num_shift_var_loss=self.shift_variation_score(sched_update)
                prefer_shift_loss=self.shifttype_pref_score(sched_update)
                new_loss=weight["pattern"]*(pattern_loss-35)/(235-35)+weight["days_off"]*req_daysoff_loss/25+weight["num_shifts"]*num_shift_var_loss/25+weight["shift_type"]*prefer_shift_loss/3.5
                if new_loss < cur_loss:
                    self.scheduler = sched_update
                    cur_loss = new_loss
            
        print(cur_loss)

    def simulated_annealing(self,iterations,weight=None):
        if weight==None:
            weight={"pattern":.25,"days_off":.25,"num_shifts":.25,"shift_type":.25}
        pattern_loss = self.schedule_pattern_loss(self.scheduler)
        req_daysoff_loss=self.req_daysoff_score(self.scheduler)
        num_shift_var_loss=self.shift_variation_score(self.scheduler)
        prefer_shift_loss=self.shifttype_pref_score(self.scheduler)
        cur_loss=weight["pattern"]*(pattern_loss-35)/(235-35)+weight["days_off"]*req_daysoff_loss/25+weight["num_shifts"]*num_shift_var_loss/25+weight["shift_type"]*prefer_shift_loss/3.5
        print("current loss: ",cur_loss)

        # Total iterations and initial modifications
        total_iterations = iterations
        initial_modifications = 10
        temperature=90
        cooling_rate=.99


        for i in range(total_iterations):
            doctor_schedules_copy = copy.deepcopy(self.scheduler)

            # Calculate the current number of modifications (simulated annealing effect)
            modifications = initial_modifications - (initial_modifications - 1) * i // total_iterations
            for j in range(modifications):
                sched_update = self.modify_schedule(doctor_schedules_copy)
            #print(is_schedule_legal(sched_update, doctor_shifts, days_unavail, max_days_in_row,False,tot_prev_shifts)[0])

            if self.is_schedule_legal(sched_update,False,self.tot_prev_shifts)[0]:
                #print("here")
                pattern_loss = self.schedule_pattern_loss(sched_update)
                req_daysoff_loss=self.req_daysoff_score(sched_update)
                num_shift_var_loss=self.shift_variation_score(sched_update)
                prefer_shift_loss=self.shifttype_pref_score(sched_update)
                new_loss=weight["pattern"]*(pattern_loss-35)/(235-35)+weight["days_off"]*req_daysoff_loss/25+weight["num_shifts"]*num_shift_var_loss/25+weight["shift_type"]*prefer_shift_loss/3.5
                if new_loss < cur_loss:
                    accept = True
                else:
                    delta = new_loss - cur_loss
                    probability = math.exp(-delta / temperature)
                    accept = random.random() < probability

                        # Accept the new solution based on the acceptance probability
                if accept:
                    self.scheduler = sched_update
                    cur_loss = new_loss

            temperature *= cooling_rate


            
        print("final loss: ",cur_loss)


    def schedule_pattern_loss(self, doctor_schedules):  #uses above two functions
        flattened=self.flatten_schedule(doctor_schedules)
        loss=0
        for value in flattened.values():
            on,off=self.doctor_schedule_pattern_score(value)
            loss=loss+on+1.8*off
        return loss
    
    def doctor_schedule_pattern_score(self, numbers):  #takes in value of the flatten_schedule dictionary output individually
        consecutive_count = 0
        gap_count = 0
        consecutive_counts = []
        gap_counts = []
        start_consec_indx=[]
        start=min(numbers)
        last_number = start - 1
        start_consec_indx.append(start)
        for number in numbers:
            if number - last_number <= 1:
                consecutive_count += 1
            else:
                start_consec_indx.append(number)
                if consecutive_count > 0:
                    consecutive_counts.append(consecutive_count)

                consecutive_count = 1

                gap_count = number - last_number - 1
                if gap_count > 0:
                    gap_counts.append(gap_count)
            
            last_number = number

        consecutive_counts.append(consecutive_count)

        # Add a final gap count if the end number is greater than the biggest number in the list, considering it inclusive
        final_gap = self.num_days_in_month - numbers[-1]
        if final_gap > 0:
            gap_counts.append(final_gap)

        target_work, target_off=4.5, 2.5
        work_days_score=0
        i=0
        for number in consecutive_counts:
            if number==1 and start_consec_indx[i]!=self.num_days_in_month:
                work_days_score=work_days_score+7
            elif number==2 and start_consec_indx[i]!=self.num_days_in_month-1:
                work_days_score=work_days_score+5
            elif number==3 and start_consec_indx[i]!=self.num_days_in_month-2:
                work_days_score=work_days_score+abs(target_work - number)
            elif number==4 and start_consec_indx[i]!=self.num_days_in_month-3:
                work_days_score=work_days_score+abs(target_work - number)
            elif number==5 and start_consec_indx[i]!=self.num_days_in_month-4:
                work_days_score=work_days_score+abs(target_work - number)
            elif number>5:
                work_days_score=work_days_score+abs(target_work - number)
            i=i+1
            
        off_days_score=0
        for number in gap_counts:
            if number==1:
                off_days_score=off_days_score+2

        return work_days_score,off_days_score

    def req_daysoff_score(self, schedule):
        conflict_count = 0
        for doctor, shifts in schedule.items():
            day_shifts=shifts["Day1"]+shifts["Day2"]
            day_conflicts=set(day_shifts).intersection(self.req_days_off[doctor]['Day'])
            night_conflicts=set(shifts['Night']).intersection(self.req_days_off[doctor]['Night'])
            conflict_count=conflict_count+len(day_conflicts)+len(night_conflicts)
        return conflict_count


    def shift_variation_score(self, doctor_schedules):
        variation_from_ideal_num_shifts=0
        for each in self.ideal_num_shifts:
            variation_from_ideal_num_shifts=variation_from_ideal_num_shifts+abs(self.ideal_num_shifts[each]-(self.count_total_shifts(doctor_schedules[each])-self.tot_prev_shifts[each]))
        return variation_from_ideal_num_shifts

    def shifttype_pref_score(self,doctor_schedules):
        shift_pref_score=0
        for each in doctor_schedules:
            if self.shift_type_pref[each]=="Night":
                shift_pref_score_temp=(len(doctor_schedules[each]['Day1'])+len(doctor_schedules[each]['Day2']))/self.count_total_shifts(doctor_schedules[each])
            else:
                shift_pref_score_temp=len(doctor_schedules[each]['Night'])/self.count_total_shifts(doctor_schedules[each])
            shift_pref_score=shift_pref_score+shift_pref_score_temp
        return shift_pref_score           


    def modify_schedule(self,schedule):  #proposed updated schedule (changes single day)
        # Step 1: Randomly select a shift and a date
        shifts = ['Day1', 'Day2', 'Night']
        shift = random.choice(shifts)
        date =random.randint(1, self.num_days_in_month)

        # Step 2: Randomly select a doctor
        doctors = list(schedule.keys())
        chosen_doctor = random.choice(doctors)
        #print(shift," ",date," ",chosen_doctor)
        # Step 3: Remove the selected date from the doctor who originally had it
        for doctor in doctors:
            if date in schedule[doctor][shift]:
                schedule[doctor][shift].remove(date)
                break

        # Step 4: Add the selected date to the same shift for the randomly chosen doctor
        schedule[chosen_doctor][shift].append(date)
        schedule[chosen_doctor][shift].sort()  # Optional: Sort for better readability
        return schedule
