import csv
from pprint import pprint
from nltk import word_tokenize, pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
import re
import json
from uuid import uuid4
import random

class Stemmer:
    def __init__(self):
        self.wnl = WordNetLemmatizer()

    def stem(self, word, tag=None):

        if tag in ['v', 'n', 'a', 'r']:
            return self.wnl.lemmatize(word, tag)

        temp = self.wnl.lemmatize(word, 'v') # check VERB
        if temp != word:
            return temp

        temp = self.wnl.lemmatize(word, 'n') # check NOUN
        if temp != word:
            return temp

        temp = self.wnl.lemmatize(word, 'a') # check ADJ
        if temp != word:
            return temp

        temp = self.wnl.lemmatize(word, 'r') # check ADV
        if temp != word:
            return temp

        return word

    def stemPOS(self, word, pos):
        if 'V' in pos:
            temp = self.wnl.lemmatize(word, 'v')
            return temp
        elif 'NN' in pos:
            temp = self.wnl.lemmatize(word, 'n')
            return temp
        elif 'JJ' in pos:
            temp = self.wnl.lemmatize(word, 'a')
            return temp
        elif 'RB' in pos:
            temp = self.wnl.lemmatize(word, 'r')
            return temp
        else:
            return word

strong_pattern = re.compile(r"<strong>.+</strong>")
my_stemmer = Stemmer()
def turn_to_display_sentence(sent, word):
    res = strong_pattern.search(sent)

    # sent is highlighted
    if res is not None:
        return sent

    # sent is not highlighted
    tokens = word_tokenize(sent)
    stemmed_tokens = [my_stemmer.stemPOS(token, pos) for token, pos in pos_tag(tokens)]

    # search
    match = []
    for i, (stemmed_token, ori_token) in enumerate(zip(stemmed_tokens, tokens)):
        if stemmed_token == word:
            match.append(ori_token)

    if len(match) == 0:
        print("\nThere is no match for the following case\nword:{}, sentence: {}".format(word, sent))
        #quit()
        return sent, sent
    
    if len(match) > 1:
        print("\nThere is {} match for the following case\nword:{}, sentence: {}".format(len(match), word, sent))
        #quit()

    target_word = match[0]
    display_sent = sent.replace(target_word, "<strong>{}</strong>".format(target_word))
    question_sent = sent.replace(target_word, "_____")

    return display_sent, question_sent

def load_data():
    data = []

    with open("20200523_tukers_sentence_selection_raw_sentence.tsv", 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile, delimiter='\t')
        info = None 
        for row in reader:
            if row[0].isdigit():

                # keep old info
                if info is not None:
                    data.append(info)

                # init new info
                index = int(row[0])
                print(index)
                w1, w2 = row[1].strip().split("|") 
                info = {
                    "index":index,
                    "w1":w1,
                    "w2":w2,
                    "wordpair":row[1].strip(),
                    "w1_sent":[],
                    "w2_sent":[],
                    w1:"w1",
                    w2:"w2",
                }
            else:
                word = row[0].strip()
                sent = row[1].strip()
                display_sent, question_sent = turn_to_display_sentence(sent, word) 

                info[info[word]+"_sent"].append({
                    "ori_sent":sent,
                    "display_sent":display_sent, 
                    "question_sent":question_sent,
                })
        
        # keep the last one
        data.append(info)

    print(len(data))

    for info in data:
        print(info["wordpair"])
        print(info["w1"], len(info["w1_sent"]))
        print(info["w2"], len(info["w2_sent"]))

    with open("data.json", 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, indent=4)

def check_repeat():
    with open("data_with_id.json", 'r', encoding='utf-8') as infile:
        data = json.load(infile)
    
    for info in data:
        print()
        print(info["wordpair"], info["index"])

        set1 = set(sent["display_sent"] for sent in info["w1_sent"])
        if len(set1) != 10:
            print("***", info["w1"], len(set1))
        
        set2 = set(sent["display_sent"] for sent in info["w2_sent"])
        if len(set2) != 10:
            print(info["w2"], len(set2))
        

def check_data():
    with open("data.json", 'r', encoding='utf-8') as infile:
        data = json.load(infile)

    strong_pattern = re.compile(r"<strong>.+</strong>")
    question_pattern = re.compile(r"_____")
    for info in data:
        print(info["wordpair"])
        
        good_display_sent = sum(1 for sent in info["w1_sent"] if strong_pattern.search(sent["display_sent"]))
        good_question_sent = sum(1 for sent in info["w1_sent"] if question_pattern.search(sent["question_sent"]))
        print(info["w1"], len(info["w1_sent"]), good_display_sent, good_question_sent)
        if good_display_sent != 10 or good_question_sent != 10:
            print("GGGGGGGGGGGGGGGGG")

        good_display_sent = sum(1 for sent in info["w2_sent"] if strong_pattern.search(sent["display_sent"]))
        good_question_sent = sum(1 for sent in info["w2_sent"] if question_pattern.search(sent["question_sent"]))
        print(info["w2"], len(info["w2_sent"]), good_display_sent, good_question_sent)
        if good_display_sent != 10 or good_question_sent != 10:
            print("GGGGGGGGGGGGGGGGG")

        # add sentence id
        for sent in info["w1_sent"]:
            sent["id"] = str(uuid4())

        for sent in info["w2_sent"]:
            sent["id"] = str(uuid4())

    with open("data_with_id.json", 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, indent=4)

