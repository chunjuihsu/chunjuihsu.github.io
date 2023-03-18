---
author: "CJ Hsu"
title: "How to Resolve 'Bad Request' with UrlFetchApp.fetch() in Apps Script"
date: "2023-03-18"
summary: "Try UrlFetchApp.fetchAll() when UrlFetchApp.fetch() doesn't work."
description: "Try UrlFetchApp.fetchAll() when UrlFetchApp.fetch() doesn't work."
categories: ["Tech"]
tags: ["How-to", "Apps Script", "API"]
---

Recently, I encountered a "bad request" issue while using the Apps Script method UrlFetchApp.fetch() to send an API POST request. The error wasn't caused by the API because I was able to make the same request successfully using Python. After researching the issue online, I discovered that UrlFetchApp.fetch() can sometimes fail for unknown reasons, and many people suggest using the method UrlFetchApp.fetchAll() instead. Fortunately, UrlFetchApp.fetchAll() worked perfectly in my case.

The code block below illustrates a case of bad request where UrlFetchApp.fetch() is used.

```javascript

const [header, ...data] = sheet.getDataRange().getValues();
const url = 'https://api.com';

const payload = {
    'name': 'Bob Smith',
    'age': 21
};

const options = {
  'method' : 'post',
  'payload' : JSON.stringify(payload),
  'muteHttpExceptions': true
}

const response = UrlFetchApp.fetch(url, options);

Logger.log(response.getResponseCode());
//400 Bad Request

```

Use UrlFetchApp.fetchAll() instead.

```javascript

const [header, ...data] = sheet.getDataRange().getValues();
const url = 'https://api.com';

const payload = {
    'name': 'Bob Smith',
    'age': 21
};

const request = {
    'url': url,
    'method' : 'post',
    'payload' : JSON.stringify(payload),
    'muteHttpExceptions': true
};

const response = UrlFetchApp.fetchAll([request])[0];

Logger.log(response.getResponseCode());
//200 OK

```