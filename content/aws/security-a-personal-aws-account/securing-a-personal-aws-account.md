---
title: "Securing a Personal AWS Account"
date: 2021-05-05T06:49:25-06:00
draft: true
toc: false
images:
tags:
  - aws
  - cli
  - aws cli
  - reference
  - cloud security
  - iam
---

The best way to learn is to do. You can read all you want about how to code in Python, create and run Docker containers, build a bookshelf or working with AWS; until you dig in and actually start experimenting, it's not going to become a persistent skill. AWS is an incredible platform that is growing and innovating as a Cloud Services Provider in amazing ways. There are now over 250 services available through AWS, and that list grows bigger every year.

AWS makes learning and experimenting on their platform easy for anyone. All you need is a phone number, email address and credit card. AWS has a [support article][create-account] that walks through the process, and, given that I've already got my account set up, I'm not going to cover that in this post.

This post is aimed at securing an AWS account (more through the lense of personal use than enterprise setup) and attempts to do so following the [AWS Well-Architected Framework][aws-waf](AWS WAF) with focus on [Security Pillar][security-pillar] best practices.

The Security Pillar of the AWS WAF talks about five main areas of security in the cloud:

  1. Identity and Access Management (IAM)
  2. Detection
  3. Infrastructure Protection
  4. Data Protection
  5. Incident Response

This post addresses several of those areas as we work to establish an initial baseline or foundational security controls that any new AWS account should be configured with. These controls apply to an AWS account whether it will be used for personal learning or it is being set up for company use.

While this post is going to look at setting up an account more from the lens of personal use, in my case, I try to reflect the account "architecture" as close as possible to what one might see in enterprise use. This means that I use a multi-account setup, even for personal use. Some time ago, AWS introduced the AWS Organizations service as a means to facilitate a multi-account approach to using AWS. AWS accounts can be considered a [hard boundary, zero trust container][aws-orgs] for resources. The recommendation is to use separate, purpose built accounts based on function, common controls or compliance requirements.

With that in mind, lets jump in to setting up AWS accounts for personal use with a secure baseline, following best practices from the Security Pillar of thw AWS Well-Architected Framework as closely as possible given the personal use use-case.

_I should point out that, because I have already had my AWS accounts running for several months, this write-up is not going to be a complete step-by-step, walking through account creation for the initial account, to the initial setup of AWS Organizations. Some of those gaps can be filled by looking at AWS's documentation._


# Account Architecture
As mentioned above, AWS recommends taking a multi-account approach to using AWS. AWS Introduced AWS Organizations some time ago to facilitate easier management of a multi-account architecture. Many of AWS's services integrate with Organizations for easier deployment across multiple accounts (services like GuardDuty, AWS SSO, CloudTrail, etc).

I currently have four active AWS accounts:

  - Organizations management account (I should point out, given the screenshots that will follow, AWS appears to have renamed some AWS Organizations terminology. The organizational root account memberships used to be referred to as master/member. The terminology is now management/member account in their docs. I had named my accounts using the previous terminology before the change.)
  - Security account
  - Shared services
  - Learning




# Securing the Root User


# Identity and Access Management


# Account Level Guard Rails


# The Audit Trail


# Intelligent Threat Detection


[create-account]: https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/ "Create and Activate an AWS Account"
[aws-waf]: https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html "AWS WAF Home Page"
[security-pillar]: https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html "AWS WAF Security Pillar Home Page"
[aws-org]: https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/aws-account-management-and-separation.html "AWS Multi-Account Management and Separation"