---
title: "Configuring the AWS CLI"
date: 2021-03-29T16:24:16-06:00
draft: false
toc: false
images:
tags:
  - aws
  - cli
  - aws cli
  - reference
---

Every time I set up a fresh install of an operating system as a result of a new computer or messing around with different OSes on existing systems, I end up having to set up the AWS CLI from scratch. I have multiple personal AWS accounts to use for learning and running services that I want on a more resilient platform than running them on a server at home. It's always a pain to find the right doc pages for setting up the CLI with easy MFA assume role, so it's time to document that here.

# Setting Up the AWS Credentials File
The first step is configuring the `~/.aws/credentials` file. AWS calls this the 'shared credentials file'. The way I use my accounts, I have set up an AWS Organizations organization. The organization master account is the 'front-door' to my other accounts through a 'master role' that can be assumed in all other accounts (including the org master account). I then have a single IAM user in the org master account which has limited IAM permissions, but which can assume the org master role in my several accounts. As such, the only stanza I have in my shared credentials file is:

    [default]
    aws_access_key_id = AKIAMYACCESSKEY
    aws_secret_access_key = mySeCREtacc3SSk3y+aws

The above stanza is then used for any CLI call made without specifying a CLI profile. As mentioned earlier, the IAM user to which this credential belongs can't do a whole heck of a lot, so some additional configuration is made in the `~/.aws/config` file. This file has several more stanzas in it, one of each account in which I want to be able to assume the master role. While I may not be following best practices here for IAM access, being a one man show with only personal accounts and no production sensitive activity going on, this setup suits my needs for now.

# Setting Up the AWS Config File
The AWS Configuration file provides a means for defining profiles which I can then use with the `--profile` flag when making CLI calls. This file provides a means for defining which role should be used and where to look for the MFA device when needing to issue a command to a specific account. I have MFA required for all assumed role calls using the org master role I have set up. The config file looks like this:

    [default]
    region = us-east-1
    output = yaml

    [profile org-master]
    region = us-east-1
    output = yaml
    role_arn = arn:aws:iam::210987654321:role/role_to_assume
    mfa_serial = arn:aws:iam::210987654321:mfa/iam_user_name
    source_profile = default

    [profile learning]
    region = us-east-1
    output = yaml
    role_arn = arn:aws:iam::123456789012:role/role_to_assume
    mfa_serial = arn:aws:iam::210987654321:mfa/iam_user_name
    source_profile = default

The first stanza is a reference to the default "profile" and credentials set up in the shared credentials file. The second and third stanzas are named profiles, `org-master` and `learning` in this case, which tells the CLI how to access and assume the role required to use the profile. The important bits are `role_arn`, `mfa_serial` and `source_profile`. `role_arn` should be for the role in the account which you want to jump in to. The `mfa_serial` tells the CLI in which account the MFA device is configured and this should match the account specified in the `source_profile` section.

You will notice in the `org-master` profile, that the AWS account ID in the role ARN and MFA device ARN are the same. In this case, it's because I want to assume the privileged role in the same account as the IAM user assuming the role.

In the `learning` profile, the account ID in the role ARN and MFA device ARN are different. This is because the IAM user defined in the `source_profile` (the default profile configured with the access key and secret access key for my IAM user) is to assume the role in the account with the ID specified in the `role_arn`. This all probably sounds terribly confusing. But once it's configured and you've issued `aws sts get-caller-identity` a few times, with and without the `--profile` flag, you will see how this all works.

# Scaling Things Up
On my work laptop, my `~/.aws/config` and `~/.aws/credentials` files look a little different. In the shared credentials file, I have a couple of different profiles configured, beyond just the 'default'. The shared credentials file is largely the same, but with several stanzas for each IAM user with their own access key and secret access key's defined.

The configuration file changes a bit in this case if the IAM users are authorized to assume different roles in different accounts. The only things that really change though in the named profiles are the `mfa_serial` and `source_profile`. Instead of each named profile having the same configuration for these two settings, they would be changed depending on the IAM user required to assume the roles in the various accounts.

# Wrapping Up
Hopefully this makes sense to you, the reader. Mostly this is meant to be a quick write up so that I have it available to me next time I need to set this up.

For what it's worth, here are a handful of links that might come in useful:

- [AWS CLI docs on AWS's docs site](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)
- [AWS CLI Command Line Reference config variables](https://awscli.amazonaws.com/v2/documentation/api/latest/topic/config-vars.html)