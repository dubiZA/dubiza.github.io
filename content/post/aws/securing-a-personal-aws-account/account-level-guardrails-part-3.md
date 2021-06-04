---
title: "Part 3 - AWS For Personal Use/Learning: Account Level Guardrails"
date: 2021-06-01T07:01:09-06:00
draft: false
toc: true
tags:
  - aws
  - reference
  - cloud security
  - aws iam
  - aws scp
  - aws organizations
---
_This is the third post in what is a multi-part series on some suggestions based on AWS Well-Architected Framework best practices focused on setting up an AWS account(s) for personal use and learning. For other parts in the series see:_
  - _[Part 1 - AWS For Personal Use/Learning: Secure Multi-Account Setup][part-1]_
  - _[Part 2 - AWS For Personal Use/Learning: Identity and Access Management][part-2]_
  - _[Part 4 - AWS For Personal Use/Learning: The Audit Trail][part-4]_

So far in this multi-part series, the benefits of multiple AWS accounts has been discussed and AWS Organizations has been configured to enable that approach. At least two accounts exist in the organization (see part 1 for my account architecture which, at present, includes 4 accounts with distinct roles in the AWS Organization) and human access has been enabled through the use of AWS SSO. Least privilege for said human access has been through the use of SSO user groups and permission sets associated with the AWS accounts and SSO users/groups. That is a great baseline, especially for individual, human user based access, however, control can be tightened up even more at an account level.

The AWS Organizations service introduced many ways to enable a streamlined approach to managing and governing a multi-account AWS architecture. Organizations supports two general feature sets to users of the service:
  
  - Consolidated Billing, which is a limited subset of the full AWS Organizations feature set. It provides an easier way to manage, view and receive bills for a multi-account environment
  - All features, which includes the Consolidated Billing functionality and several other enhancements like Service Control Policies, Tagging Policies, and other advanced management functionality

This post, as the title suggests, is focused on applying account level "guardrails" against accounts in the AWS Organization using the Service Control Policies (SCP) feature.

## SCPs: Overview and Enabling
Services in AWS are all the high-level things you can use in an AWS account. EC2, S3, CloudFormation, CloudTrail, SageMaker are some examples of the 250+ services. As the name Service Control Policies suggest, these policies control access to the service.

It might be important to note that they do not grant access to services in an account by themselves. In other words, if there are no IAM identities in an account, applying the default AWS managed SCP `FullAWSAccess` would do nothing. In fact, even if there was an IAM principal, but that principal had no IAM policies attached to it, the SCP would still not take effect.

So, if SCPs don't do anything by themselves, how do they work? They provide a way of controlling the maximum permissions that can be applied to an IAM principal (user or role) by an IAM access policy. I'm not going to go in to detail about how AWS evaluates effective permissions - [the AWS docs have a great explanation of the logic behind policy evaluations][policy-eval] (it turns out that depending on the service, there could be up to 5 different types of policies that determine final effective permissions).

Before moving on, it is really important to point out that SCPs have absolutely no effect on the organization management account. Any SCPs attached to the root organizational unit or directly to the management account will do nothing to limit the access that can be assigned to IAM identities (users or roles) and root user. Access for identities in the management account can only be controlled through IAM policies. This behavior, I believe is intended to prevent locking one's self out of their entire account architecture.

### Enabling SCPs
With AWS Organizations enabled, Service Control Polices can be turned on from within the AWS Organizations Management Console view.

  - In the AWS Org Management Console left side navigation, click "Policies"
  - On the "Policies" page, click the link for "Service Control Policies"

![Enable SCPs](/post/aws/securing-a-personal-aws-account/images/aws_scp_policies_page.png)

  - The top right of the SCP page should show a button that allows it to be enabled if it is not already enabled (again, my accounts has been around for several months now and much of what I'm demonstrating was done by me months ago so I don't have exact deployment/enable screenshots and information. AWS docs are generally good enough to answer questions that might come up)

![Enable SCPs](/post/aws/securing-a-personal-aws-account/images/aws_scp_full_access.png)

