---
title: "ModSecurity Rules Management in Kubernetes"
date: 2020-10-01T14:15:05+07:00
slug: /modsecurity/
description: ModSecurity-based Web application firewall in Kubernetes.
image: images/modsec-in-k8s/big.png
categories:
  - tech
tags:
  - kubernetes
  - security
draft: false
---
*This article was published in the Deutsche Telekom Pan-Net Blog*

## How to manage ModSecurity rules for Nginx using web UI, Kubernetes, CICD and git
Most of the online companies nowadays understand the risk of exposing web applications to the Internet. We are not any exception. As many others we are running the workloads in Kubernetes and try to utilize this platform for ensuring application security as well.

The most convenient option is to utilize Kubernetes Ingress Annotations and [Nginx](https://www.nginx.com) & [ModSecurity](https://www.modsecurity.org) or [Openresty](https://openresty.org) as a WAF(Web Application Firewall) solution. This option works well, but brings a bit of operational overhead. Sharing the rules among WAFs is not streamlined and every application has to manage security on its own.

In DT Pan-Net we have decided to stick to solid and time-tested technologies and selected Nginx and ModSecurity to build WAF as a Service in Kubernetes with user-friendly management of WAF rules via UI.

This blog does not have intention to provide a deep dive to the to complexity of the product called [Pan-Net WebShield](https://portal.webshield.pan-net.cloud), rather to focus on one specific infrastructure fragment – WAF rules management using Nginx, ModSecurity, Kubernetes, git and CICD pipelines.

### The high-level architecture:

{{< figure src="images/modsec-in-k8s/blog1.png" >}}

WAF Portal acts as a full-blown self-service UI and provides the user a capability to select arbitrary combination of WAF rules. Each combination refers to a Kubernetes [ConfigMap](https://kubernetes.io/docs/concepts/configuration/configmap/) containing set of WAF rules - RuleSets.

### How are the RuleSet ConfigMaps created, maintained and what do they contain?

#### Terminology used in this blog:
**Rule** is a ModSecurity syntactical line, e.g.:
`SecRule ARGS:ip ";" "t:none,log,deny,msg:'semi colon test',id:2"`

**RuleFile** is a file containing group of Rules used by a Nginx & ModSecurity, e.g.:
`REQUEST-930-APPLICATION-ATTACK-LFI.conf`

**RuleSet** is a group of RuleFiles, e.g. RuleSet 100:
```
# Scanners
100:
- REQUEST-913-SCANNER-DETECTION.conf
- REQUEST-921-PROTOCOL-ATTACK.conf
```

ModSecurity RuleFiles are grouped to RuleSets and presented in UI in a human-understandable way:
{{< figure src="images/modsec-in-k8s/blog2.png" >}}

Grouping of the RuleFiles to the RuleSets is kept in a base YAML file where each key represents one RuleSet:
```
…
# Essential
50:
- REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf
- REQUEST-901-INITIALIZATION.conf
- REQUEST-905-COMMON-EXCEPTIONS.conf
- REQUEST-911-METHOD-ENFORCEMENT.conf
- REQUEST-920-PROTOCOL-ENFORCEMENT.conf
- REQUEST-949-BLOCKING-EVALUATION.conf
- RESPONSE-959-BLOCKING-EVALUATION.conf
- RESPONSE-980-CORRELATION.conf
- RESPONSE-999-EXCLUSION-RULES-AFTER-CRS.conf
- RESPONSE-950-DATA-LEAKAGES.conf
- RESPONSE-954-DATA-LEAKAGES-IIS.conf

# Scanners
100:
- REQUEST-913-SCANNER-DETECTION.conf
- REQUEST-921-PROTOCOL-ATTACK.conf

# File Inclusion
150:
- REQUEST-930-APPLICATION-ATTACK-LFI.conf
- REQUEST-931-APPLICATION-ATTACK-RFI.conf
- REQUEST-943-APPLICATION-ATTACK-SESSION-FIXATION.conf

# Code Execution
200:
- REQUEST-932-APPLICATION-ATTACK-RCE.conf
...
```

Base YAML file is processed by a Python script and creates as many RuleSet ConfigMaps in the Kubernetes cluster as there are combinations of the keys in the input YAML file.
The structure of the resulting RuleSet ConfigMaps reflects the need of Nginx & ModSecurity Docker image. That is why all the RuleFiles are prefixed with “Includes” keyword and full path when deploying the ConfigMap.

RuleSet ConfigMap below was created out for the combination of RuleSets 100, 150 and 200. Note that all RuleSet ConfigMaps are always extended by a RuleSet 50 (to be explained in a while):

```
$ kubectl describe cm rules-50-100-150-200

Name:         rules-50-100-150-200
Namespace:    webshield-stage
Labels:       app=waf
              config=rules
              infra=webshield
Annotations:  <none>

Data
====
pan-net-rules.conf:
----
Include /etc/nginx/modsecurity/crs/rules/REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf
Include /etc/nginx/modsecurity/crs/rules/REQUEST-901-INITIALIZATION.conf
Include /etc/nginx/modsecurity/crs/rules/REQUEST-905-COMMON-EXCEPTIONS.conf
Include /etc/nginx/modsecurity/crs/rules/REQUEST-911-METHOD-ENFORCEMENT.conf
Include /etc/nginx/modsecurity/crs/rules/REQUEST-913-SCANNER-DETECTION.conf
Include /etc/nginx/modsecurity/crs/rules/REQUEST-920-PROTOCOL-ENFORCEMENT.conf
Include /etc/nginx/modsecurity/crs/rules/REQUEST-921-PROTOCOL-ATTACK.conf
Include /etc/nginx/modsecurity/crs/rules/REQUEST-930-APPLICATION-ATTACK-LFI.conf
Include /etc/nginx/modsecurity/crs/rules/REQUEST-931-APPLICATION-ATTACK-RFI.conf
Include /etc/nginx/modsecurity/crs/rules/REQUEST-932-APPLICATION-ATTACK-RCE.conf
Include /etc/nginx/modsecurity/crs/rules/REQUEST-943-APPLICATION-ATTACK-SESSION-FIXATION.conf
Include /etc/nginx/modsecurity/crs/rules/REQUEST-949-BLOCKING-EVALUATION.conf
Include /etc/nginx/modsecurity/crs/rules/RESPONSE-950-DATA-LEAKAGES.conf
Include /etc/nginx/modsecurity/crs/rules/RESPONSE-954-DATA-LEAKAGES-IIS.conf
Include /etc/nginx/modsecurity/crs/rules/RESPONSE-959-BLOCKING-EVALUATION.conf
Include /etc/nginx/modsecurity/crs/rules/RESPONSE-980-CORRELATION.conf
Include /etc/nginx/modsecurity/crs/rules/RESPONSE-999-EXCLUSION-RULES-AFTER-CRS.conf
```

### RuleSet 50
Each RuleSet ConfigMap contains also additional RuleFiles (RuleSet 50). RuleSet 50 – Essential Ruleset enforces basic level of security and enables us to enforce globally the rules we consider mandatory.

Now it is pretty clear how RuleSet ConfigMaps are created. And now we need to inject them to Kubernetes Pods running the WAF itself.

We do that by RuleSet ConfigMap mounts in the Deployment manifest (200+ lines including HorizontalPodAutoscaler, PodDisruptionBudget, Update Strategies, sidecar containers and other mounts related to TLS certificates or other templated configuration files)

```
kind: Deployment
...
    spec:
      containers:
      - image: {{WAF_IMAGE}}
      …
        volumeMounts:
        ...
        - name: rulesetconf
          mountPath: /etc/nginx/modsecurity/pan-net-rules.conf
          subPath: pan-net-rules.conf
          readOnly: true
          ...
      volumes:
      …
      - name: rulesetconf
        configMap:
          name: {{RULESET}}
          items:
          - key: pan-net-rules.conf
            path: pan-net-rules.conf
      ...
```

Each selected option in the Portal form holds a key matching the RuleSet key in the base YAML file. Selected keys are sorted and appended to build up a final aggregated key to identify the desired RuleSet ConfigMap Name `{{RULESET}}` to mount. Aggregated key is also stored to the database.

Kubernetes Jobs running on the background template the Deployment manifest which picks up the right RuleSet ConfigMap based on aggregated key from the database.

{{< figure src="images/modsec-in-k8s/blog3.png" >}}

RuleSet ConfigMap contents is mounted to `/etc/nginx/modsecurity/pan-net-rules.conf` inside the WAF Pods and is recognized by `/etc/nginx/modsecurity/nginx-modsecurity.conf` which governs inclusion of ModSecurity configuration files.

`nginx-modsecurity.conf` originally includes hardcoded CRS RuleFiles. Yet we rather include our own file with dynamic contents.
Our `/etc/nginx/modsecurity/nginx-modsecurity.conf`:

```
Include /etc/nginx/modsecurity/modsecurity.conf
Include /etc/nginx/modsecurity/crs/setup.conf
#Include /etc/nginx/modsecurity/crs/rules/*.conf
Include /etc/nginx/modsecurity/pan-net-rules.conf
Include /etc/nginx/modsecurity/ruleset-extra.conf
```

Another important file is `/etc/nginx/modsecurity/modsecurity.conf` primarily due to presence of `SecRuleEngine` directive with available values `On|Off|DetectionOnly`.
`SecRuleEngine` makes decision whether the malicious traffic is blocked or logged only. As we want the user to be able to run WAF in logging-only mode and inspect WAF behavior prior enforcing any RuleSets, it is necessary to modify this option on the fly upon user’s selection in the WAF Portal as well – we call this feature Blocking Mode.

{{< figure src="images/modsec-in-k8s/blog4.png" >}}

Implementation is similar to RuleSet deployment and can happen instantly without need to rebuild Docker images.

All the files mentioned so far including infrastructure provisioning code are stored in git. Infrastructure as a code and CICD governs everything for us. Only git commits and database changes are triggers for any infrastructure change. Changes are tested in a dedicated Kubernetes namespaces starting by unit test, followed by integration tests and finalized by Robot Framework Selenium tests.

### How does the process of adding new Rules or RuleFiles look like?
Adding/updating Rules in existing RuleSets is the most frequent usecase and the solution must be as smooth as possible. We only need to insert a new Rule to the existing RuleFile in the Docker image from which WAF is spawned. No new RuleFiles are created thus the change is confined in the Docker image itself. RuleSet ConfigMaps are mounted to the containers the way as before, yet they now refer to the updated RuleFiles with newly added ModSecurity Rules inside the Docker image.

Adding new RuleFiles or even RuleSets is a more complex usecase and is beyond the scope of this blog. It combines updating the Docker image for WAF, updating existing RuleSet ConfigMaps and if needed also updating WAF Portal web form. Even though it might look difficult, CICD pipelines automate much of that.

All information mentioned until now ensure consistent management of global WAF rules applied for all WAF instances.

We have identified also usecases of having custom WAF rules per WAF instance, e.g. due to specific nature or sensitivity of protected application. We had to introduce mechanism to flexibly manage and propagate WAF rules only to a subset of WAF instances. It is useful also for canary testing of the new WAF Rules without risk of affecting the whole user base.

### Per-WAF Rules management
We have defined the design principle to be able to add new WAF Rules on the fly per WAF instance without need to rebuild any Docker images which might affect other customers or be overly complex. To explain our approach of per-WAF Rules management, let’s come back to `/etc/nginx/modsecurity/nginx-modsecurity.conf` and focus on a different line for now:

```
Include /etc/nginx/modsecurity/modsecurity.conf
Include /etc/nginx/modsecurity/crs/setup.conf
#Include /etc/nginx/modsecurity/crs/rules/*.conf
Include /etc/nginx/modsecurity/pan-net-rules.conf
Include /etc/nginx/modsecurity/ruleset-extra.conf
```

`/etc/nginx/modsecurity/ruleset-extra.conf` file is part of the Docker image for WAF and evaluated by Nginx and ModSecurity the same way as `/etc/nginx/modsecurity/pan-net-rules.conf`. This file is by default empty. During the WAF provisioning process, empty ConfigMap mounts to this path and is a subject of git-driven updates only when needed:

{{< figure src="images/modsec-in-k8s/blog5.png" >}}

There is a prescribed file structure in git for this purpose. As we have more environments, each one represents a separate directory (e.g. pub-prod) with files per-WAF inside (e.g. `cm-ruleset-extra-62p79wzc.yaml`). File names are as follows: `cm-ruleset-extra-UNIQUE_WAF_ID.yaml`. These files may contain Rule excludes or ModSecurity Rules themselves:

{{< figure src="images/modsec-in-k8s/blog6.png" >}}

For CICD purposes we are utilizing GitLab pipelines triggered by changes of the respective files:

```
pub-prod-deploy-ruleset-cm-extra:
  extends:
    - .k8s-auth
    - .setup-ruleset-extra
  variables:
    ENV: "pub-prod"
    RULE_FOLDER: "configuration/wafdeployer/rulesets-extra/pub-prod/"
  only:
    refs:
      - master
    changes:
      - configuration/wafdeployer/rulesets-extra/pub-prod/*.{yaml,yml}
    variables:
      - $ACTION == null
```

`.setup-ruleset-extra` “extend” parses the file name and templates underlying ConfigMap mounted to `/etc/nginx/modsecurity/ruleset-extra.conf` for that specific WAF instance. The last step of the pipeline is to trigger rolling restart and check its success. Automated cleanup scripts revert ConfigMaps back to default (empty) state when git files are removed.

Alternative option is to let users manage custom rules per their WAF instances via the WAF Portal. For now we opt for not enabling it. Writing ModSecurity rules can become quite complex requiring thorough testing, understanding of Nginx and ModSecurity logs and security expert knowledge.

### Conclusion
Kubernetes provides suitable platform for running atomic WAF instances with unified approach of configuration and updates. Above-mentioned architecture fulfills zero-downtime operation and native scalability.

Combination of Nginx & ModSecurity provides feature-rich and extensible twin for building full-blown WAF solutions. By adding a database layer for keeping the state information and graphical UI anybody can build a powerful platform.
