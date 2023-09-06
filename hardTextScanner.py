#!/usr/bin/env python
# encoding: utf-8
import json
import logging
import time
import os

import threading

from flask import Flask, jsonify, request, g, render_template
from wordfreq import zipf_frequency
from PyDictionary import PyDictionary



# timezone
os.environ["TZ"] = "America/Los_Angeles"
time.tzset()

# logging options
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(asctime)s [%(levelname)s]: %(message)s')
log = logging.getLogger("hardTextScanner")

# app setup
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# dictionary setup
dictionary = PyDictionary()
#dictionary.set_words_lang('en')


# main app
@app.route('/hardTextScan', methods=['POST'])
def index():
    data = request.json
    text = data['payload']
    word_dict = dict()

    word_freq_start = time.time()
    for word_literal in text.split():
        if _is_word_eligible(word_literal):
            for word in _preprocess_word(word_literal):
                if word not in word_dict:
                    freq = zipf_frequency(word, 'en')
                    word_dict[word] = {"freq":freq, "count":1}
                else:
                    word_dict[word]["count"] += 1

    sorted_list = sorted(word_dict.items(), key=lambda x:x[1]["freq"])
    filtered_list = list(filter(lambda x:x[1]['freq'] != 0, sorted_list))
    word_freq_end = time.time()
    word_freq_diff = (word_freq_end - word_freq_start) * 1000

    #log.info(list(map(lambda x:x[0], filtered_list)))
    log.info("WordFreq Elapsed %.1f ms" % word_freq_diff)
    
    
    translate_start = time.time()
    response = list()
    for item in filtered_list:
        formated_item = _format_item(item)
        if formated_item['explain'] != None and len(formated_item['explain']) != 0:
            response.append(formated_item)
            if len(response) == 10:
                break
    translate_end = time.time()
    translate_diff = (translate_end - translate_start) * 1000
    log.info("Translate Elapsed %.1f ms" % translate_diff)
            
    #log.info(response)
    return render_template('result.html', items=response)


def _is_word_eligible(word):
    # todo: exclude names
    return word.isalpha()  

def _preprocess_word(word):
    res = []
    word = word.lower()
    if _not_empty(word) and word[-1] in ['.', ',', '?', '!', ')']:
        word = word[:-1] # remove appended punctuation
    if _not_empty(word) and word[0] in ['(', '@']:
        word = word[1:]
    if _not_empty(word) and '-' in word:
        res = word.split('-')
    res.append(word.replace('-', '')) # have potentially anti-social => [anti, social, antisocial]
    return res
        
def _not_empty(word):
    return word != None and len(word) > 0

def _format_item(item):
    return {
        "word": item[0], 
        "score": item[1]['freq'], 
        "explain": _get_meaning(item[0])
    }

def _get_meaning(word):
    try:
        #return dictionary.meaning('en', word, dictionary='wordnet')
        return dictionary.meaning(word)
    except Exception:
        return {}
    

@app.before_request
def before_request():
    g.start = time.time()

@app.after_request
def after_request(response):
    diff = (time.time() - g.start) * 1000
    log.info("Elapsed %.1f ms" % diff)
    return response


if __name__=="__main__":
    app.run(host='0.0.0.0', port=1921)