## Service Control Policy Strategies
Now that SCPs are enabled, there are a couple of strategies to think about on how to use them. Much like firewalls, for those in the networking world, SCPs (and IAM policies) have an implicit deny if there is no policy statement explicitly allowing a service (or API action for IAM).

The first strategy for SCPs then, would be an allow list model. By default, AWS attaches a managed SCP to the root Organizational Unit (OU) in the AWS Organization. The managed SCP is called `FullAWSAccess`. To use the allow list model, it would be necessary to detach the `FullAWSAccess` policy from the root OU. Doing so would result in that implicit deny taking effect. Any service that needs to be used in any given member account would need to explicitly be allowed through an SCP attached to the OU or account. This can be an effect way to really lock down the account, however, the draw back is it doesn't scale well. If only a handful of services will ever be used, this could be a great strategy.

The second strategy would be a deny list model. Deny listing is the default configuration AWS applies when enabling SCPs by attaching the above mentioned `FullAWSAccess` managed policy - a * on * policy that allows all actions on all services. The deny model can be more difficult to lock down, but scales much better when there is a solid understanding of how AWS is used in an organization. In the personal use scenario for AWS accounts, I'd venture to say this deny model makes the most sense as it gives the freedom to learn how to use services without needing to go and add each service to an allow list. It does allow us to configure some guardrails that can help reduce the hurt if we end up screwing up at some point and leak access keys, or spin up a server we didn't mean to, etc.

## Suggested Guardrails For Personal Use Accounts
Which strategy one ends up using is up to the user/organization. I went with the deny list approach to make things a bit easier on myself. Having said that, I've read enough horror stories of people trying to learn AWS inadvertently racking up thousands of dollars in service charges either through their own mistake or account compromise (arguably also their own mistake).

To mitigate some of the risk of screwing up and account compromise, using SCPs to limit access in some key areas is a great idea. Here I have a few suggestions, one of which will work very well with the next part in the series and using GuardDuty for intelligent threat detection in cases of account compromise.

### Limiting Regions
The first suggested guardrail I'd strongly recommend for a personal use environment (even enterprise use can benefit from this!) is locking down regions that can be used to deploy services. It is much too easy for a new user to inadvertently deploy a bunch of infrastructure to a region they don't typically use or didn't mean to use. People do this all the time and then forget about it because they never use the region again and forget to clean up. This is one of the most common ways personal account users rack up high bills in AWS. Typically, AWS is really nice about waiving bills from PEBKAC issues, but it's much easier to avoid those in the first place.

Another benefit to limiting regions is that it makes it that much harder to miss account compromise. When an AWS account is pwned, attackers will often spin up infrastructure in regions that don't have anything going on so as to fly under the radar as much as possible. By disabling regions that are known to not be used and needed, this can be prevented. Region limiting, in conjunction with the GuardDuty service can enable a rather effective means of rapid detection and response in a case of account (and even compute) compromise.

My recommendations for limiting regions would be to use the [sample SCP][region-lock] provided by AWS in the SCP docs (see below). The policy can be/needs to be tweaked a bit to make it work for you. The policy would work in conjunction with the default `FullAWSAccess` SCP. The action is to `deny` access to all resources where the `aws:RequestedRegion` (see the condition statement) is not an approved region. The policy provides a means of adding exempt principals (IAM roles or users) that should still be able to use all regions. This condition could be removed. Additionally, because there are a number of global services that have their endpoints based in the `us-east-1` region, the policy also includes a `NotAction` statement in the `deny` statement.

      {
          "Version": "2012-10-17",
          "Statement": [
              {
                  "Sid": "DenyAllOutsideEU",
                  "Effect": "Deny",
                  "NotAction": [
                      "a4b:*",
                      "acm:*",
                      "aws-marketplace-management:*",
                      "aws-marketplace:*",
                      "aws-portal:*",
                      "awsbillingconsole:*",
                      "budgets:*",
                      "ce:*",
                      "chime:*",
                      "cloudfront:*",
                      "config:*",
                      "cur:*",
                      "directconnect:*",
                      "ec2:DescribeRegions",
                      "ec2:DescribeTransitGateways",
                      "ec2:DescribeVpnGateways",
                      "fms:*",
                      "globalaccelerator:*",
                      "health:*",
                      "iam:*",
                      "importexport:*",
                      "kms:*",
                      "mobileanalytics:*",
                      "networkmanager:*",
                      "organizations:*",
                      "pricing:*",
                      "route53:*",
                      "route53domains:*",
                      "s3:GetAccountPublic*",
                      "s3:ListAllMyBuckets",
                      "s3:PutAccountPublic*",
                      "shield:*",
                      "sts:*",
                      "support:*",
                      "trustedadvisor:*",
                      "waf-regional:*",
                      "waf:*",
                      "wafv2:*",
                      "wellarchitected:*"
                  ],
                  "Resource": "*",
                  "Condition": {
                      "StringNotEquals": {
                          "aws:RequestedRegion": [
                              "eu-central-1",
                              "eu-west-1"
                          ]
                      },
                      "ArnNotLike": {
                          "aws:PrincipalARN": [
                              "arn:aws:iam::*:role/Role1AllowedToBypassThisSCP",
                              "arn:aws:iam::*:role/Role2AllowedToBypassThisSCP"
                          ]
                      }
                  }
              }
          ]
      }
  
