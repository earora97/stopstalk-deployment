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
import utilities
import sites
import gevent
from gevent import monkey
gevent.monkey.patch_all(thread=False)

now_time = datetime.datetime.now()
today = now_time.strftime("%Y-%m-%d")
before_30 = (now_time - \
             datetime.timedelta(30)).strftime("%Y-%m-%d")

change_counts = {}

# ==============================================================================
def _get_date_as_string(value):
    return str(value) if isinstance(value, datetime.date) else value

# ==============================================================================
class TagHandler():
    # --------------------------------------------------------------------------
    @staticmethod
    def column_value():
        return "tags"

    # --------------------------------------------------------------------------
    @staticmethod
    def conditional(dal_object):
        """
            @params dal_object (DAL relation or Record object): Object on which the conditions should be applied
        """
        return (_get_date_as_string(dal_object.tags_added_on) >= before_30) & \
               (dal_object.tags == "['-']")

    # --------------------------------------------------------------------------
    @staticmethod
    def update_params(link, prev_value, curr_value):
        curr_value = "['-']" if curr_value == [] else str(curr_value)
        if prev_value != curr_value and prev_value == "['-']":
            print "Updated tags", link, prev_value, "->", curr_value
            return dict(tags=curr_value if curr_value != "['-']" else "['-']",
                        tags_added_on=today)
        else:
            print "No-change in tags", link
            return dict()

# ==============================================================================
class EditorialHandler():
    # --------------------------------------------------------------------------
    @staticmethod
    def column_value():
        return "editorial_link"

    # --------------------------------------------------------------------------
    @staticmethod
    def conditional(dal_object):
        """
            @params dal_object (DAL relation or Record object): Object on which the conditions should be applied
        """
        return ((dal_object.editorial_added_on == None) |
                (_get_date_as_string(dal_object.editorial_added_on) >= before_30)) & \
               ((dal_object.editorial_link == None) | \
                (dal_object.editorial_link == ""))

    # --------------------------------------------------------------------------
    @staticmethod
    def update_params(link, prev_value, curr_value):
        if curr_value is not None and prev_value is None:
            print "Updated editorial_link", link, prev_value, "->", curr_value
            return dict(editorial_link=curr_value,
                        editorial_added_on=today)
        else:
            print "No-change in editorial_link", link
            return dict()

# ==============================================================================
genre_classes = {
    "tags": TagHandler,
    "editorials": EditorialHandler
}

# ------------------------------------------------------------------------------
def refresh_problem_details():
    ptable = db.problem

    # Problems having tags = ["-"]
    # Possibilities of such case -
    #   => There are actually no tags for the problem
    #   => The problem is from a contest and they'll be
    #      updating tags shortly(assuming 15 days)
    #   => Page was not reachable due to some reason
    tags_query = tag_conditional(ptable)

    editorial_query = editorial_conditional(ptable)

    # If tag or editorial retrieval is required
    query = tags_query | editorial_query
    results = db(query).select()

    threads = []
    workers = 49
    for i in xrange(0, len(results), workers):
        threads = []
        # O God I am so smart !!
        for problem_record in results[i : i + workers]:
            threads.append(gevent.spawn(get_problem_details,
                                        problem_record))

        gevent.joinall(threads)

    return

# ------------------------------------------------------------------------------
def tag_conditional(dal_object):
    """
        @params dal_object (DAL relation or Record object): Object on which the conditions should be applied
    """
    return (_get_date_as_string(dal_object.tags_added_on) >= before_30) & \
           (dal_object.tags == "['-']")

# ------------------------------------------------------------------------------
def editorial_conditional(dal_object):
    """
        @params dal_object (DAL relation or Record object): Object on which the conditions should be applied
    """
    return ((dal_object.editorial_added_on == None) |
            (_get_date_as_string(dal_object.editorial_added_on) >= before_30)) & \
           ((dal_object.editorial_link == None) | \
            (dal_object.editorial_link == ""))

# ------------------------------------------------------------------------------
def get_problem_details(problem_record):
    update_params = dict()
    link = problem_record.link
    site = utilities.urltosite(link)
    Site = getattr(sites, site.lower()).Profile
    try:
        details = Site.get_problem_details(problem_record.link)
    except AttributeError:
        # get_problem_details not implemented for this site
        print "get_problem_details not implemented for", link
        return

    for genre in genre_classes:
        this_class = genre_classes[genre]
        column_value = this_class.column_value()
        if this_class.conditional(problem_record):
            curr_update_params = this_class.update_params(
                                    problem_record.link,
                                    problem_record[column_value],
                                    details[column_value]
                                 )
            if len(curr_update_params):
                update_params.update(curr_update_params)
                change_counts[column_value]["updated"] += 1

        change_counts[column_value]["total"] += 1

    if len(update_params) > 0:
        problem_record.update_record(**update_params)

    return

if __name__ == "__main__":
    for genre in genre_classes:
        change_counts[genre_classes[genre].column_value()] = {
            "updated": 0, "total": 0
        }

    refresh_problem_details()

    print change_counts
