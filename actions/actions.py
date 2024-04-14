# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import AllSlotsReset, Restarted
from SPARQLWrapper import SPARQLWrapper, JSON

# 1


class GetCourseList(Action):

    def name(self) -> Text:
        return "get_course_list"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # query
        sparql = SPARQLWrapper(
            "http://localhost:3030/Data/sparql", agent='Rasabot agent')
        sparql.setQuery("""
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            prefix xsd: <http://www.w3.org/2001/XMLSchema#>
            prefix foaf: <http://xmlns.com/foaf/0.1/>
            prefix dbo: <http://dbpedia.org/ontology/>
            prefix uni: <http://uni.com/schema#>
            prefix owl: <http://www.w3.org/2002/07/owl#>

            SELECT ?cName
            WHERE{
            ?uni rdf:type dbo:University.
            ?uni uni:name ?uniName.
            ?uni  uni:offers ?course.
            ?course uni:subject ?cName.
            }
            LIMIT 100


            """)
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()
        if (len(result['results']['bindings']) == 0):
            dispatcher.utter_message(
                text="Sorry, I was unable to find any results for that question.")
        else:
            for res in result['results']['bindings']:
                dispatcher.utter_message(
                    text="Course: " + res["cName"]["value"])

        return [AllSlotsReset(), Restarted()]


# 2
class CourseHasTopic(Action):

    def name(self) -> Text:
        return "course_has_topic"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # get slot info
        topic = tracker.get_slot('topic')

        if topic is None:
            dispatcher.utter_message(text=f"I don't understand")
            return [AllSlotsReset(), Restarted()]

        # query
        sparql = SPARQLWrapper(
            "http://localhost:3030/Data/sparql", agent='Rasabot agent')
        sparql.setQuery("""
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            prefix xsd: <http://www.w3.org/2001/XMLSchema#>
            prefix foaf: <http://xmlns.com/foaf/0.1/>
            prefix dbo: <http://dbpedia.org/ontology/>
            prefix uni: <http://uni.com/schema#>
            prefix owl: <http://www.w3.org/2002/07/owl#>

            SELECT ?cName
            WHERE{
            ?course uni:has_topic ?topic.

            ?topic uni:topicName ?tName.
            ?course uni:subject ?cName.
            FILTER(REGEX(STR(?tName), '%s', "i"))
            }
            LIMIT 100

            """ % (topic))
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()
        if (len(result['results']['bindings']) == 0):
            dispatcher.utter_message(
                text="Sorry, I was unable to find any results for that question.")
        else:
            for res in result['results']['bindings']:
                dispatcher.utter_message(
                    text="Course: " + res["cName"]["value"])

        return [AllSlotsReset(), Restarted()]


# 3
class TopicInCourseNumber(Action):

    def name(self) -> Text:
        return "topic_in_course_number"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # get slot info
        course = tracker.get_slot('course')
        lecnum = int(tracker.get_slot('lec_number'))

        if (course is None) or (lecnum is None):
            dispatcher.utter_message(text=f"I don't understand")
            return [AllSlotsReset(), Restarted()]

        # query
        sparql = SPARQLWrapper(
            "http://localhost:3030/Data/sparql", agent='Rasabot agent')
        sparql.setQuery("""
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            prefix xsd: <http://www.w3.org/2001/XMLSchema#>
            prefix foaf: <http://xmlns.com/foaf/0.1/>
            prefix dbo: <http://dbpedia.org/ontology/>
            prefix uni: <http://uni.com/schema#>
            prefix owl: <http://www.w3.org/2002/07/owl#>

            SELECT ?tName
            WHERE{
            ?course uni:subject ?cName.
            ?course uni:has_lecture ?lecture.
            ?lecture uni:lecture_number ?lecNum.
            ?topic uni:provenance ?courseMat.
            ?course uni:has_lecture ?courseMat.
            ?topic uni:topicName ?tName.
            FILTER(REGEX(STR(?cName), '%s', "i")).
            FILTER(?lecNum=%d).
            }
            LIMIT 100
            



            """ % (course, lecnum))
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()
        if (len(result['results']['bindings']) == 0):
            dispatcher.utter_message(
                text="Sorry, I was unable to find any results for that question.")
        else:
            for res in result['results']['bindings']:
                dispatcher.utter_message(
                    text="Topic: " + res["tName"]["value"])

        return [AllSlotsReset(), Restarted()]


