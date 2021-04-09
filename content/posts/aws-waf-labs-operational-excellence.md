---
title: "AWS WAF Labs: Operational Excellence"
date: 2021-04-07T07:36:28-06:00
draft: false
toc: false
images:
tags:
  - aws
  - aws labs
  - well architected
  - operational excellence
---

# AWS Well-Architected Framework
A few month ago, I stumbled across some AWS provided resources in the form of labs that one can work through to better understand some of AWS recommended best practices. I don't fully recall all the links I ended up finding (this is why the blog is being written - I know, browser bookmarks would also have been a good idea...), but at least one of the places with some good labs to work through is [https://wellarchitectedlabs.com](https://wellarchitectedlabs.com "AWS Well Architected Labs").

So, this is Part 1 of my experience going through these labs. If you are not acquainted with the Well Architected Framework (WAF), you can read more about it in-depth at [AWS's website](https://aws.amazon.com/architecture/well-architected/?wa-lens-whitepapers.sort-by=item.additionalFields.sortDate&wa-lens-whitepapers.sort-order=desc "AWS Well-Architected"). The nutshell version is the WAF is a framework that cloud architects can use to build robust, resilient, secure, performant and scalable cloud based infrastructure and application in the AWS ecosystem. It is comprised of 5 "pillars":

  1. Operational Excellence
  2. Security
  3. Reliability
  4. Performance
  5. Cost Optimization

The labs in the series cover each of the 5 pillars. This initial post will go over some of the things that I learned about while working through the Operational Excellence pillar.

# CloudFormation
One thing to point out is that the first lab on Operational Excellence makes use of the [CloudFormation service](https://aws.amazon.com/cloudformation/ "CloudFormation Service Page"). If you are not familiar with CloudFormation (CF), it's AWS's declarative Infrastructure as Code (IaC) solution for many things AWS. I say many things and not all things AWS because my experience - albeit limit experience - with it is that CloudFormation is often slow to add support for new services and new features to existing services.

## Benefits of CloudFormation in Personal AWS Accounts
CloudFormation (or any IaC tool) is still a very useful service when deploying infrastructure within AWS as it makes things easily repeatable and scales well amongst other benefits. Possibly the biggest benefit to someone running things in their own AWS account for experimentation is that it provides a single place to deploy a whole host of services, infrastructure and more that could otherwise be difficult to keep track of when it comes time to cleaning up.

If you're running your own personal AWS account to learn new things, I'd highly recommend becoming familiar with CloudFormation (or another IaC tool) when deploying infrastructure that could end up costing you money. Once you're done with the infrastructure, deleting the CF stack cleans things up quickly and easily and, ideally, saves you from unexpected bills due to forgotten resources.

## FYI On Uploading CF Templates in the AWS Console
Something I wanted to point out about CloudFormation is that when you deploy CF templates using the AWS console by uploading a template you have already created/downloaded from somewhere, the CF service will attempt to create an S3 bucket in your account and save the template file there.

The S3 bucket it creates will have a name similar to `cf-templates-83lzhmd7bws4-us-east-1` (the random bit of text between `cf-templates` and the region are there to ensure uniqueness in the S3 bucket global namespace). If you end up using the console to upload the same template again at a later time, it will save a new copy of the template to S3. It seems any uploads from the console have a random string added as a prefix to the original filename. To get around repeat uploads of the same template, you can either use the S3 URL when creating a duplicate stack from an existing template, or you can use the AWS CLI when creating stacks.

# Warp Up
While I realize this post hardly touched on the labs for the Operations Excellence pillar, to avoid too long of a post, I'll end this one here. AWS provides some powerful tools for provisioning and managing infrastructure and services. The Operational Excellence Pillar of the Well-Architected Framework aims to help organizations deliver business value by doing things like automation, defining standards to manage operations etc. CloudFormation certainly touches on some of these key topics.