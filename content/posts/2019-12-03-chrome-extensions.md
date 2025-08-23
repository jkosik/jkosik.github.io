---
title: "Google Chrome Extension"
date: 2019-12-03T14:15:05+07:00
slug: /google-chrome/
description: How to build simple Chrome Extension from scratch.
image: images/chrome-extension/big.png
categories:
  - tech
tags:
  - browser
  - google
draft: false
---
Have you been looking for a Google Chrome Extension precisely for your usecase without any luck? Have you spent searching and trying this or that alternative and still have not found the right one? If you have been considering to write your own Chrome plugin, I am sharing a brief tutorial how to create own Extension without need to go through the extensive documentation.

## A bit of theory
Google Chrome Extensions are in fact small web pages. They utilize well-known technologies as HTML, CSS and JavaScript. JavaScript is doing the heavy lifting and talks to Chrome APIs to get more functionalities.

Logic of your Extension can runs in three contexts:
1) Content context - `content.js` has access to the page's [DOM](https://en.wikipedia.org/wiki/Document_Object_Model) and can inject code to the page (nice attack vector for malicious guys :) ).
2) Background context - `background.js` lives in an isolated area, intercepts browser actions and accesses Chrome APIs. Does not see the DOM.
3) Popup context - `popup.html` provides nice looking UI. Does have access to Chrome APIs similarly to `background.js`.

`Content` and `Background` contexts are separated and can interact by [Message Passing](https://developer.chrome.com/extensions/messaging). You do not always need to use all three contexts.

## Task
Imagine an Chrome Extension which will provide UI where the customer can find various external sites which might execute scan of the domain you are currently browsing. You should have a possibility to select only the relevant ones and Chrome should remember your selection.

## File structure
We need several files.
{{< figure src="images/chrome-extension/files.png" >}}

### manifest.json
`manifest.json` contains Extension metadata, links to scripts, permission configuration and plenty of other settings. Please see [Chrome Docs](https://developers.chrome.com/extensions/manifest) for more information.

```
{
  "manifest_version": 2,
  "name": "ScanDomain",
  "description": "ScanDomain",
  "version": "0.0.1",
  "icons":  {
    "64": "img/icon.png"
  },
  "browser_action": {
    "default_icon": "img/icon.png",
    "default_title": "ScanDomain",
    "default_popup": "popup.html"
  },
  "permissions": ["activeTab", "notifications", "storage"]
}
```

### popup.html
`popup.html` opens up upon clicking on the Extension icon in the browser toolbar. HTML document can be enrich by CSS and JavaScript. Usage of locally linked `script/popup.js` JavaScript is preferred.

*Note: JavaScript present directly in the `popup.html` is not recommended due to [Content Security Policy](https://en.wikipedia.org/wiki/Content_Security_Policy) limitations. CSP can be still configured in `manifest.json`. Chrome helps you here by calculating sha256 hash of your JavaScript code or suggests using the nonce for permitting your in-html JavaScript code.*

```
<html>

<head>
    <link rel="stylesheet" type="text/css" href="css/popup.css">
    <script src="script/popup.js"></script>
</head>

<body>

    <input id="check1" type="checkbox" name="check1" value="Qualys" checked>
    <label for="check1">Qualys</label><br>
    <input id="check2" type="checkbox" name="check2" value="MXtoolbox" checked>
    <label for="check2">MXtoolbox</label><br>
    <input id="check3" type="checkbox" name="check3" value="Shodan" checked>
    <label for="check3">Shodan</label><br><br>

    <button class="btn btn-3" id="launch" type="button" name="launch">Launch ScanDomain</button>

</body>
</html>
```

### popup.js
`popup.js` Plays with the DOM of the `popup.html` and talks to Chrome APIs.
Please find the comment lines in the code below.


```
//popup.js

//setting parameters fro Chrome notification window
var options = {
    type: "basic",
    title: "ScanDomain",
    message: "New browser tabs are opened based on selected options.",
    iconUrl: "img/icon.png"

};

//optional callback function when triggering Chrome notification window
function creationCallback() {
  console.log("Notification triggered");
}

//main part. Runs whenever popup.html is loaded
document.addEventListener('DOMContentLoaded', function() {

  //load and update checkbox states as stored in local Chrome storage
  chrome.storage.sync.get('check1', function (data){
    document.getElementById('check1').checked = data.check1;
  });
  chrome.storage.sync.get('check2', function (data){
    document.getElementById('check2').checked = data.check2;
  });
  chrome.storage.sync.get('check3', function (data){
    document.getElementById('check3').checked = data.check3;
  });

  //store checkbox states to local Chrome storage upon clicking Launch button
  document.getElementById("launch").onclick = function () {
    var value1 = document.getElementById('check1').checked;
    var value2 = document.getElementById('check2').checked;
    var value3 = document.getElementById('check3').checked;
    chrome.storage.sync.set({'check1': value1});
    chrome.storage.sync.set({'check2': value2});
    chrome.storage.sync.set({'check3': value3});

    //trigger Chrome notification
    chrome.notifications.create(options, creationCallback);

    //detect domain currently browsed by the user
    chrome.tabs.query({active: true, lastFocusedWindow: true, currentWindow: true}, function (tabs) {
      var tab = tabs[0];
      var url = new URL(tab.url);
      var domain = url.hostname;
      target1 = "https://www.ssllabs.com/ssltest/analyze.html?viaform=on&d=" + domain
      target2 = "https://mxtoolbox.com/SuperTool.aspx?action=mx%3a" + domain + "&run=toolpage"
      target3 = "https://www.shodan.io/search?query=" + domain

      //if option checked, open new tab
      if (document.getElementById('check1').checked) {
        chrome.tabs.create({"url": target1});
      }
      if (document.getElementById('check2').checked) {
        chrome.tabs.create({"url": target2});
      }
      if (document.getElementById('check3').checked) {
        chrome.tabs.create({"url": target3});
      }
    });

  };
});
```

## Code
You can find the final code [here](https://github.com/jkosik/scandomain).

## Installation
In Chrome:
1. Browse to `chrome://extensions/`
2. Enable `Developer mode`
3. Click on `Load unpacked` and select `scandomain` subfolder
4. Pin the Extension to the Chrome toolbar and use.

{{< figure src="images/chrome-extension/extension.png" >}}