# 4
class GetCourseByUNiversityWithinSubject(Action):

    def name(self) -> Text:
        return "get_course_by_university_withing_subject"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # get slot info
        # uni = tracker.get_slot('university')
        topic = tracker.get_slot('topic')

        if (topic is None):
            dispatcher.utter_message(text=f"I don't understand")
            return [AllSlotsReset(), Restarted()]

        # query
        sparql = SPARQLWrapper(
            "http://localhost:3030/Data/sparql", agent='Rasabot agent')
        sparql.setQuery("""
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            prefix xsd: <http://www.w3.org/2001/XMLSchema#>
            prefix foaf: <http://xmlns.com/foaf/0.1/>
            prefix dbo: <http://dbpedia.org/ontology/>
            prefix uni: <http://uni.com/schema#>
            prefix owl: <http://www.w3.org/2002/07/owl#>

            SELECT ?cName
            WHERE{
            ?uni rdf:type dbo:University.
            ?uni uni:name ?uniName.
            ?uni uni:offers ?course.
            ?course rdf:type uni:Course.
            ?course uni:subject ?cName.
            ?course uni:has_topic ?topic.
            ?topic uni:topicName ?tName.
            FILTER(REGEX(STR(?uniName), 'Concordia', "i")).  
            FILTER(REGEX(STR(?tName), '%s', "i")).
            }
            LIMIT 100



            """ % (topic))
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()
        if (len(result['results']['bindings']) == 0):
            dispatcher.utter_message(
                text="Sorry, I was unable to find any results for that question.")
        else:
            for res in result['results']['bindings']:
                dispatcher.utter_message(
                    text="Course: " + res["cName"]["value"])

        return [AllSlotsReset(), Restarted()]


# 5----------------------------------------------------------------------Review
class GetMaterialForTopicCourse(Action):

    def name(self) -> Text:
        return "get_material_for_topic_course"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # get slot info
        course = tracker.get_slot('course')
        topic = tracker.get_slot('topic')

        if (course is None) or (topic is None):
            dispatcher.utter_message(text=f"I don't understand")
            return [AllSlotsReset(), Restarted()]

        # query
        sparql = SPARQLWrapper(
            "http://localhost:3030/Data/sparql", agent='Rasabot agent')
        sparql.setQuery("""
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            prefix xsd: <http://www.w3.org/2001/XMLSchema#>
            prefix foaf: <http://xmlns.com/foaf/0.1/>
            prefix dbo: <http://dbpedia.org/ontology/>
            prefix uni: <http://uni.com/schema#>
            prefix owl: <http://www.w3.org/2002/07/owl#>

            SELECT ?content
            WHERE{
            ?course uni:subject ?subject.
            ?topic uni:provenance ?lecture.
            ?course uni:has_topic ?topic.
            ?topic uni:topicName ?tName.
            ?course uni:has_lecture ?lecture.
            ?lecture uni:has_content ?content.
            FILTER(REGEX(STR(?subject), '%s', "i")).  
            FILTER(REGEX(STR(?tName), '%s', "i")).
            }
            LIMIT 100



            """ % (course, topic))
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()
        if (len(result['results']['bindings']) == 0):
            dispatcher.utter_message(
                text="Sorry, I was unable to find any results for that question.")
        else:
            for res in result['results']['bindings']:
                dispatcher.utter_message(
                    text="Content: " + res["content"]["value"])

        return [AllSlotsReset(), Restarted()]


# 6
class GetCreditsCourse(Action):

    def name(self) -> Text:
        return "get_credits_course"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # get slot info
        course = tracker.get_slot('course')

        if course is None:
            dispatcher.utter_message(text=f"I don't understand")
            return [AllSlotsReset(), Restarted()]

        # query
        sparql = SPARQLWrapper(
            "http://localhost:3030/Data/sparql", agent='Rasabot agent')
        sparql.setQuery("""
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            prefix xsd: <http://www.w3.org/2001/XMLSchema#>
            prefix foaf: <http://xmlns.com/foaf/0.1/>
            prefix dbo: <http://dbpedia.org/ontology/>
            prefix uni: <http://uni.com/schema#>
            prefix owl: <http://www.w3.org/2002/07/owl#>

            SELECT ?credits
            WHERE{
            ?course rdf:type uni:Course.
            ?course uni:subject ?cName.
            ?course uni:credits ?credits.
            FILTER(REGEX(STR(?cName), '%s', "i")).  
            }
            LIMIT 100



            """ % (course))
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()
        if (len(result['results']['bindings']) == 0):
            dispatcher.utter_message(
                text="Sorry, I was unable to find any results for that question.")
        else:
            for res in result['results']['bindings']:
                dispatcher.utter_message(
                    text="Content: " + res["credits"]["value"])

        return [AllSlotsReset(), Restarted()]


