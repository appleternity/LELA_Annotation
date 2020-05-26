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
    setting = build_setting(url, 1100)

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
            {
                "QualificationTypeId": "00000000000000000040",
                "Comparator": "GreaterThanOrEqualTo",
                "IntegerValues": [
                    3000
                ],
                "ActionsGuarded": "Accept"
            },
            #{
            #    "QualificationTypeId": qual_id,
            #    "Comparator": "DoesNotExist",
            #    "ActionsGuarded": "DiscoverPreviewAndAccept",
            #}
        ],
    )

    return response

def get_previous_worker(mongo, story_info):
    workers = []

    # previous part
    for res in mongo.story_info.find({
        "index":story_info["index"],
        "part":{"$lt":story_info["part"]},
        "answers":{"$exists":True},
    }):
        for r in res["answers"]:
            workers.append(r["worker_id"])
        
    # same part, previous character
    for res in mongo.story_info.find({
        "index":story_info["index"],
        "part":story_info["part"],
        "char_index":{"$lt":story_info["char_index"]},
        "answers":{"$exists":True},
    }):
        for r in res["answers"]:
            workers.append(r["worker_id"])

    if len(workers) != len(list(set(workers))):
        print("ERROR: repeated worker appears!!!!!!!")
        quit()

    return workers

def get_all_previous_worker(mongo, story_index):
    workers = []
    for res in mongo.story_info.find({
        "index": story_index,
        "answers": {"$exists":True}
    }):
        for r in res["answers"]:
            workers.append(r["worker_id"])
    return workers

"""
def create_hit_batch(client, batch_index, mode, check=True, override=False):
    if override is True:
        r = input("Are you sure you want to override the hits? (YES/no)\n")
        if r != "YES":
            quit()

    mongo = MongoClient("localhost")["CrowdAI"]
    
    if mode == "role":
        with open("batch_info.json", 'r', encoding='utf-8') as infile:
            batch_info = json.load(infile)
    elif mode == "normal":
        with open("batch_info_normal.json", 'r', encoding='utf-8') as infile:
            batch_info = json.load(infile)
    else:
        print("unavailable mode [{}]".format(mode))
        quit()

    batch_setting = batch_info[batch_index]
    print(batch_setting)

    if mode == "role":
        query = {
            "char_index":batch_setting["char_index"],
            "part":batch_setting["part"],
            "type":"role"
        }
    elif mode == "normal":
        query = {
            "part":batch_setting["part"],
            "type":"normal",
        }
    else:
        print("unavailable mode [{}]".format(mode))

    for res in mongo.story_info.find(query):
        #previous_workers = get_previous_worker(mongo, res)
        previous_workers = get_all_previous_worker(mongo, res["index"])
        if res["index"] == 0:
            #previous_workers.extend(["A2JUTFKDJYFU67"])
            previous_workers.extend(["A3VFEPSZMHZPEY", "A33SKY7HS5PDT6", "A2TLN8489YGY81", "A25R2OI9L2Q1OW", "A249LDVPG27XCE", "A3A8P4UR9A0DWQ", "AAN06KVDS2XRY", "A3D5V7JNVBQH59", "A2VNR6984SDFGQ", "A1HNR6OIRFCEHS"])
        if override is True or "hit_id" not in res:
            if check is True:
                #print(sorted(previous_workers))
                print(len(previous_workers))
                print(res["url"])
                print()
            else:
                hit_info = create_hit(
                    client, 
                    res["url"], 
                    batch_setting["reward"], 
                    worker_id_list=previous_workers,
                    num_assignment=5 if mode != "normal" else res["char_num"] * 5
                )
                mongo.story_info.update_one(
                    {"_id":res["_id"]},
                    {"$set":{"hit_id":hit_info["HIT"]["HITId"], "answers":[]}}
                )
        else:
            print("hit_id exists!!!")
"""

def loop_update_answer(client, batch_index, mode):
    mongo = MongoClient("localhost")["CrowdAI"]
    
    if mode == "role":
        with open("batch_info.json", 'r', encoding='utf-8') as infile:
            batch_info = json.load(infile)
    elif mode == "normal":
        with open("batch_info_normal.json", 'r', encoding='utf-8') as infile:
            batch_info = json.load(infile)
    else:
        print("unavailable mode [{}]".format(mode))
        quit()

    batch_setting = batch_info[batch_index]
    print(batch_setting)

    while True:
        update_answer(client, mongo, batch_setting, mode)
        time.sleep(60*5)

