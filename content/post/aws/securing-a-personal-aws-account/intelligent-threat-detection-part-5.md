---
title: "Part 5 - AWS For Personal Use/Learning: Intelligent Threat Detection"
date: 2021-06-19T15:58:00-06:00
draft: false
toc: true
tags:
  - aws
  - reference
  - cloud security
  - amazon guardduty 
  - aws organizations
---
_This is the fifth and final post in what is a multi-part series on some suggestions based on AWS Well-Architected Framework best practices focused on setting up an AWS account(s) for personal use and learning. For other parts in the series see:_
  - _[Part 1 - AWS For Personal Use/Learning: Secure Multi-Account Setup][part-1]_
  - _[Part 2 - AWS For Personal Use/Learning: Identity and Access Management][part-2]_
  - _[Part 3 - AWS For Personal Use/Learning: Account Level Guardrails][part-3]_
  - _[Part 4 - AWS For Personal Use/Learning: The Audit Trail][part-4]_

If you have IAM identities (users, roles) and compute workloads running in AWS, there is no excuse to not be using [Amazon GuardDuty][gduty-service]. AWS calls GuardDuty "intelligent threat detection" and it was originally focused on identifying and alerting to potential threats/signs of compromise in IAM and EC2. Not too long ago, as the Amazon Macie service was matured and more tightly integrated into AWS (Macie was the result of an acquisition and looked rather different from other AWS consoles for a long time), it was apparent that Macie overlapped with GuardDuty in a few ways. Macie stopped processing CloudTrail for anomaly detection, and because GuardDuty was already looking for badness in control/management plane CloudTrail logging, it took over the processing of data plane (S3) CloudTrail events to look for badness there too.

## 30,000 ft View - How Does It Work?
So, how does GuardDuty apply intelligent threat detection to AWS accounts? The combination of lots of log processing, machine learning/anomaly detection and threat intelligence feeds make it possible. GuardDuty (when not configured for S3 monitoring) processes logs from three source:

  1. CloudTrail management plane logs
  2. VPC Flow logs
  3. DNS query logs

The awesome thing with all these logs is GuardDuty processes these in an independent stream; account owners don't need to turn these logs sources on, let alone store them in S3 or some other AWS storage solution for GuardDuty to work. I imagine that because AWS is generating the CloudTrail and VPC flow logs regardless of whether customers use it, they are able to just tap GuardDuty in to those streams. For the DNS logs, so long as the default VPC DNS resolver is being used (I'd imagine most people don't reconfigure that in VPCs), GuardDuty taps in to those logs too, which is really handy given that there is no way for customers to access those DNS logs.

It's extremely helpful to have access to all those log sources with the GuardDuty service, because from what I've seen so far, many organizations using AWS don't collect and store VPC flow logs due to the sheer volume that can be generated. Network flow data is also not always particularly helpful on it's own. So, between the perceived low value of the log and the likely high cost of collecting and storing them, many organizations seem to not bother with VPC flow data. Additionally, as mentioned, the DNS logs are not available to customers of AWS when using the default resolver configured through the VPC's DHCP options. In the security world, however, DNS logs can be extremely high value for detecting compromise through activity like beaconing, data exfiltration, etc.

GuardDuty is a surprisingly cheap service. AWS offers a 30-day free trial which will help determine a baseline cost to work off of going forward. After that, depending on how much is happening in the various accounts GuardDuty is watching, costs can be very low to more than expected. I've seen it cost as little as $50/day in a single account and region. That daily cost was in a large scale account generating well over 100GB of CloudTrail, hundreds of GB of VPC flow and similar volumes of DNS logs daily. For personal use, GuardDuty has never come close to costing me even $1/month (maybe I should be using my accounts more actively :D).

This is probably a good place to point out then that GuardDuty is a regional service. AWS recommends turning it on across all accounts and regions where there are active workloads running. The combination of SCPs to disable regions not in use and GuardDuty enabled in any regions which are, is an effective combination that balances cost with threat detection that would be difficult to achieve through other means. Turning GuardDuty on for all accounts and in all regions can result in costs which get out of hand in enterprise level usage; typically with 20+ accounts and no region blocking though SCPs. So, I'd highly recommend working with Cloud Engineering teams to leverage SCPs and lock down regions which are not being used. If one doesn't block regions, it would make sense to enable GuardDuty everywhere - the consequence of not doing that could be having a compromised account mining crypto in a region no one looks at until the bill arrives...

## Getting GuardDuty Going
GuardDuty is an incredibly easy service to get started with. Doing so in a multi-account environment used to be a little painful, however, since the tighter integration with AWS Organizations, it's super easy to enable in the organization. GuardDuty works on a management/member model, much like Organizations does. GuardDuty does not require the management account to be the same as the Organization management account though. For this reason, I have delegated one of my AWS accounts as a "security" account and will be using it as the management account through the remainder of this write-up.

  1. Sign-in to the the AWS Org management account and navigate to the GuardDuty console. Much like other AWS services, it will present a pre-activation landing page. Click "Get started"

