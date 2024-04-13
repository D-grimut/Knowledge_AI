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
