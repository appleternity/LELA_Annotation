import sys
sys.path.append("/home/appleternity/workspace/lab/Crowd/mturk_util")
from mturk import *
from pprint import pprint
import json
from pymongo import MongoClient
import time
from notification import Notification
from datetime import datetime

def create_hit(client, url, reward, worker_id_list=None, num_assignment=5):
    setting = build_setting(url, 1000)

    #worker_id_list = ["A3VFEPSZMHZPEY", "A33SKY7HS5PDT6", "A2TLN8489YGY81", "A25R2OI9L2Q1OW", "A249LDVPG27XCE", "A3A8P4UR9A0DWQ", "AAN06KVDS2XRY", "A3D5V7JNVBQH59", "A2VNR6984SDFGQ", "A1HNR6OIRFCEHS"]
    #if worker_id_list is None:
    #    worker_id_list = []
    #qual_id = create_worker_qualification(client, worker_id_list)

    response = client.create_hit(
        MaxAssignments=num_assignment,
        LifetimeInSeconds=60*60*60, # 60 days
        AssignmentDurationInSeconds=60*60, # 30 min
        Reward=str(reward),
        Title='Useful Example Sentence Annotation.',
        Keywords='example sentences, language learning, confusing words, synonyms',
        Description="""
            In this task, you will need to read through 20 sentences and determine which one is good for learners.
            There are 3 stages to guide you understand and read through all the example sentences.
        """.strip().replace("  ", ""),
        Question=setting,
        QualificationRequirements=[
            {
                "QualificationTypeId": "000000000000000000L0",
                "Comparator": "GreaterThanOrEqualTo",
                "IntegerValues": [
                    98
                ],
                "ActionsGuarded": "Accept"
            },
            {
                "QualificationTypeId": "00000000000000000060",
                "Comparator": "EqualTo",
                "IntegerValues": [
                    1
                ],
                "ActionsGuarded": "Accept"
            },
            {
                'QualificationTypeId': '00000000000000000071',
                'Comparator': 'In',
                'LocaleValues': [
                    {
                        'Country': 'US',
                    },
                ],
                'ActionsGuarded': 'Accept'
            },
            #{
            #    "QualificationTypeId": "00000000000000000040",
            #    "Comparator": "GreaterThanOrEqualTo",
            #    "IntegerValues": [
            #        3000
            #    ],
            #    "ActionsGuarded": "Accept"
            #},
            #{
            #    "QualificationTypeId": qual_id,
            #    "Comparator": "DoesNotExist",
            #    "ActionsGuarded": "DiscoverPreviewAndAccept",
            #}
        ],
    )

    return response

def create_hit_batch(client):
    for i in range(4, 5):
        url = "https://appleternity.github.io/LELA_Annotation/annotation_use/html_0526/{:0>3}.html".format(i)
        print("creating hit {} / 30".format(i+1))
        print(url)
        res = create_hit(
            client, 
            url=url,
            reward=2.5, 
            num_assignment=5
        )

def get_result(client, hit_id):
    result = []
    res = get_all_assignment(client, hit_id, status=["Submitted", "Approved"])
    for r in res:
        r["parsed_answer"] = parse_hit(r["Answer"])
        for key in ["answer", "fib_answer", "reason_answer"]:
            r["parsed_answer"][key] = json.loads(r["parsed_answer"][key])
        approve_assignment(client, r["AssignmentId"])
    result.extend(res)
    return result

def get_result_batch(client, hit_id_list):
    final_result = {} 
    for hit_id in hit_id_list:
        result = get_result(client, hit_id)
        final_result[hit_id] = result
    return final_result

def get_hit_and_approve(client):
    hit = list_hit(client, 1)
    result = []
    for i, r in enumerate(hit["HITs"]):
        hit_id = r["HITId"]
        res = get_all_assignment(client, hit_id, status=["Submitted", "Approved"])
        for r in res:
            r["parsed_answer"] = parse_hit(r["Answer"])
            approve_assignment(client, r["AssignmentId"])
        result.extend(res)

    with open("result/result_03.json", 'w', encoding='utf-8') as infile:
        json.dump(result, infile, indent=4)

def lela_annotation():
    client = get_client(mode="production")
    #client = get_client()

    #create_hit_batch(client) 

    #HITID: 3MDWE879UIBWP6WIX9RUDD0NFFHB9I (small/little) without handling duplicated sentences

    #res = get_result(client, "3R16PJFTS40WL3U0MR8X946USZ5K4K")
    #res = get_result(client, "3Y40HMYLL2R1M1NM0GE4C2CQNMVUXV")

    hit_id_list = [
        "3A520CCNWO981SI7Z67KAGHSOUCEA0",
        "3MDWE879UIBWP6WIX9RUDD0NFFHB9I", # questioned
        "307FVKVSYSO8QONG3XJNR33BAXC74W",
        "38B7Q9C28HEQJUFN1IAM2XEV1E696V",
        "3YKP7CX6G3OSBN8PICTAZH9HKPTB76",
    ]
    res = get_result_batch(client, hit_id_list)
    with open("test_result.json", 'w', encoding='utf-8') as outfile:
        json.dump(res, outfile, indent=4)

def main():

    #client = get_client(mode="production")
    client = get_client()
    quit()
    
    #res = create_hit(client, "https://appleternity.github.io/CrowdWriting/html/story_feedback.html", 0.5)
    #res = create_hit(client, "https://appleternity.github.io/CrowdWriting/html/story_feedback_normal.html", 0.5)
    #get_hit_and_approve(client)

if __name__ == "__main__":
    #main()
    lela_annotation()