![GuardDuty Landing Page](/post/aws/securing-a-personal-aws-account/images/aws_gd_enable_1.png)

  2. On the subsequent page, click on "Enable GuardDuty"

![Enable GuardDuty](/post/aws/securing-a-personal-aws-account/images/aws_gd_enable_2.png)

  3. Once GuardDuty is enabled, navigate to the "Settings" page using the left side navigation in the console. There are several things that can be configured here, like delivering findings to S3 if you want to export them to a SIEM, options to suspend or disable the service, etc. I'm not going to change much here (see step 4 for the one change that will be made)

![GuardDuty Settings Page](/post/aws/securing-a-personal-aws-account/images/aws_gd_settings.png)

  4. Because I want to use a different account (my security account) as the GuardDuty management/admin account, I'll provide that AWS account ID to the the GuardDuty Delegated Administrator setting. Clicking the delegate button will then enable GuardDuty in the delegated admin account.

![GuardDuty Delegate Admin](/post/aws/securing-a-personal-aws-account/images/aws_gd_delegate_admin.png)
  
  5. Sign out of the Org management account and in to the security account. Navigate to the GuardDuty console. In the left side navigation, go to "Settings > Accounts" to view the AWS accounts that are part of the AWS Organization (it might take a moment to load them all). The first time on this page, a blue banner across the top will ask about enabling GuardDuty for the Organization. Clicking enable will turn GuardDuty on in all accounts in the Org for the current region and add them to this delegated admin account. It will also cause any new org accounts to auto join when they are created/invited to the org. Accounts can also be managed by selecting the check box next to them and adding using the action dropdown in the top right.

![GuardDuty Multi-Account Configuration](/post/aws/securing-a-personal-aws-account/images/aws_gd_org_add_members.png)

And that's it. GuardDuty is now enabled. Because I have locked down regions using SCPs, I've only enabled GuardDuty in the `us-east-1` region in my accounts. For anyone using a region nearer to them, GuardDuty will need to be enabled in both the region of choice **and** `us-east-1`. There are a number of services that are considered global services (in that one doesn't need to worry about which region the service will deploy in). For the purposes of logging, those services typically are considered in `us-east-` and, as such, it is highly recommended to enable GuardDuty in `us-east-1` regardless of if it will be used or not to ensure visibility for those global services).

## Wrapping Up
And that's it... the end of this series of posts. If you've followed along since part one, a multi-account architecture has been created with some secure baseline configurations and the ability to detect malicious activity in the account. As GuardDuty finds indicators of compromise across EC2 and CloudTrail, findings will be generated and show up in the Findings page. Reading the GuardDuty docs is really the best way to understand the finding types and suggested response processes for when findings are detected. I've included a screen shot below to show one of the finds that generated as I was working on this series of posts and ended up turning CloudTrail on and off.

![GuardDuty Finding](/post/aws/securing-a-personal-aws-account/images/aws_gd_finding_eg.png)

In a future post I'll look at enabling a more pro-active alerting mechanism for when GuardDuty generates findings. I might even look at sending findings to S3 so that I can ingest them in to a SIEM type of solution. It could also be interesting to put together a post testing GuardDuty by carrying out "malicious" activity to force alerts to generate.

I hope this series of posts has been helpful to those interested in starting on an AWS journey of learning. I realize there are probably several dozen post series like this out there (not to mention YouTube videos covering this sort of content). My experience has been that one person's style of explaining isn't always the right style for the pieces to click. Hopefully my style is helpful to someone out there. If you have comments, suggestions, etc. please don't hesitate to leave a comment in the post or reach out in some other way.

[part-1]: https://dariushall.com/post/aws/securing-a-personal-aws-account/secure-multi-account-setup-part-1/ "Part 1 - AWS For Personal Use/Learning: Secure Multi-Account Setup"
[part-2]: https://dariushall.com/post/aws/securing-a-personal-aws-account/iam-personal-accounts-part-2/ "Part 2 - AWS For Personal Use/Learning: Identity and Access Management"
[part-3]: https://dariushall.com/post/aws/securing-a-personal-aws-account/account-level-guardrails-part-3/ "Part 3 - AWS For Personal Use/Learning: Account Level Guardrails"
[part-4]: https://dariushall.com/post/aws/securing-a-personal-aws-account/the-audit-trail-part-4/ "Part 4 - AWS For Personal Use/Learning: The Audit Trail"
[gduty-service]: https://aws.amazon.com/guardduty/ "Amazon GuardDuty Service Page"