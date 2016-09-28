sql_query = """
                SELECT user_id, custom_user_id, problem_link, time_stamp
                FROM submission
                WHERE status = "AC"
                GROUP BY user_id, custom_user_id, problem_link;
            """

db.solved_problem.truncate()
import datetime
res = db.executesql(sql_query)
for row in res:
    db.solved_problem.insert(user_id=row[0],
                             custom_user_id=row[1],
                             problem_link=row[2],
                             time_stamp=row[3])
