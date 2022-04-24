from pickle import FALSE
import re
import nltk
import tkinter as tk
from tkinter import filedialog
import numpy
import gender_guesser.detector as gender

from itertools import tee, islice, chain
# Ref: http://nealcaren.github.io/text-as-data/html/times_gender.html
# Two lists  of words that are used when a man or woman is present, based on Danielle Sucher's https://github.com/DanielleSucher/Jailbreak-the-Patriarchy
male_words=set(['guy','spokesman','chairman',"men's",'men','him',"he's",'his','boy','boyfriend','boyfriends','boys','brother','brothers','dad','dads','dude','father','fathers','fiance','gentleman','gentlemen','god','grandfather','grandpa','grandson','groom','he','himself','husband','husbands','king','male','man','mr','nephew','nephews','priest','prince','son','sons','uncle','uncles','waiter','widower','widowers'])
female_words=set(['heroine','spokeswoman','chairwoman',"women's",'actress','women',"she's",'her','aunt','aunts','bride','daughter','daughters','female','fiancee','girl','girlfriend','girlfriends','girls','goddess','granddaughter','grandma','grandmother','herself','ladies','lady','lady','mom','moms','mother','mothers','mrs','ms','niece','nieces','priestess','princess','queens','she','sister','sisters','waitress','widow','widows','wife','wives','woman'])
male_words_with_name = set(male_words)
female_words_with_name = set(female_words)


def read_articles_from_gui():
    root = tk.Tk()
    root.withdraw()

    content_list = list()
    file_path = filedialog.askopenfilenames(title='Select Articles', filetypes=[
        ("Text Files", ".txt")
    ])
    for entry in file_path:
        with open(entry, 'r', encoding='UTF-8') as file_opened:
            text = file_opened.read()
            content_list.append(text)

    return content_list

def create_name_dict(content_list):
    # key: name; value: list([gender, count])
    name_dict = dict()
    for text in content_list:
        for person in get_human_names(text):
            name_dict[person] = ["unknown", 0]
    
    return name_dict

def read_article(path):
    a_file = open("sample.txt", "r")
    text = a_file.read()
    a_file.close()
    return text

def parse_article(str):
    list_of_words = re.findall(r'\w+', str)
    return list_of_words

def clean_list_for_name_extraction(list_of_tagged_words):
    # deal with Mr as NNP, so a full name is expected as [firstname, lastname]
    cleaned_list = list(list_of_tagged_words)
    for pair in list_of_tagged_words:
        if pair[0].lower() in male_words:
            print(pair)
            cleaned_list.remove(pair)
        if pair[0].lower() in female_words:
            print(pair)
            cleaned_list.remove(pair)
    print(cleaned_list)
    return cleaned_list

def article_analysis(list_of_tagged_words, name_dict):
    name_count = 0
    male_count = 0
    female_count = 0
    andy_count = 0

    # check gender
    d = gender.Detector()
    skip = 0
    cleaned_list = clean_list_for_name_extraction(list_of_tagged_words)
    copy_for_next = list(cleaned_list)
    copy_for_next.append([None])
    for pair, next in zip(cleaned_list, copy_for_next):
        if skip == 1:
            skip = 0
            continue

        name = pair[0]
        tag = pair[1]

        if tag != "NNP": continue
        # skip the name "The" in Korea
        if name == "The": continue
        if len(name) <= 1: continue

        for p in name_dict.keys():
            if name in p:
                print("Name " + name + " is found in person list as " + p)
                result = d.get_gender(name)
                value = name_dict[p]
                value[0] = result
                value[1] = value[1] + 1
                name_dict[p] = value

                if result == "male" or result == "mostly_male":
                    name_count += 1
                    male_count += 1
                    male_words_with_name.add(name.lower())
                    print(name + " is found to be male.")
                elif result == "female" or result == "mostly_female":
                    name_count += 1
                    female_count += 1
                    female_words_with_name.add(name.lower())
                    print(name + " is found to be female.")
                elif result == "andy":
                    name_count += 1
                    andy_count += 1
                    print(name + " is found to be androgynous.")
                if (next[1] == "NNP"):
                    skip = 1
    
    print("There are " + str(name_count) + " names identified in the article.")
    print("There are " + str(male_count) + " male names in total.")
    print("There are " + str(female_count) + " female names in total.")
    print("There are " + str(andy_count) + " androgynous names in total.")

    print
    print(male_words_with_name)
    print(male_words_with_name)

    one_third_count = 1 + (len(list_of_tagged_words) // 3)
    one_third_result = list([[0, 0],
                             [0, 0],
                             [0, 0]])
    for i in range(0, one_third_count):
        pair = list_of_tagged_words[i]
        word = pair[0].lower()
        if word in male_words_with_name:
            print(word + " is count for male in 1/3.")
            one_third_result[0][0] = one_third_result[0][0] + 1
        if word in female_words_with_name:
            print(word + " is count for female in 1/3.")
            one_third_result[0][1] = one_third_result[0][1] + 1
    for i in range(one_third_count, 2 * one_third_count):
        pair = list_of_tagged_words[i]
        word = pair[0].lower()
        if word in male_words_with_name:
            print(word + " is count for male in 2/3.")
            one_third_result[1][0] = one_third_result[1][0] + 1
        if word in female_words_with_name:
            print(word + " is count for female in 2/3.")
            one_third_result[1][1] = one_third_result[1][1] + 1
    for i in range(2 * one_third_count, len(list_of_tagged_words)):
        pair = list_of_tagged_words[i]
        word = pair[0].lower()
        if word in male_words_with_name:
            print(word + " is count for male in 3/3.")
            one_third_result[2][0] = one_third_result[2][0] + 1
        if word in female_words_with_name:
            print(word + " is count for female in 3/3.")
            one_third_result[2][1] = one_third_result[2][1] + 1

    return one_third_result

def get_human_names(text):
    tokens = nltk.tokenize.word_tokenize(text)
    pos = nltk.pos_tag(tokens)
    sentt = nltk.ne_chunk(pos, binary = False)
    person_list = []
    person = []
    name = ""
    for subtree in sentt.subtrees(filter=lambda t: t.label() == 'PERSON'):
        for leaf in subtree.leaves():
            person.append(leaf[0])
        if len(person) > 0: #avoid grabbing lone surnames
            for part in person:
                name += part + ' '
            #check duplicates
            if not any(name in p for p in person_list):
                for p in person_list:
                    if p in name:
                        person_list.remove(p)
                        person_list.append(name[:-1])
                        break
                else:
                    person_list.append(name[:-1])
            name = ''
        person = []

    return (person_list)

full_content_list = read_articles_from_gui()
name_dict = create_name_dict(full_content_list)
for article in full_content_list:
    list_of_words = parse_article(article)
    tagged_words = nltk.pos_tag(list_of_words)
    result_list = article_analysis(tagged_words, name_dict)
    print(result_list)

print("\nCount:")
for name, count in name_dict.items():
    print("%20s: %20s" % (name, count))

# path = "sample.txt"
# text = read_article(path)
# list_of_words = parse_article(text)
# tagged_words = nltk.pos_tag(list_of_words)
# person_list = get_human_names(text)
# # print(tagged_words)
# print(get_human_names(text))
# name_dict = article_analysis(tagged_words, person_list)