def turn_highlight(sent):
    strong_pattern = re.compile(r"<strong>(?P<word>.+?)</strong>")
    res = strong_pattern.findall(sent)
    print(res)
    for r in res:
        sent = sent.replace("<strong>{}</strong>".format(r), '<span class="highlighted">{}</span>'.format(r))
    return sent

def render_html(template, info):
    w1 = info["w1"]
    w2 = info["w2"]

    # remove duplicated
    new_sent = []
    sent_set = set()
    for sent in info["w1_sent"]:
        if sent["display_sent"] not in sent_set:
            new_sent.append(sent)
            sent_set.update([sent["display_sent"]])
    info["w1_sent"] = new_sent

    new_sent = []
    sent_set = set()
    for sent in info["w2_sent"]:
        if sent["display_sent"] not in sent_set:
            new_sent.append(sent)
            sent_set.update([sent["display_sent"]])
    info["w2_sent"] = new_sent

    # stage 1
    question_template = """
        <tr>
            <td>{{question}}</td>
            <td><input type="radio" name="{{id}}" value="{{w1}}" class="form-radio" /></td>
            <td><input type="radio" name="{{id}}" value="{{w2}}" class="form-radio" /></td>
        </tr>
    """
    question_list = []
    for sent in info["w1_sent"]+info["w2_sent"]:
        question = sent["question_sent"].replace("_____", '<span class="blank"></span>')
        res = question_template.replace("{{question}}", question).replace("{{id}}", sent["id"]).replace("{{w1}}", w1).replace("{{w2}}", w2)
        question_list.append(res)
    random.shuffle(question_list)
    stage_one_content = "\n".join(question_list)
    
    # stage 2
    condition_template = """
        <tr sent_id="{{id}}">
            <td>{{sent}}</td>
            <td><input type="checkbox" class="form-radio" /></td>
            <td>
                <div class="btn-group">
                    <button class="btn btn-danger btn-sm dropdown-toggle" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                          Select a Condition
                    </button>
                    <div class="dropdown-menu">
                        <span class="dropdown-item" value="suitability">Suitability</span>
                        <span class="dropdown-item" value="informative">Informative</span>
                        <span class="dropdown-item" value="diversity">Diversity</span>
                        <span class="dropdown-item" value="sentence_complexity">Sentence Complexity</span>
                        <span class="dropdown-item" value="lexical_complexity">Lexical Complexity</span>
                    </div>
                </div>
            </td>
        </tr>
    """
    condition_list = []
    for sent in info["w1_sent"]+info["w2_sent"]: 
        sent["display_sent"] = turn_highlight(sent["display_sent"])
        res = condition_template.replace("{{id}}", sent["id"]).replace("{{sent}}", sent["display_sent"])
        condition_list.append(res)
    stage_two_content = "\n".join(condition_list)

    # stage 3 
    choose_template = """
        <div class="not_selected sentence" id="{{id}}"><span class="badge"> </span> {{sent}} </div>
    """
    choose_list_1 = []
    for sent in info["w1_sent"]:
        res = choose_template.replace("{{id}}", sent["id"]).replace("{{sent}}", sent["display_sent"])
        choose_list_1.append(res)

    choose_list_2 = []
    for sent in info["w2_sent"]:
        res = choose_template.replace("{{id}}", sent["id"]).replace("{{sent}}", sent["display_sent"])
        choose_list_2.append(res)

    choose_content_1 = "\n".join(choose_list_1)
    choose_content_2 = "\n".join(choose_list_2)

    # fill in all data
    html = template.replace("{{w1}}", w1).replace("{{w2}}", w2).replace("{{stage_one_content}}", stage_one_content).replace("{{stage_two_content}}", stage_two_content)
    html = html.replace("{{choose_content_1}}", choose_content_1).replace("{{choose_content_2}}", choose_content_2)
    html = html.replace("{{index}}", str(info["index"])).replace("{{sent_num}}", str(len(info["w2_sent"])+len(info["w1_sent"])))

    return html

def render_batch():
    with open("data_with_id.json", 'r', encoding='utf-8') as infile:
        data = json.load(infile)

    with open("useful_template.html", 'r', encoding='utf-8') as infile:
        template = infile.read()

    for i, info in enumerate(data[:]):
        html = render_html(template, info)

        with open("html_0526/{:0>3}.html".format(i), 'w', encoding='utf-8') as outfile:
            outfile.write(html)

def main():
    #load_data()
    #check_data()
    #check_repeat()
    render_batch()

if __name__ == "__main__":
    main()
