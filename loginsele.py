#!/usr/bin/env python
import sys
from time import sleep
from argparse import ArgumentParser
from collections import defaultdict
from lxml import html
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options


__version__ = '1.2.0'


def _form_score(form):
    score = 0
    # In case of user/pass or user/pass/remember-me
    if len(form.inputs.keys()) in (2, 3):
        score += 10

    typecount = defaultdict(int)
    for x in form.inputs:
        type_ = x.type if isinstance(x, html.InputElement) else "other"
        typecount[type_] += 1

    if typecount['text'] > 1:
        score += 10
    if not typecount['text']:
        score -= 10

    if typecount['password'] == 1:
        score += 10
    if not typecount['password']:
        score -= 10

    if typecount['checkbox'] > 1:
        score -= 10
    if typecount['radio']:
        score -= 10

    return score


def _pick_form(forms):
    """Return the form most likely to be a login form"""
    return sorted(forms, key=_form_score, reverse=True)[0]


def _pick_fields(form):
    """Return the most likely field names for username and password"""
    userfield = passfield = emailfield = None
    for x in form.inputs:
        if not isinstance(x, html.InputElement):
            continue

        type_ = x.type
        if type_ == 'password' and passfield is None:
            passfield = x.name
        elif type_ == 'email' and emailfield is None:
            emailfield = x.name
        elif type_ == 'text' and userfield is None:
            userfield = x.name

    return emailfield or userfield, passfield    


def submit_value(form):
    """Returns the value for the submit input, if any"""
    for x in form.inputs:
        if not isinstance(x, html.InputElement):
            continue

        if x.type == "submit" and x.name:
            return [(x.name, x.value)]
    else:
        return []


def fill_login_form(url, body, username, password):
    doc = html.document_fromstring(body, base_url=url)
    form = _pick_form(doc.xpath('//form'))
    userfield, passfield = _pick_fields(form)
    form.fields[userfield] = username
    form.fields[passfield] = password
    form_values = form.form_values() + submit_value(form)
    return form_values, form.action or form.base_url, form.method


def main():
    ap = ArgumentParser()
    ap.add_argument('-u', '--username', default='username')
    ap.add_argument('-p', '--password', default='secret')
    ap.add_argument('url')
    args = ap.parse_args()

    try:
        r = requests.get(args.url)
        values, action, method = fill_login_form(args.url, r.text, args.username, args.password)
        print(u'url: {0}\nmethod: {1}\npayload:'.format(action, method))
        for k, v in values:
            print(u'- {0}: {1}'.format(k, v))

        # Selenium setup to open the logged-in page
        options = Options()
        options.headless = True  # Set to False if you want to see the browser
        driver = webdriver.Firefox(options=options)
        driver.get(action)
        # You can add further actions here, such as clicking on links or buttons
        # Example:
        # driver.find_element_by_xpath("//a[contains(text(),'Dashboard')]").click()
        sleep(30)
        driver.quit()  # Close the browser after use
    except ImportError:
        print('requests library is required to use loginform as a tool')


if __name__ == '__main__':
    sys.exit(main())