# 7
class GetCourseAdditionalResource(Action):

    def name(self) -> Text:
        return "get_course_additional_resource"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # get slot info
        course = tracker.get_slot('course')

        if course is None:
            dispatcher.utter_message(text=f"I don't understand")
            return [AllSlotsReset(), Restarted()]

        # query
        sparql = SPARQLWrapper(
            "http://localhost:3030/Data/sparql", agent='Rasabot agent')
        sparql.setQuery("""
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            prefix xsd: <http://www.w3.org/2001/XMLSchema#>
            prefix foaf: <http://xmlns.com/foaf/0.1/>
            prefix dbo: <http://dbpedia.org/ontology/>
            prefix uni: <http://uni.com/schema#>
            prefix owl: <http://www.w3.org/2002/07/owl#>

            SELECT ?lectureContent
            WHERE{
            ?course uni:subject ?subject.
            ?course uni:has_lecture ?lecture.
            ?lecture uni:has_content ?lectureContent.
            ?lectureContent rdf:type uni:OtherLectureMaterial.
            FILTER(REGEX(STR(?subject), '%s', "i")).  
            }
            LIMIT 100




            """ % (course))
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()
        if (len(result['results']['bindings']) == 0):
            dispatcher.utter_message(
                text="Sorry, I was unable to find any results for that question.")
        else:
            for res in result['results']['bindings']:
                dispatcher.utter_message(
                    text="Content: " + res["lectureContent"]["value"])

        return [AllSlotsReset(), Restarted()]


# 8
class GetMaterialLectureCourse(Action):

    def name(self) -> Text:
        return "get_material_lecture_course"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # get slot info
        course = tracker.get_slot('course')
        lecnum = int(tracker.get_slot('lec_number'))

        if (course is None) or (lecnum is None):
            dispatcher.utter_message(text=f"I don't understand")
            return [AllSlotsReset(), Restarted()]

        # query
        sparql = SPARQLWrapper(
            "http://localhost:3030/Data/sparql", agent='Rasabot agent')
        sparql.setQuery("""
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            prefix xsd: <http://www.w3.org/2001/XMLSchema#>
            prefix foaf: <http://xmlns.com/foaf/0.1/>
            prefix dbo: <http://dbpedia.org/ontology/>
            prefix uni: <http://uni.com/schema#>
            prefix owl: <http://www.w3.org/2002/07/owl#>

            SELECT ?material
            WHERE{
            ?course rdf:type uni:Course.
            ?course uni:subject ?cName.
            ?course uni:has_lecture ?lecture.
            ?lecture uni:lecture_number ?lecNum.
            ?lecture uni:has_content ?material.
            FILTER(REGEX(STR(?cName), '%s', "i")). 
            FILTER(?lecNum=%d).
            }
            LIMIT 100



            """ % (course, lecnum))
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()
        if (len(result['results']['bindings']) == 0):
            dispatcher.utter_message(
                text="Sorry, I was unable to find any results for that question.")
        else:
            for res in result['results']['bindings']:
                dispatcher.utter_message(
                    text="Material: " + res["material"]["value"])

        return [AllSlotsReset(), Restarted()]


# 9
class GetMaterialTopicCourse(Action):

    def name(self) -> Text:
        return "get_material_topic_course"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # get slot info
        topic = tracker.get_slot('topic')
        course = tracker.get_slot('course')

        if (course is None) or (topic is None):
            dispatcher.utter_message(text=f"I don't understand")
            return [AllSlotsReset(), Restarted()]

        # query
        sparql = SPARQLWrapper(
            "http://localhost:3030/Data/sparql", agent='Rasabot agent')
        sparql.setQuery("""
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            prefix xsd: <http://www.w3.org/2001/XMLSchema#>
            prefix foaf: <http://xmlns.com/foaf/0.1/>
            prefix dbo: <http://dbpedia.org/ontology/>
            prefix uni: <http://uni.com/schema#>
            prefix owl: <http://www.w3.org/2002/07/owl#>

            SELECT ?content
            WHERE{
            ?coures uni:subject ?cName.
            ?course uni:has_topic ?tName.
            ?course uni:has_lecture ?lecture.
            ?lecture uni:has_content ?content.
            ?content rdf:type uni:OtherLectureMaterial.
            FILTER(REGEX(STR(?tName), '%s', "i")). 
            FILTER(REGEX(STR(?cName), '%s', "i")). 
            }
            LIMIT 100



            """ % (topic, course))
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()
        if (len(result['results']['bindings']) == 0):
            dispatcher.utter_message(
                text="Sorry, I was unable to find any results for that question.")
        else:
            for res in result['results']['bindings']:
                dispatcher.utter_message(
                    text="Content: " + res["content"]["value"])

        return [AllSlotsReset(), Restarted()]

