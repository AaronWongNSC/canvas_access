"""
Grade_bundle functions for use with canvas_access.

Functions:
    bundle_to_df(): Converts a GradingBundle into a data frame.
    score_by_cluster(): Calculates the total points and percentage earned for a cluster of assignments
    weight_clusters(): Calculates the weighted score of a set of clusters
"""

import pandas as pd

from canvas_access.assignment import Assignment
from canvas_access.course import Course
from canvas_access.user import User
from canvas_access.util import GET_list, list_to_dict

from canvas_grade_bundle.bundle_classes import AssignmentCluster, GradingBundle

def bundle_to_grades(bundle: GradingBundle) -> pd.DataFrame:
    """
    Converts GradingBundle to data frame containing all the grades.
    
    Args:
        bundle (GradingBundle): The grading bundle to be converted
    
    Returns:
        pd.DataFrame: A dataframe whose rows are individual students and whose columns are identifying information and the scores for the assignments.
    """
    data = []

    points_possible = {}
    for assignment_id in bundle.assignment_ids:
        assignment = bundle.assignments[assignment_id]
        points_possible[f'{assignment.name} ({assignment.id})'] = assignment.points_possible
    data.append(points_possible)

    for student_id in bundle.student_ids:
        portfolio = bundle.portfolios[student_id]
        student_data = {}
        for assignment_id in bundle.assignment_ids:
            submission = portfolio.submissions[assignment_id]
            student_data[f'{submission.assignment_name} ({assignment_id})'] = submission.score
        data.append(student_data)
    return pd.DataFrame(data).set_axis(['Points Possible'] + [student_id for student_id in bundle.student_ids], axis = 'index')

def bundle_to_names(bundle: GradingBundle, columns: list[str] = ['Name', 'ID'], extra_rows: list[str] = ['Points Possible']) -> pd.DataFrame:
    """
    Converts GradingBundle to data frame containing identifying information and extra rows.
    
    Args:
        bundle (GradingBundle): The grading bundle to be converted.
        columns (list[str]): Identifying columns, default is name and ID.
        extra_rows (list[str]): Creates extra rows at the top. The default is one row for the points possible.
    
    Returns:
        pd.DataFrame: A dataframe whose rows are individual students with identifying information plus some number of additional rows on top.
    """
    data = {}
    for column in columns:
        if column == 'Name':
            data['Name'] = ['' for _ in extra_rows] + [bundle.portfolios[student_id].student_name for student_id in bundle.student_ids]
        elif column == 'ID':
            data['ID'] = ['' for _ in extra_rows] + [student_id for student_id in bundle.student_ids]
        else:
            data[column] = ['' for _ in extra_rows] + [bundle.portfolios[student_id].__dict__[column] for student_id in bundle.student_ids]
    return pd.DataFrame(data).set_axis(['Points Possible'] + [student_id for student_id in bundle.student_ids], axis = 'index')

def count_in_cluster(name: str, bundle: GradingBundle, cluster: AssignmentCluster, submission_attribute: str, comparison_type: str = '==', comparison_value: str|float = 0, count_missing: bool = True) -> pd.Series:
    """
    Counts the number of assignments in the cluster of the given submission_attribute that meet the comparison with the threshold.
    
    Args:
        name (str): Name of the data
        bundle (GradingBundle): The grade bundle containing the course data.
        cluster (AssignmentCluster): The assignment cluster to be counted.
        submission_attribute (str): The name of the attribute to be observed.
        comparison_type (str): The type of comparison to be made. Invalid strings result in using '=='.
            '==': Count when it is equal to the comparison
            '!=': Count when it is equal to the comparison
            '<': Count when it is less than the comparison
            '<=': Count when it is less than or equal to the comparison
            '>': Count when it is greater than the comparison
            '>=': Count when it is greater than or equal to the comparison
        comparison_value (str|float): The string or value to comare against.
        count_missing: Count if the attribute is missing.
    
    Returns:
        pd.Series: A series that represents the count.
    """

    assignment_dict = get_by_condition(bundle, cluster, submission_attribute, comparison_type, comparison_value, count_missing)
    count_list = []
    for student_id in bundle.student_ids:
        count_list.append(len(assignment_dict[student_id]))

    final_count = pd.Series(count_list)
    final_count.name = name
    final_count.index = [student_id for student_id in bundle.student_ids]

    return final_count