def update_answer(client, mongo, batch_setting, mode):
    print()
    if mode == "role":
        query = {
            "char_index":batch_setting["char_index"],
            "part":batch_setting["part"],
            "answers":{"$exists":True},
            "$where":"this.answers.length<5",
            "type":"role",
        }
    elif mode == "normal":
        query = {
            "part":batch_setting["part"],
            "type":"normal",
            "answers":{"$exists":True},
            "$where":"this.answers.length<5*this.char_num",
        }
    else:
        print("unavailable mode [{}]".format(mode))
        quit()

    for res in mongo.story_info.find(query): 
        print("checking story {}... [{}]".format(res["index"], len(res["answers"])))
        hit_id = res["hit_id"]
        
        assignments = get_all_assignment(client, hit_id, status=["Submitted"])
        for a in assignments:
            answers = parse_hit(a["Answer"])
            approve_assignment(client, a["AssignmentId"])
            answer_info = {
                "worker_id":a["WorkerId"],
                "assignment_id":a["AssignmentId"],
                "answers":answers
            }
            mongo.story_info.update_one(
                {"_id":res["_id"]},
                {"$push":{"answers":answer_info}}
            )

    if mongo.story_info.count(query) == 0:
        # send notification
        print("all assignments are finished")
        noti = Notification()
        noti.send(
            "appleternity@gmail.com", 
            "[Mturk] Batch {} Has Finished".format(batch_setting["batch_index"]), 
            "Batch {} Has Finished at {}".format(
                batch_setting["batch_index"],
                str(datetime.now())
            )
        )
        quit()

def generate_batch():
    mongo = MongoClient("localhost")["CrowdAI"]
    reward_mapping = {
        1: 0.5,
        2: 0.8,
        3: 1.6,
    }
    batch_index = 0
    batch_setting = []
    for part in [1, 2, 3]:
        for char_index in [0, 1, 2, 3, 4]:
            results = mongo.story_info.find({
                "part":part,
                "char_index":char_index
            })
            results = [r for r in results]
            if results:
                print("batch_index:{}, part:{}, char_index:{}, len:{}".format(batch_index, part, char_index, len(results)))
                batch_setting.append({
                    "batch_index":batch_index,
                    "part":part,
                    "char_index":char_index,
                    "len":len(results),
                    "reward":reward_mapping[part],
                })
                batch_index += 1

    with open("batch_info.json", 'w', encoding='utf-8') as outfile:
        json.dump(batch_setting, outfile, indent=4)

def generate_baseline_batch():
    mongo = MongoClient("localhost")["CrowdAI"]
    reward_mapping = {
        1: 0.5,
        2: 0.8,
        3: 1.6,
    }
    batch_index = 0
    batch_setting = []
    for part in [1, 2, 3]:
        results = mongo.story_info.find({
            "part":part,
            "type":"normal",
        })
        results = [r for r in results]
        if results:
            print("batch_index:{}, part:{}, len:{}".format(batch_index, part, len(results)))
            batch_setting.append({
                "batch_index":batch_index,
                "part":part,
                "len":len(results),
                "reward":reward_mapping[part],
                "type":"normal"
            })
            batch_index += 1
    with open("batch_info_normal.json", 'w', encoding='utf-8') as outfile:
        json.dump(batch_setting, outfile, indent=4)

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

def main():
    #generate_batch()
    #generate_baseline_batch()
    #quit()

    #client = get_client(mode="production")
    client = get_client()
    quit()

    ## role
    #res = create_hit_batch(client, batch_index=5, mode="role", check=True)
    #loop_update_answer(client, batch_index=5)
    
    ## normal
    res = create_hit_batch(client, batch_index=1, mode="normal", check=False, override=False)
    loop_update_answer(client, batch_index=1, mode="normal")

    #res = create_hit(client, "https://appleternity.github.io/CrowdWriting/html/story_feedback.html", 0.5)
    #res = create_hit(client, "https://appleternity.github.io/CrowdWriting/html/story_feedback_normal.html", 0.5)
    #get_hit_and_approve(client)

if __name__ == "__main__":
    main()