# 10


class GetTopicsGainedCourse(Action):

    def name(self) -> Text:
        return "get_topics_gained_course"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # get slot info
        course = tracker.get_slot('course')

        if course is None:
            dispatcher.utter_message(text=f"I don't understand")
            return [AllSlotsReset(), Restarted()]

        # query
        sparql = SPARQLWrapper(
            "http://localhost:3030/Data/sparql", agent='Rasabot agent')
        sparql.setQuery("""
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            prefix xsd: <http://www.w3.org/2001/XMLSchema#>
            prefix foaf: <http://xmlns.com/foaf/0.1/>
            prefix dbo: <http://dbpedia.org/ontology/>
            prefix uni: <http://uni.com/schema#>
            prefix owl: <http://www.w3.org/2002/07/owl#>

            SELECT ?tName
            WHERE{
            ?course rdf:type uni:Course.
            ?course uni:subject ?cName.
            ?course uni:has_topic ?topic.
            ?topic rdf:type uni:Topic.
            ?topic uni:topicName ?tName.
            FILTER(REGEX(STR(?cName), '%s', "i")). 
            }
            LIMIT 100



            """ % (course))
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()
        if (len(result['results']['bindings']) == 0):
            dispatcher.utter_message(
                text="Sorry, I was unable to find any results for that question.")
        else:
            for res in result['results']['bindings']:
                dispatcher.utter_message(
                    text="Topic: " + res["tName"]["value"])

        return [AllSlotsReset(), Restarted()]

# 11


class GetGradeStudentCourse(Action):

    def name(self) -> Text:
        return "get_grade_student_course"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # get slot info
        student_id = int(tracker.get_slot('student'))
        course = tracker.get_slot('course')

        if (course is None) or (student_id is None):
            dispatcher.utter_message(text=f"I don't understand")
            return [AllSlotsReset(), Restarted()]

        # query
        sparql = SPARQLWrapper(
            "http://localhost:3030/Data/sparql", agent='Rasabot agent')
        sparql.setQuery("""
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            prefix xsd: <http://www.w3.org/2001/XMLSchema#>
            prefix foaf: <http://xmlns.com/foaf/0.1/>
            prefix dbo: <http://dbpedia.org/ontology/>
            prefix uni: <http://uni.com/schema#>
            prefix owl: <http://www.w3.org/2002/07/owl#>

            SELECT ?gradeVal
            WHERE{
            ?student rdf:type uni:Student.
            ?student uni:student_ID ?ID.
            ?student uni:grade_obtained ?grade.
            ?grade rdf:type uni:Grade.
            ?grade uni:grade_obtained_in ?course.
            ?course uni:subject ?cName.
            ?grade uni:grade_value ?gradeVal.
            FILTER(?ID=%d). 
            FILTER(REGEX(STR(?cName), '%s', "i")). 
            }
            LIMIT 100



            """ % (student_id, course))
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()
        if (len(result['results']['bindings']) == 0):
            dispatcher.utter_message(
                text="Sorry, I was unable to find any results for that question.")
        else:
            for res in result['results']['bindings']:
                dispatcher.utter_message(
                    text="Grade: " + res["gradeVal"]["value"])

        return [AllSlotsReset(), Restarted()]


# 12
class GetStudentCompleted(Action):

    def name(self) -> Text:
        return "get_student_completed"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # get slot info
        course = tracker.get_slot('course')

        if course is None:
            dispatcher.utter_message(text=f"I don't understand")
            return [AllSlotsReset(), Restarted()]

        # query
        sparql = SPARQLWrapper(
            "http://localhost:3030/Data/sparql", agent='Rasabot agent')
        sparql.setQuery("""
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            prefix xsd: <http://www.w3.org/2001/XMLSchema#>
            prefix foaf: <http://xmlns.com/foaf/0.1/>
            prefix dbo: <http://dbpedia.org/ontology/>
            prefix uni: <http://uni.com/schema#>
            prefix owl: <http://www.w3.org/2002/07/owl#>

            SELECT ?studentID
            WHERE{
            ?student rdf:type uni:Student.
            ?student uni:student_ID ?studentID.
            ?student uni:completed ?course.
            ?course uni:subject ?cName.
            FILTER(REGEX(STR(?cName), '%s', "i")). 
            }
            LIMIT 100



            """ % (course))
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()
        if (len(result['results']['bindings']) == 0):
            dispatcher.utter_message(
                text="Sorry, I was unable to find any results for that question.")
        else:
            for res in result['results']['bindings']:
                dispatcher.utter_message(
                    text="Student ID: " + res["studentID"]["value"])

        return [AllSlotsReset(), Restarted()]


