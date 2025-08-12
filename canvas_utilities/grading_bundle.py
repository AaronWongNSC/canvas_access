from canvas_access.submission import Submission
from canvas_access.util import GET_list, list_to_dict

class GradingBundle:
    def __init__(self, course, assignments, students):
        self.type = 'GradingBundle'
        self.student_ids = list(students.keys())
        self.assignment_ids = list(assignments.keys())
        self.grade_data = {}

        self.submissions = {
            student_id: {} for student_id in self.student_ids
        }
        for student_id, student in students.items():
            for assignment_id, assignment in assignments.items():
                self.submissions[student_id][assignment_id] = None

        url = course.api_url + '/students/submissions?per_page=100'

        self.dict_of_submissions = {}
        student_count = 0
        for student_id, student in students.items():
            student_count += 1
            print(f'Getting submissions for student {student_count} of {len(self.student_ids)} ({student.name})')
            self.dict_of_submissions[student_id] = student.get_submissions()
            for submission_id, submission in self.dict_of_submissions[student_id].items():
                if submission.assignment_id in self.assignment_ids:
                    submission.__dict__['course_id'] = course.id
                    submission.__dict__['course'] = course.name
                    submission.add_Assignment_info(assignments[submission.assignment_id])
                    self.submissions[submission.user_id][submission.assignment_id] = submission

    def count_percent_threshold(self, name, threshold, clusters = None, below = True):
        def check_list(student_id, assignment_id_list):
            count = 0
            assignments = []
            for assignment_id in assignment_id_list:
                if self.submissions[student_id][assignment_id] != None:
                    points_earned = self.submissions[student_id][assignment_id].score
                    points_possible = self.submissions[student_id][assignment_id].assignment_points_possible
                    if points_possible > 0 and points_earned != None:
                        if below and points_earned / points_possible <= threshold:
                            count += 1
                            assignments.append(assignment_id)
                        if not(below) and points_earned / points_possible >= threshold:
                            count += 1
                            assignments.append(assignment_id)
            return count, assignments

        count_name = name +'_count'
        list_name = name +'_list'
        self.grade_data[count_name] = {}
        self.grade_data[list_name] = {}
        if clusters == None:
            for student_id in self.student_ids:
                count, assignments = check_list(student_id, self.assignment_ids)
                self.grade_data[count_name][student_id] = count
                self.grade_data[list_name][student_id] = assignments
        else:
            for student_id in self.student_ids:
                self.grade_data[count_name][student_id] = {
                    cluster_id: 0 for cluster_id in clusters
                }
                self.grade_data[list_name][student_id] = {
                    cluster_id: [] for cluster_id in clusters
                }
                for cluster_id, cluster in clusters.items():
                    count, assignments = check_list(student_id, cluster['assignment_id_list'])
                    self.grade_data[count_name][student_id][cluster_id] = count
                    self.grade_data[list_name][student_id][cluster_id] = assignments
                    