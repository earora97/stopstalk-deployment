"""
    Copyright (c) 2015-2020 Raj Patel(raj454raj@gmail.com), StopStalk

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

import json
import utilities
from stopstalk_constants import *

from gluon import current, IMG, DIV, TABLE, THEAD, HR, H5, \
                  TBODY, TR, TH, TD, A, SPAN, INPUT, I, P, \
                  TEXTAREA, SELECT, OPTION, URL, BUTTON, TAG

# ==============================================================================
class BaseCard:
    # --------------------------------------------------------------------------
    def __init__(self, user_id, card_type):
        self.user_id = user_id
        self.card_type = card_type

    # --------------------------------------------------------------------------
    def get_html(self, **args):
        if self.card_type == "simple_with_cta":
            return DIV(DIV(DIV(SPAN(args["card_title"], _class="card-title"),
                               P(args["card_text"]),
                                _class="card-content " + \
                                       args["card_text_color_class"]),
                           DIV(A(args["card_action_text"],
                                 _href=args["card_action_url"],
                                 _class="btn btn-default",
                                 _target="_blank"),
                               _class="card-action right-text"),
                           _class="card " + args["card_color_class"]),
                       _class="col s4")
        elif self.card_type == "simple_with_multiple_ctas":
            return DIV(DIV(DIV(SPAN(args["card_title"], _class="card-title"),
                               P(args["card_text"]),
                                _class="card-content " + \
                                       args["card_text_color_class"]
                               ),
                           DIV(*args["cta_links"],
                               _class="card-action"),
                           _class="card " + args["card_color_class"]),
                       _class="col s4")
        elif self.card_type == "with_html":
            return DIV(DIV(DIV(SPAN(args["card_title"], _class="card-title"),
                               args["custom_html"],
                                _class="card-content " + \
                                       args["card_text_color_class"]),
                           DIV(A(args["card_action_text"],
                                 _href=args["card_action_url"],
                                 _class="btn btn-default",
                                 _target="_blank"),
                               _class="card-action right-text"),
                           _class="card " + args["card_color_class"]),
                       _class="col s4")

    # --------------------------------------------------------------------------
    def get_data(self):
        pass

    # --------------------------------------------------------------------------
    def get_from_cache(self):
        value = current.REDIS_CLIENT.get(self.cache_key)
        return json.loads(value) if value else None

    # --------------------------------------------------------------------------
    def set_to_cache(self, value):
        current.REDIS_CLIENT.set(self.cache_key,
                                 json.dumps(value),
                                 ex=CARD_REDIS_CACHE_TTL)

# ==============================================================================
class StreakCard(BaseCard):
    # --------------------------------------------------------------------------
    def __init__(self, user_id, kind):
        self.genre = StreakCard.__name__
        self.kind = kind
        self.key_name = "curr_%s_streak" % self.kind
        self.user_id = user_id
        self.card_title = "Keep your %s streak going!" % self.kind
        self.stats = None
        BaseCard.__init__(self, user_id, "simple_with_cta")

    # --------------------------------------------------------------------------
    def get_html(self):
        streak_value = self.get_data()
        if self.kind == "day":
            card_text = "You're at a %d day streak. Keep solving a new problem everyday!" % streak_value
            card_action_text = "Pick a Problem"
        elif self.kind == "accepted":
            card_text = "You're at a %d accepted problem streak. Let the greens rain!" % streak_value
            card_action_text = "Pick a Problem"
        else:
            return "FAILURE"

        card_action_url = URL("default",
                              "cta_handler",
                              vars=dict(kind="random"))

        card_html = BaseCard.get_html(self, **dict(
                       card_title=self.card_title,
                       card_text=card_text,
                       card_action_text=card_action_text,
                       card_action_url=card_action_url,
                       card_color_class="white",
                       card_text_color_class="black-text"
                    ))
        return card_html

    # --------------------------------------------------------------------------
    def get_data(self):
        return self.stats[self.key_name]

    # --------------------------------------------------------------------------
    def should_show(self):
        self.stats = utilities.get_rating_information(self.user_id, False)
        return True
        return self.stats[self.key_name] > 0

# ==============================================================================
class SuggestProblemCard(BaseCard):
    # --------------------------------------------------------------------------
    def __init__(self, user_id):
        self.genre = SuggestProblemCard.__name__
        self.user_id = user_id
        self.card_title = "Mood"
        BaseCard.__init__(self, self.user_id, "simple_with_multiple_ctas")

    # --------------------------------------------------------------------------
    def get_html(self):
        streak_value = self.get_data()
        card_text = "Let's find you some problem that you can start solving."
        card_action_url = URL("default",
                              "cta_handler",
                              vars=dict(kind="random"))

        card_html = BaseCard.get_html(self, **dict(
                       card_title=self.card_title,
                       card_text=card_text,
                       card_action_text="abcd",
                       cta_links=[
                            A("Easy",
                              _href=URL("default", "cta_handler",
                                        vars=dict(kind="suggested_tag",
                                                  tag_category="Easy")),
                              _class="btn btn-default",
                              _target="_blank"),
                            " ",
                            A("Medium",
                              _href=URL("default", "cta_handler",
                                        vars=dict(kind="suggested_tag",
                                                  tag_category="Medium")),
                              _class="btn btn-default",
                              _target="_blank"),
                            " ",
                            A("Hard",
                              _href=URL("default", "cta_handler",
                                        vars=dict(kind="suggested_tag",
                                                  tag_category="Hard")),
                              _class="btn btn-default",
                              _target="_blank"),
                       ],
                       card_color_class="white",
                       card_text_color_class="black-text"
                    ))
        return card_html

    # --------------------------------------------------------------------------
    def get_data(self):
        pass

    # --------------------------------------------------------------------------
    def should_show(self):
        return True

# ==============================================================================
class UpcomingContestCard(BaseCard):

    # --------------------------------------------------------------------------
    def __init__(self, user_id):
        self.genre = UpcomingContestCard.__name__
        self.user_id = user_id
        self.card_title = "Upcoming contests"
        self.cache_key = CARD_CACHE_REDIS_KEYS["upcoming_contests"]
        BaseCard.__init__(self, self.user_id, "with_html")

    # --------------------------------------------------------------------------
    def get_html(self):
        contest_data = self.get_data()
        card_content_table = TABLE(
            _class="bordered centered highlight",
            _style="line-height: 20px"
        )
        tbody = TBODY()

        for contest in contest_data:
            tbody.append(TR(TD(contest[0]),
                            TD(IMG(_src=current.get_static_url(
                                            "images/%s_small.png" % str(contest[1])
                                        ),
                                   _style="height: 30px; width: 30px;")),
                            TD(A(I(_class="fa fa-external-link-square"),
                                 _class="btn-floating btn-small accent-4 green view-contest",
                                 _href=contest[2],
                                 _target="_blank"))))

        card_content_table.append(tbody)

        card_action_url = URL("default",
                              "cta_handler",
                              vars=dict(kind="random"))

        card_html = BaseCard.get_html(self, **dict(
                       card_title=self.card_title,
                       custom_html=card_content_table,
                       card_action_text="View all",
                       card_action_url=URL("default", "contests"),
                       card_color_class="white",
                       card_text_color_class="black-text"
                    ))
        return card_html

    # --------------------------------------------------------------------------
    def get_data(self):
        value = self.get_from_cache()
        if value:
            return value

        _, upcoming = utilities.get_contests()
        data = []
        for contest in upcoming[:2]:
            data.append((
                contest["Name"],
                str(contest["Platform"]).lower(),
                contest["url"]
            ))

        self.set_to_cache(data)
        return data

    # --------------------------------------------------------------------------
    def should_show(self):
        return True

# ==============================================================================
class RecentSubmissionsCard(BaseCard):
    # --------------------------------------------------------------------------
    def __init__(self, user_id):
        self.genre = RecentSubmissionsCard.__name__
        self.user_id = user_id
        self.card_title = "Recent Friends' submissions"
        self.cache_key = CARD_CACHE_REDIS_KEYS["recent_submissions_prefix"] + str(user_id)
        self.final_data = None
        BaseCard.__init__(self, user_id, "with_html")

    # --------------------------------------------------------------------------
    def get_html(self):
        submissions_data = self.get_data()
        card_action_url = URL("default",
                              "submissions",
                              args=[1])

        card_content_table = TABLE(
            _class="bordered highlight"
        )
        tbody = TBODY()

        for row in submissions_data:
            user_record = utilities.get_user_records([row[0]], "id", "id", True)
            tr = TR(TD(A(user_record.first_name + " " + user_record.last_name,
                                 _href=URL("user", "profile",
                                           args=user_record.stopstalk_handle,
                                           extension=False),
                                 _target="_blank")))

            td = TD()
            for site in row[1]:
                if site == "total":
                    continue
                else:
                    td.append(SPAN(IMG(_src=current.get_static_url(
                                                "images/%s_small.png" % str(site).lower()
                                            ),
                                       _style="height: 18px; width: 18px; margin-bottom: -4px;"),
                                   " " + str(row[1][site]),
                                   _style="padding-right: 10px;"))
            tr.append(td)
            tbody.append(tr)

        card_content_table.append(tbody)

        card_html = BaseCard.get_html(self, **dict(
                       card_title=self.card_title,
                       custom_html=card_content_table,
                       card_action_text="View all",
                       card_action_url=card_action_url,
                       card_color_class="white",
                       card_text_color_class="black-text"
                    ))
        return card_html

    # --------------------------------------------------------------------------
    def get_data(self):
        return self.final_data if self.final_data else "FAILURE"

    # --------------------------------------------------------------------------
    def should_show(self):
        final_data = self.get_from_cache()
        if final_data:
            pass
        else:
            import datetime
            db = current.db
            stable = db.submission
            friends, _ = utilities.get_friends(self.user_id)
            today = datetime.datetime.today()
            last_week = today - datetime.timedelta(days=150)
            rows = db.executesql("""
                SELECT user_id, site, count(*)
                FROM submission
                WHERE time_stamp >= "%s" AND
                    user_id in (%s) AND custom_user_id is NULL
                GROUP BY 1, 2
                ORDER BY 3 DESC
            """ % (str(last_week.date()),
                   ",".join([str(x) for x in friends])))
            final_hash = {}
            for row in rows:
                if row[0] not in final_hash:
                    final_hash[row[0]] = {"total": 0}
                final_hash[row[0]][row[1]] = int(row[2])
                final_hash[row[0]]["total"] += int(row[2])

            final_data = sorted(final_hash.items(),
                                key=lambda x: x[1]["total"],
                                reverse=True)[:2]
            self.set_to_cache(final_data)

        if len(final_data) > 0:
            self.final_data = final_data
            return True
        return False

# ==============================================================================
class AddMoreFriendsCard(BaseCard):
    # --------------------------------------------------------------------------
    def __init__(self, user_id):
        self.genre = AddMoreFriendsCard.__name__
        self.user_id = user_id
        self.card_title = "Add more friends"
        self.cache_key = CARD_CACHE_REDIS_KEYS["add_more_friends_prefix"] + str(self.user_id)
        BaseCard.__init__(self, user_id, "simple_with_cta")

    # --------------------------------------------------------------------------
    def get_html(self):
        data = self.get_data()
        card_text = "You have %d friends on StopStalk. To make best use of StopStalk, we recommend you to add more friends for best Competitive Programming learning experience." % data["friend_count"]
        card_action_text = "Show me"

        card_action_url = URL("default", "search",
                              vars={"institute": data["institute"]})

        card_html = BaseCard.get_html(self, **dict(
                       card_title=self.card_title,
                       card_text=card_text,
                       card_action_text=card_action_text,
                       card_action_url=card_action_url,
                       card_color_class="white",
                       card_text_color_class="black-text"
                    ))
        return card_html

    # --------------------------------------------------------------------------
    def get_data(self):
        cache_value = self.get_from_cache()
        if cache_value:
            return cache_value

        record = utilities.get_user_records([self.user_id], "id", "id", True)
        result = dict(institute=record["institute"],
                      friend_count=self.friend_count)
        self.set_to_cache(result)
        return result

    # --------------------------------------------------------------------------
    def should_show(self):
        db = current.db
        self.friend_count = db(db.following.follower_id == self.user_id).count()
        return True
        return self.friend_count < 3

# ==============================================================================
class JobProfileCard(BaseCard):
    # --------------------------------------------------------------------------
    def __init__(self, user_id):
        self.genre = JobProfileCard.__name__
        self.user_id = user_id
        self.card_title = "Looking for job!"
        self.cache_key = CARD_CACHE_REDIS_KEYS["job_profile_prefix"] + str(self.user_id)
        BaseCard.__init__(self, user_id, "simple_with_cta")

    # --------------------------------------------------------------------------
    def get_html(self):
        card_text = "I am looking for a job and I want StopStalk to reach out to me for matching opportunities. Let me update my preferences."
        card_action_text = "Update job preferences"

        card_action_url = URL("default", "job_profile")

        card_html = BaseCard.get_html(self, **dict(
                       card_title=self.card_title,
                       card_text=card_text,
                       card_action_text=card_action_text,
                       card_action_url=card_action_url,
                       card_color_class="white",
                       card_text_color_class="black-text"
                    ))
        return card_html

    # --------------------------------------------------------------------------
    def get_data(self):
        pass
    # --------------------------------------------------------------------------
    def should_show(self):
        db = current.db
        query = (db.resume_data.user_id == self.user_id)
        return db(query).select().first() is None

# ==============================================================================
class LinkedAccountsCard(BaseCard):
    # --------------------------------------------------------------------------
    def __init__(self, user_id):
        self.genre = JobProfileCard.__name__
        self.user_id = user_id
        self.card_title = "Link more accounts"
        self.cache_key = CARD_CACHE_REDIS_KEYS["more_accounts_prefix"] + str(self.user_id)
        BaseCard.__init__(self, user_id, "simple_with_cta")

    # --------------------------------------------------------------------------
    def get_html(self):
        count = self.get_data()
        card_text = "You have %d accounts linked with StopStalk. Update your profile with more handles for a very deedy StopStalk profile." % count
        card_action_text = "Update now"

        card_action_url = URL("user", "update_details")

        card_html = BaseCard.get_html(self, **dict(
                       card_title=self.card_title,
                       card_text=card_text,
                       card_action_text=card_action_text,
                       card_action_url=card_action_url,
                       card_color_class="white",
                       card_text_color_class="black-text"
                    ))
        return card_html

    # --------------------------------------------------------------------------
    def get_data(self):
        cache_value = self.get_from_cache()
        if cache_value:
            return cache_value

        self.set_to_cache(self.handle_count)
        return self.handle_count

    # --------------------------------------------------------------------------
    def should_show(self):
        handle_count = 0
        db = current.db
        record = utilities.get_user_records([self.user_id], "id", "id", True)
        for site in current.SITES:
            if record[site.lower() + "_handle"]:
                handle_count += 1
        self.handle_count = handle_count
        return True
        return handle_count < 3

# ==============================================================================