# 13
class GetTranscript(Action):

    def name(self) -> Text:
        return "get_transcript"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # get slot info
        student_id = int(tracker.get_slot('student'))

        if student_id is None:
            dispatcher.utter_message(text=f"I don't understand")
            return [AllSlotsReset(), Restarted()]

        # query
        sparql = SPARQLWrapper(
            "http://localhost:3030/Data/sparql", agent='Rasabot agent')
        sparql.setQuery("""
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            prefix xsd: <http://www.w3.org/2001/XMLSchema#>
            prefix foaf: <http://xmlns.com/foaf/0.1/>
            prefix dbo: <http://dbpedia.org/ontology/>
            prefix uni: <http://uni.com/schema#>
            prefix owl: <http://www.w3.org/2002/07/owl#>

            SELECT ?gradeVal ?cName ?courseID
            WHERE{
            ?student rdf:type uni:Student.
            ?student uni:grade_obtained ?grade.
            ?grade uni:grade_value ?gradeVal.
            ?grade uni:grade_obtained_in ?course.
            ?course uni:subject ?cName.
            ?course uni:ID ?courseID.
            ?student uni:student_ID ?ID.
            FILTER(?ID=%d). 

            }
            LIMIT 100



            """ % (student_id))
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()
        if (len(result['results']['bindings']) == 0):
            dispatcher.utter_message(
                text="Sorry, I was unable to find any results for that question.")
        else:
            for res in result['results']['bindings']:
                dispatcher.utter_message(
                    text=res["gradeVal"]["value"] + " was earned in " + res["cName"]["value"] + " " + res["courseID"]["value"])

        return [AllSlotsReset(), Restarted()]

# 14
class CourseDescription(Action):

    def name(self) -> Text:
        return "get_course_description"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        course = tracker.get_slot['course']

        # query
        sparql = SPARQLWrapper(
            "http://localhost:3030/Data/sparql", agent='Rasabot agent')
        sparql.setQuery("""
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            prefix xsd: <http://www.w3.org/2001/XMLSchema#>
            prefix foaf: <http://xmlns.com/foaf/0.1/>
            prefix dbo: <http://dbpedia.org/ontology/>
            prefix uni: <http://uni.com/schema#>
            prefix owl: <http://www.w3.org/2002/07/owl#>

            SELECT ?description
            WHERE{
            ?course rdf:type uni:Course.
            ?course uni:subject ?cname.
            ?course uni:description ?description.
            FILTER(REGEX(STR(?cname), '%s', "i")). 
            }
            LIMIT 100
            """%(course))
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()
        if (len(result['results']['bindings']) == 0):
            dispatcher.utter_message(
                text="Sorry, I was unable to find any results for that question.")
        else:
            for res in result['results']['bindings']:
                dispatcher.utter_message(
                    text="The description for the course is: " + res["description"]["value"])

        return [AllSlotsReset(), Restarted()]


# 15
class CourseEventTopic(Action):
    def name(self) -> Text:
        return "get_course_event_topic"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        topic = tracker.get_slot['topic']

        # query
        sparql = SPARQLWrapper(
            "http://localhost:3030/Data/sparql", agent='Rasabot agent')
        sparql.setQuery("""
            prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            prefix xsd: <http://www.w3.org/2001/XMLSchema#>
            prefix foaf: <http://xmlns.com/foaf/0.1/>
            prefix dbo: <http://dbpedia.org/ontology/>
            prefix uni: <http://uni.com/schema#>
            prefix owl: <http://www.w3.org/2002/07/owl#>
            SELECT ?provenance (COUNT(?provenance) AS ?freq)
            WHERE{
            ?topic uni:topicName ?tName.
            ?topic uni:provenance ?provenance.
            FILTER(REGEX(STR(?tName), '%s', "i")).
            }
            GROUP BY ?provenance
            ORDER BY DESC(?freq)
            LIMIT 100
            """ % (topic))
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()
        if (len(result['results']['bindings']) == 0):
            dispatcher.utter_message(
                text="Sorry, I was unable to find any results for that question.")
        else:
            for res in result['results']['bindings']:
                dispatcher.utter_message(
                    text=res["provenance"]["value"] + " covers this topic.")

        return [AllSlotsReset(), Restarted()]