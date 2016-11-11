db.combined_rating.truncate()
sql_query = """
                INSERT INTO combined_rating (user_id, stopstalk_handle, curr_rating)
                SELECT a.id, a.stopstalk_handle, CAST(a.rating AS UNSIGNED) FROM auth_user AS a;
            """

db.executesql(sql_query)

sql_query = """
                INSERT INTO combined_rating (custom_user_id, stopstalk_handle, curr_rating)
                SELECT c.id, c.stopstalk_handle, CAST(c.rating AS UNSIGNED) FROM custom_friend AS c;
            """

db.executesql(sql_query)