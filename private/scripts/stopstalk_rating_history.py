"""
    Copyright (c) 2015-2018 Raj Patel(raj454raj@gmail.com), StopStalk

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
"""

"""
@Usage
1. Single user with the user_id (custom/normal in params)
    python web2py.py -S stopstalk -M -R applications/stopstalk/private/scripts/stopstalk_rating_history.py -A single <user_id> <normal/custom>
2. All the users (including custom users)
    python web2py.py -S stopstalk -M -R applications/stopstalk/private/scripts/stopstalk_rating_history.py -A complete
"""

import sys
import datetime
import utilities

stable = db.submission
atable = db.auth_user
cftable = db.custom_friend
BATCH_SIZE = 500

def get_sql_result(start_id, end_id, custom):
    column_name = "custom_user_id" if custom else "user_id"
    query = """
    SELECT %(column_name)s, time_stamp, problem_link, status
    FROM submission
    WHERE %(column_name)s BETWEEN %(start_id)d AND %(end_id)d
    ORDER BY %(column_name)s, time_stamp
            """ % ({"column_name": column_name,
                    "start_id": start_id,
                    "end_id": end_id})
    return db.executesql(query)

def update_stopstalk_rating(user_id, user_submissions, custom):
    final_rating = utilities.get_stopstalk_rating_history_dict(user_submissions)
    if final_rating == {}:
        print user_id, custom, "No submissions"
        return

    atable = db.auth_user
    cftable = db.custom_friend

    today = str(datetime.datetime.now().date())
    current_rating = sum(final_rating[today])

    print user_id, custom, current_rating

    update_params = dict(stopstalk_rating=int(current_rating))
    if custom:
        cftable(user_id).update_record(**update_params)
    else:
        atable(user_id).update_record(**update_params)

def compute_group_ratings(last_id, custom):
    column_name = "custom_user_id" if custom else "user_id"
    start = 0

    for i in xrange(last_id / BATCH_SIZE + 1):
        res = get_sql_result(i * BATCH_SIZE,
                             (i + 1) * BATCH_SIZE,
                             custom)
        if len(res) == 0:
            # Batch had no submission
            continue
        prev_user_id = res[0][0]
        user_submissions = []
        for submission in res:
            user_id, time_stamp, problem_link, status = submission
            if user_id == prev_user_id:
                user_submissions.append({"user_id": user_id,
                                         "time_stamp": time_stamp,
                                         "problem_link": problem_link,
                                         "status": status})
            else:
                update_stopstalk_rating(prev_user_id, user_submissions, custom)
                user_submissions = [{"user_id": user_id,
                                     "time_stamp": time_stamp,
                                     "problem_link": problem_link,
                                     "status": status}]
                prev_user_id = user_id
        update_stopstalk_rating(prev_user_id, user_submissions, custom)
        start += BATCH_SIZE

def compute_single_rating(user_id, custom):
    res = get_sql_result(user_id, user_id, custom)
    user_submissions = []
    for submission in res:
        _user_id, time_stamp, problem_link, status = submission
        user_submissions.append({"user_id": _user_id,
                                 "time_stamp": time_stamp,
                                 "problem_link": problem_link,
                                 "status": status})
    update_stopstalk_rating(user_id, user_submissions, custom)


if __name__ == "__main__":
    if sys.argv[1] == "complete":
        last_user_id = db(atable).select(orderby=~atable.id,
                                         limitby=(0, 1)).first().id
        last_custom_user_id = db(cftable).select(orderby=~cftable.id,
                                                 limitby=(0, 1)).first().id

        compute_group_ratings(last_custom_user_id, True)
        compute_group_ratings(last_user_id, False)
    elif sys.argv[1] == "single":
        user_id = int(sys.argv[2])
        custom = (sys.argv[3] == "custom")
        compute_single_rating(user_id, custom)
    else:
        print "Invalid command line arguments"