### Limiting EC2 Instance Types
I made the decision in my AWS accounts to limit the type of EC2 instances that can be launched. The intention here was to make sure that I could only use instance types in the free tier of service and prevent mistakenly spinning something up that is bigger and more expensive and then forgetting to terminate the instance. Again, with this statement, it is an explicit `deny` to work with the deny list model suggested above. Any run instance API call to the EC2 service where the specified EC instance type is not `t2.micro` will be blocked.

        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Sid": "RequireMicroInstanceType",
              "Effect": "Deny",
              "Action": "ec2:RunInstances",
              "Resource": [
                "arn:aws:ec2:*:*:instance/*"
              ],
              "Condition": {
                "StringNotEquals": {
                  "ec2:InstanceType": "t2.micro"
                }
              }
            }
          ]
        }

### Other Options for SCPs
I highly recommend viewing the [SCPs examples][example-scp] in the docs. There are a number of other SCPs that can be combined in to a "baseline" SCP that could then be applied to the root OU. I should point out that AWS does not recommend attaching new deny policies to the root OU right off the bat as there could be unintended consequences. I'd definitely agree with that in a working, enterprise production account setup. In this case, where the accounts are likely new and being used only for personal use, it's a bit safer to just go ahead with it. The SCP will not affect the org management account, so in this personal use use case, it's a quicker thing to just go an make a change if there are unintended consequences.

Some suggestions from the example SCPs would be to:

  - Deny IAM identities from making changes to admin roles (in the case where a cross-account role was added when creating new org member accounts)
  - Denying org member accounts the ability to leave the organization
  - Denying or member accounts the ability to disable GuardDuty (part 5 of this series will look at turning GuardDuty on)

Currently, I'm only using the policies to block undesired regions and EC2 instances, however, I will be experimenting with a new baseline SCP which I'll included here with a later update when I have it working. At this point, I think we can call this post done though. AWS has been configured with some great initial baseline security measures. The addition of SCPs will add some useful guardrails to prevent member accounts from being used in ways that are not desired. Next steps are to set up an audit log of all the API actions taking place across accounts in the AWS Organization. Stay tuned for part 4!


[part-1]: https://dariushall.com/post/aws/securing-a-personal-aws-account/secure-multi-account-setup-part-1/ "Part 1 - AWS For Personal Use/Learning: Secure Multi-Account Setup"
[part-2]: https://dariushall.com/post/aws/securing-a-personal-aws-account/iam-personal-accounts-part-2/ "Part 2 - AWS For Personal Use/Learning: Identity and Access Management"
[part-4]: https://dariushall.com/post/aws/securing-a-personal-aws-account/the-audit-trail-part-4/ "Part 4 - AWS For Personal Use/Learning: The Audit Trail"
[policy-eval]: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html "AWS Policy Evaluation Logic"
[region-lock]: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps_examples.html#examples_general "Example SCPs - Region"