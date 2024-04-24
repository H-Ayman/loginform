#!/usr/bin/env python
import sys
import requests
from argparse import ArgumentParser
from collections import defaultdict
from bs4 import BeautifulSoup


def form_score(form):
    score = 0
    inputs = form.find_all("input")
    typecount = defaultdict(int)
    for input_tag in inputs:
        type_ = input_tag.get("type", "").lower()
        typecount[type_] += 1

    if len(inputs) in (2, 3):
        score += 10

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


def pick_form(forms):
    """Return the form most likely to be a login form"""
    return sorted(forms, key=form_score, reverse=True)[0]


def pick_fields(form):
    """Return the most likely field names for username and password"""
    user_field = pass_field = None
    inputs = form.find_all("input")
    for input_tag in inputs:
        type_ = input_tag.get("type", "").lower()
        if type_ == 'text' and not user_field:
            user_field = input_tag.get("name")
        elif type_ == 'password' and not pass_field:
            pass_field = input_tag.get("name")

    return user_field, pass_field


def detect_login_forms(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        forms = soup.find_all('form')
        login_forms = []

        for form in forms:
            user_field, pass_field = pick_fields(form)
            if user_field and pass_field:
                action_url = form.get('action') or response.url
                method = form.get('method', 'get')
                login_forms.append({
                    'action': action_url,
                    'method': method,
                    'username_field': user_field,
                    'password_field': pass_field
                })
    except requests.RequestException as e:
        print(f"Error occurred while fetching URL: {e}")
        return []

    return login_forms


def main():
    ap = ArgumentParser()
    ap.add_argument('url', help='URL to detect login forms')
    args = ap.parse_args()

    login_forms = detect_login_forms(args.url)
    if login_forms:
        print("Login forms detected:")
        for idx, form in enumerate(login_forms, start=1):
            print(f"Form {idx}:")
            print(f"Action URL: {form['action']}")
            print(f"Method: {form['method']}")
            print(f"Username Field: {form['username_field']}")
            print(f"Password Field: {form['password_field']}")
            print()
    else:
        print("No login forms detected on the provided URL.")


if __name__ == '__main__':
    sys.exit(main())