def get_by_condition(bundle: GradingBundle, cluster: AssignmentCluster, submission_attribute: str, comparison_type: str = '==', comparison_value: str|float = 0, count_missing: bool = True) -> dict:
    """
    Creates a dictionary whose keys are student IDs and whose values are dicts of Submissions (indexed by assignment_id) that meet the condition.
    
    Args:
        bundle (GradingBundle): The grade bundle containing the course data.
        cluster (AssignmentCluster): The assignment cluster to be counted.
        submission_attribute (str): The name of the attribute to be observed.
        comparison_type (str): The type of comparison to be made. Invalid strings result in using '=='.
            '==': Count when it is equal to the comparison
            '!=': Count when it is equal to the comparison
            '<': Count when it is less than the comparison
            '<=': Count when it is less than or equal to the comparison
            '>': Count when it is greater than the comparison
            '>=': Count when it is greater than or equal to the comparison
        comparison_value (str|float): The string or value to comare against.
        count_missing: Count if the attribute is missing.
    
    Returns:
        dict: The keys of the dict are student IDs and the value is the dict of Submissions that met the condition.
    """
    result_dict = {}
    for student_id in bundle.student_ids:
        portfolio = bundle.portfolios[student_id]
        student_result = {}
        for assignment_id in cluster.assignment_ids:
            if submission_attribute in portfolio.submissions[assignment_id].__dict__.keys():
                if comparison_type == '!=':
                    if portfolio.submissions[assignment_id].__dict__[submission_attribute] != comparison_value:
                        student_result[assignment_id] = portfolio.submissions[assignment_id]
                elif comparison_type == '>':
                    if portfolio.submissions[assignment_id].__dict__[submission_attribute] > comparison_value:
                        student_result[assignment_id] = portfolio.submissions[assignment_id]
                elif comparison_type == '<':
                    if portfolio.submissions[assignment_id].__dict__[submission_attribute] < comparison_value:
                        student_result[assignment_id] = portfolio.submissions[assignment_id]
                elif comparison_type == '>=':
                    if portfolio.submissions[assignment_id].__dict__[submission_attribute] >= comparison_value:
                        student_result[assignment_id] = portfolio.submissions[assignment_id]
                elif comparison_type == '<=':
                    if portfolio.submissions[assignment_id].__dict__[submission_attribute] <= comparison_value:
                        student_result[assignment_id] = portfolio.submissions[assignment_id]
                else:
                    if portfolio.submissions[assignment_id].__dict__[submission_attribute] == comparison_value:
                        student_result[assignment_id] = portfolio.submissions[assignment_id]
            else:
                if count_missing:
                    student_result[assignment_id] = portfolio.submissions[assignment_id]
        result_dict[student_id] = student_result

    return result_dict

def make_gradebook(course: Course) -> pd.DataFrame:
    """
    Converts GradingBundle to data frame that is a gradebook with full grades and assignment groups.
    
    Args:
        course (Course): The course from which to create the gradebook
    
    Returns:
        pd.DataFrame: A dataframe that represents the gradebook
    """
    students = course.get_users()
    assignments = course.get_assignments()
    assignment_groups = course.get_assignment_groups()
    bundle = GradingBundle(course, assignments, students)

    clusters = []
    for assignment_group_id, assignment_group in assignment_groups.items():
        assignments = assignment_group.get_assignments()
        assignment_ids = [assignment_id for assignment_id in assignments]
        clusters.append(AssignmentCluster(assignment_group.name, assignment_ids, assignment_group.group_weight))

    cluster_dfs = []
    for cluster in clusters:
        cluster_dfs.append(score_by_cluster(bundle, cluster))

    final_grades = weight_clusters(bundle, clusters)

    return pd.concat([bundle_to_names(bundle), bundle_to_grades_df(bundle)] + cluster_dfs + [final_grades], axis = 1)

def score_by_cluster(bundle: GradingBundle, cluster: AssignmentCluster) -> pd.DataFrame:
    """
    Calculates points and percentages for each cluster.
    
    Args:
        bundle (GradingBundle): The grading bundle to be converted
    
    Returns:
        pd.DataFrame: A dataframe whose rows are individual students and whose columns are identifying information and the scores for the assignments.
    """
    # Count up possible points
    points_possible = 0
    for assignment_id in cluster.assignment_ids:
        if 'points_possible' in bundle.assignments[assignment_id].__dict__.keys():
            points_possible += bundle.assignments[assignment_id].points_possible

    # Count up student scores
    points_earned_list = []
    for student_id in bundle.student_ids:
        portfolio = bundle.portfolios[student_id]
        points_earned = 0
        for assignment_id in cluster.assignment_ids:
            if 'score' in portfolio.submissions[assignment_id].__dict__.keys():
                if portfolio.submissions[assignment_id].score != None:
                    points_earned += portfolio.submissions[assignment_id].score
        points_earned_list.append(points_earned)

    if points_possible == 0:
        percents = [0] + [0 for _ in points_earned_list]
    else:
        percents = [100] + [ points_earned/points_possible * 100 for points_earned in points_earned_list ]

    data = {
        f'{cluster.name} (Points)': [points_possible] + points_earned_list,
        f'{cluster.name} (Percent)': percents,
    }

    return pd.DataFrame(data).set_axis(['Points Possible'] + [student_id for student_id in bundle.student_ids], axis = 'index')

def weight_clusters(bundle: GradingBundle, clusters: list[AssignmentCluster]) -> pd.Series:
    """
    Calculates the weighted grade of a collection of clusters. If weights are not provided, it will calculate based on total points.
    
    Args:
        bundle (GradingBundle): The grading bundle to be converted
        clusters (list[AssignmentCluster]): The list of clusters to be calculated.
    
    Returns:
        pd.Series: A series named 'Final Grade' that contains the grade as a percent.
    """
    total_weight = sum([cluster.weight for cluster in clusters if (cluster.weight != None and len(cluster.assignment_ids))])
    cluster_scores = [ score_by_cluster(bundle, cluster) for cluster in clusters]
    if total_weight > 0:
        final_grade = sum([cluster.weight * df[f'{cluster.name} (Percent)'] for df, cluster in zip(cluster_scores, clusters)]) / total_weight
    else:
        total_points = sum([df[f'{cluster.name} (Points)'].get('Points Possible') for df, cluster in zip(cluster_scores, clusters) ])
        points_earned = sum([df[f'{cluster.name} (Points)'] for df, cluster in zip(cluster_scores, clusters)])
        if total_points == 0:
            final_grade = pd.Series()
        else:
            final_grade = points_earned / total_points * 100
    final_grade.name = 'Final Grade'
    final_grade.index = ['Points Possible'] + [student_id for student_id in bundle.student_ids]

    return final_grade
