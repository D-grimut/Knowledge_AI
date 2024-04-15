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
                template="no_result")
        else:
            course = ""
            for res in result['results']['bindings']:
                course = course + "Course: " + res["cName"]["value"] + "\n"

            dispatcher.utter_message(template="get_course_list", uni="Concordia", courses=course)
                
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
                template="no_result")
        else:
            course = ""
            for res in result['results']['bindings']:
                course = course + "Course: " + res["cName"]["value"] + "\n"

            dispatcher.utter_message(template="course_has_topic", topic=topic, courses=course)

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
        lecnum_str = tracker.get_slot('lec_number')
        if lecnum_str is not None and lecnum_str.isdigit():
            lecnum = int(lecnum_str)
        else:
            dispatcher.utter_message(text=f"Not a valid number")
            return [AllSlotsReset(), Restarted()]

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
                template="no_result")
        else:
            topics = ""
            for res in result['results']['bindings']:
                topics = topics + "Topic: " + res["tName"]["value"] + "\n"

            dispatcher.utter_message(template="topic_in_course_number", course=course, lec=lecnum, topics=topics)
                
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
                template="no_result")
        else:
            course = ""
            for res in result['results']['bindings']:
                course = course + "Course: " + res["cName"]["value"] + "\n"

            dispatcher.utter_message(template="get_course_by_university_withing_subject", uni="Concordia", topic=topic, courses=course)
        return [AllSlotsReset(), Restarted()]


# 5----------------------------------------------------------------------Review
class GetMaterialForTopicCourse(Action):

    def name(self) -> Text:
        return "get_material_for_topic_course"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_question = tracker.latest_message.get('text')

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
            LIMIT 5



            """ % (course, topic))
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()
        if (len(result['results']['bindings']) == 0):
            dispatcher.utter_message(
                template="no_result")
        else:
            contex = ""
            for res in result['results']['bindings']:
                contex = res["content"]["value"] + "\n"

            dispatcher.utter_message(template="get_material_for_topic_course", topic=topic, course=course, material=contex)

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
        user_question = tracker.latest_message.get('text')

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
            LIMIT 1



            """ % (course))
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()
        if (len(result['results']['bindings']) == 0):
            dispatcher.utter_message(
                template="no_result")
        else:

            cred = ""
            for res in result['results']['bindings']:
                cred = res

            dispatcher.utter_message(template="get_credits_course", course=course, credits=cred)

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
        user_question = tracker.latest_message.get('text')

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
            LIMIT 5




            """ % (course))
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()
        if (len(result['results']['bindings']) == 0):
            dispatcher.utter_message(
                template="no_result")
        else:
       
            context = ""
            for res in result['results']['bindings']:
                context = context + res["lectureContent"]["value"] + "\n"

            dispatcher.utter_message(template="get_course_additional_resource", course=course, resources=context)

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
        lecnum_str = tracker.get_slot('lec_number')
        user_question = tracker.latest_message.get('text')
        
        if lecnum_str is not None and lecnum_str.isdigit():
            lecnum = int(lecnum_str)
        else:
            dispatcher.utter_message(text=f"Not a valid number")
            return [AllSlotsReset(), Restarted()]

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
            LIMIT 5



            """ % (course, lecnum))
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()
        if (len(result['results']['bindings']) == 0):
            dispatcher.utter_message(
                template="no_result")
        else:

            context = ""
            for res in result['results']['bindings']:
                context = context + res["material"]["value"] + "\n "

            dispatcher.utter_message(template="get_material_lecture_course", lecnum=lecnum, course=course, content=context)

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
        user_question = tracker.latest_message.get('text')

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
            LIMIT 5



            """ % (topic, course))
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()
        if (len(result['results']['bindings']) == 0):
            dispatcher.utter_message(
                template="no_result")
        else:

            context = ""
            for res in result['results']['bindings']:
                context = context + res["content"]["value"] + "\n"

            dispatcher.utter_message(template="get_material_topic_course", topic=topic, course=course, mats=context)

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
        user_question = tracker.latest_message.get('text')

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
                template="no_result")
        else:

            context = ""
            for res in result['results']['bindings']:
                context = context + res["tName"]["value"] + "\n"

            dispatcher.utter_message(template="get_topics_gained_course", course=course, comp=context)

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
        user_question = tracker.latest_message.get('text')

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
            LIMIT 10



            """ % (student_id, course))
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()
        if (len(result['results']['bindings']) == 0):
            dispatcher.utter_message(
                template="no_result")
        else:

            context = ""
            for res in result['results']['bindings']:
                context = context + res["gradeVal"]["value"] + "\n"

            dispatcher.utter_message(template="get_grade_student_course", student_id=student_id, course=course, grades=context)

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
                template="no_result")
        else:

            students = ""
            for res in result['results']['bindings']:
                students = students + "Student ID: " + res["studentID"]["value"] + "\n"

            dispatcher.utter_message(template="get_student_completed", course=course, students=students)

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
                template="no_result")
        else:

            grades = ""
            for res in result['results']['bindings']:
                grades = grades + ["gradeVal"]["value"] + " was earned in " + res["cName"]["value"] + " " + res["courseID"]["value"] + "\n"

            dispatcher.utter_message(template="get_student_completed", student=student_id, grades=grades)

        return [AllSlotsReset(), Restarted()]


