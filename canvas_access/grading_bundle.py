from canvas_access.submission import Submission
from canvas_access.util import GET_list, list_to_dict

class GradingBundle:
    def __init__(self, course, assignments, students):
        self.type = 'GradingBundle'
        self.student_ids = list(students.keys())
        self.assignment_ids = list(assignments.keys())
        self.assignment_group_ids = list(set([assignment.assignment_group_id for _, assignment in assignments.items()]))
        self.assignment_group_map = {
            assignment_id: assignment.assignment_group_id for assignment_id, assignment in assignments.items()
        }
        self.grade_data = {}

        self.submissions = {
            student_id: {
                assignment_group_id: {} for assignment_group_id in self.assignment_group_ids
            } for student_id in self.student_ids
        }
        for student_id, student in students.items():
            for assignment_id, assignment in assignments.items():
                self.submissions[student_id][assignment.assignment_group_id][assignment_id] = None

        url = course.api_url + '/students/submissions?per_page=100'

        self.dict_of_submissions = {}
        for student_id, student in students.items():
            self.dict_of_submissions[student_id] = student.get_submissions()
            for submission_id, submission in self.dict_of_submissions[student_id].items():
                if submission.assignment_id in self.assignment_ids:
                    submission.__dict__['course_id'] = course.id
                    submission.__dict__['course'] = course.name
                    submission.add_Assignment_info(assignments[submission.assignment_id])
                    self.submissions[submission.user_id, submission.assignment_group_id, submission.assignment_id] = submission

    def count_zeros(self):
        self.grade_data['zero_assignments_count'] = {}
        self.grade_data['zero_assignments_list'] = {}
        for student_id in self.student_ids:
            self.grade_data['zero_assignments_count'][student_id] = {
                assignment_group_id: 0 for assignment_group_id in self.assignment_group_ids
            }
            self.grade_data['zero_assignments_list'][student_id] = {
                assignment_group_id: [] for assignment_group_id in self.assignment_group_ids
            }
            for assignment_id in self.assignment_ids:
                if self.submissions[student_id, self.assignment_group_map[assignment_id], assignment_id] != None:
                    if self.submissions[student_id, self.assignment_group_map[assignment_id], assignment_id].score == 0:
                        self.grade_data['zero_assignments_count'][student_id][self.assignment_group_map[assignment_id]] += 1
                        self.grade_data['zero_assignments_list'][student_id][self.assignment_group_map[assignment_id]].append(assignment_id)

    def count_percent_threshold(self, name, threshold, below = True):
        count_name = name +'_count'
        list_name = name +'_list'
        self.grade_data[count_name] = {}
        self.grade_data[list_name] = {}
        for student_id in self.student_ids:
            self.grade_data[count_name][student_id] = {
                assignment_group_id: 0 for assignment_group_id in self.assignment_group_ids
            }
            self.grade_data[list_name][student_id] = {
                assignment_group_id: [] for assignment_group_id in self.assignment_group_ids
            }
            for assignment_id in self.assignment_ids:
                if self.submissions[student_id, self.assignment_group_map[assignment_id], assignment_id] != None:
                    points_earned = self.submissions[student_id, self.assignment_group_map[assignment_id], assignment_id].score
                    points_possible = self.submissions[student_id, self.assignment_group_map[assignment_id], assignment_id].assignment_points_possible
                    if points_possible > 0 and points_earned != None:
                        if below and points_earned / points_possible <= threshold:
                            self.grade_data[count_name][student_id][self.assignment_group_map[assignment_id]] += 1
                            self.grade_data[list_name][student_id][self.assignment_group_map[assignment_id]].append(assignment_id)
                        if not(below) and points_earned / points_possible >= threshold:
                            self.grade_data[count_name][student_id][self.assignment_group_map[assignment_id]] += 1
                            self.grade_data[list_name][student_id][self.assignment_group_map[assignment_id]].append(assignment_id)