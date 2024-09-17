#!/usr/bin/env python
# encoding: utf-8
import json
import logging
import time
import os
import markdown
import markdown.extensions.fenced_code

from openai import OpenAI

client = OpenAI(api_key=os.environ['OPEN_AI_KEY'])


import threading

from flask import Flask, jsonify, request, g, render_template



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
# dictionary = PyDictionary()
#dictionary.set_words_lang('en')

# llm setup
system_prompt = {"role": "system", "content": "Your job is to pick the top 10 hardest words from the user-provided text and come up with 3 synonyms for each of the hardes words you choose. Return in format of html language directly."}


@app.route('/hardTextScanLlm', methods=['POST'])
def scan_with_llm():
    data = request.json
    text = data['payload']

    messages = [
        system_prompt,
        {"role": "user", "content": text}
    ]

    response = client.chat.completions.create(
        messages=messages,
        temperature=0.1,
        model="gpt-3.5-turbo",
    )
    response_message = response.choices[0].message.content.encode('utf-8').decode()

    #md_template_string = markdown.markdown(response_message)

    print(response_message)
    return response_message



    

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