# 14
class CourseDescription(Action):

    def name(self) -> Text:
        return "get_course_description"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        course = tracker.get_slot('course')
        user_question = tracker.latest_message.get('text')

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
            """ % (course))
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()
        if (len(result['results']['bindings']) == 0):
            dispatcher.utter_message(
                template="no_result")
        else:
  
            context = ""
            for res in result['results']['bindings']:
                context = context + res["description"]["value"]  + "\n"

            dispatcher.utter_message(template="get_course_description", course=course, desc=context)
 
        return [AllSlotsReset(), Restarted()]


# 15
class CourseEventTopic(Action):
    def name(self) -> Text:
        return "get_course_event_topic"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        topic = tracker.get_slot('topic')

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
                template="no_result")
        else:

            resources = ""
            for res in result['results']['bindings']:
                resources = resources + res["provenance"]["value"] + "\n"

            dispatcher.utter_message(template="get_course_event_topic", topic=topic, resources=resources)

        return [AllSlotsReset(), Restarted()]

#16
class TopicCoveredEvent(Action):

    def name(self) -> Text:
        return "get_topic_covered_event"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        event = tracker.get_slot('lec')
        course = tracker.get_slot('course')
        lecnum_str = tracker.get_slot('lec_number')
        if lecnum_str is not None and lecnum_str.isdigit():
            lecnum = int(lecnum_str)
        else:
            dispatcher.utter_message(text=f"Not a valid number")
            return [AllSlotsReset(), Restarted()]

        if event is None or lecnum is None or course is None:
            dispatcher.utter_message(text=f"I don't understand")
            return [AllSlotsReset(), Restarted()]

        # query
        sparql = SPARQLWrapper(
            "http://localhost:3030/Data/sparql", agent='Rasabot agent')

        # ----------------------------------------------
        event = event.lower()
        if event in set(['lecture', 'lectures', 'lec']):
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

        elif event in set(['lab', 'labs', 'laboratories', 'laboratory']):
            sparql.setQuery("""
            PREFIX un: <http://www.w3.org/2007/ont/unit#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX uni: <http://uni.com/schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>

            SELECT ?tName
            WHERE{
            ?course uni:subject ?cName.
            ?course uni:has_lecture ?lecture.
            ?lecture rdf:type uni:Labs.
            ?lecture uni:lecture_number ?lecNum.
            ?topic uni:provenance ?lecture.
            ?topic uni:topicName ?tName.
            FILTER(REGEX(STR(?cName), '%s', "i")).
            FILTER(?lecNum=%d).
            }
            LIMIT 100
            """ % (course, lecnum))
            sparql.setReturnFormat(JSON)
            result = sparql.query().convert()

        elif event in set(['tutorial', 'tutorials', 'tuts', 'tut']):
            sparql.setQuery("""
            PREFIX un: <http://www.w3.org/2007/ont/unit#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX uni: <http://uni.com/schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>

            SELECT ?tName
            WHERE{
            ?course uni:subject ?cName.
            ?course uni:has_lecture ?lecture.
            ?lecture rdf:type uni:Tutorials.
            ?lecture uni:lecture_number ?lecNum.
            ?topic uni:provenance ?lecture.
            ?topic uni:topicName ?tName.
            FILTER(REGEX(STR(?cName), '%s', "i")).
            FILTER(?lecNum=%d).
            }
            LIMIT 100
            """ % (course, lecnum))
            sparql.setReturnFormat(JSON)
            result = sparql.query().convert()

        # ---------------------------------------------

        if (len(result['results']['bindings']) == 0):
            dispatcher.utter_message(
                template="no_result")
        else:

            topics = ""
            for res in result['results']['bindings']:
                topics = topics + res["tName"]["value"] + "\n"

            dispatcher.utter_message(template="get_topic_covered_event", lecture=event, lec_number=lecnum, course=course, topics=topics)

        return [AllSlotsReset(), Restarted()]
