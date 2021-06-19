---
title: "Part 2 - AWS For Personal Use/Learning: Identity and Access Management"
date: 2021-05-28T21:26:09-06:00
draft: false
toc: false
tags:
  - aws
  - reference
  - cloud security
  - aws iam
  - aws sso
  - aws organizations
---
_This is the second post in what is a multi-part series on some suggestions based on AWS Well-Architected Framework best practices focused on setting up an AWS account(s) for personal use and learning. For other parts in the series see:_
  - _[Part 1 - AWS For Personal Use/Learning: Secure Multi-Account Setup][part-1]_
  - _[Part 3 - AWS For Personal Use/Learning: Account Level Guardrails][part-3]_
  - _[Part 4 - AWS For Personal Use/Learning: The Audit Trail][part-4]_
  - _[Part 5 - AWS For Personal Use/Learning: Intelligent Threat Detection][part-5]_

With everything locked down in the management account and potentially no AWS Organizations cross account role created, how the heck does the account get used without using the root account!? Well, there are a couple of ways this could be approached. AWS recommends using a central identity store to efficiently manage users. This makes sense, especially in large organizations where there is typically more churn in the employee base. Additionally, there are generally two types of identities that might be required in AWS:

  1. **Humans**: Think admins, developers, operators, etc. This is probably one of the most scary types of identities because they can think and often break things while actively looking for ways to make life easier for themselves &#128540;
  2. **Machines**: The applications and workloads running in and dependant on the cloud resources in the various accounts. These are the less scary type of principal because they shut up, do what they're told and get in to far less trouble once they start working

This write up is going to address the human kind of identity and leave the machines alone for now. In my mind, there are two ways to implement the best practice of using a central identity store.

  1. Create IAM roles in the various AWS accounts in the AWS Organization that can be assumed by principals in the org management account. The roles are scoped for least privilege. IAM users are then created in the org management account with only the rights to manage their own IAM properties, like password changes and MFA tokens, and with the ability to assume roles in other accounts. Their ability to assume roles would be limited to only those they need for their job function. Essentially, the management account is the central identity provider (IdP) - when a user leaves the company, there is one place to remove the user and access to all other AWS accounts is terminated with that removal
  2. Use a SAML 2.0 based IdP solution that can integrate with AWS (like Okta, PingIdentity, etc). The great thing here is that AWS provides it's own IdP solution in the form of AWS SSO (in fact, from what I can tell, even using external IdPs would require the use of AWS SSO). The benefit here is AWS SSO integrates tightly with AWS Organizations. Enabling AWS SSO in the org management account will make it a breeze to get working with all other accounts in the organization

Now, I must be honest here, AWS SSO is a new service to me. I started out using option 1 with roles that get assumed by an IAM user in the org management account. But, AWS SSO just makes more sense. Given the updates to the [AWS CLI with the v2 release][aws-cli2] that now supports AWS SSO, and the ease of setup for multi-account access and implementing different types of MFA, it's silly to not use it.

To get started, in the AWS Organizations management account (remember to sign in with the root user for the org management account if you are continuing this from part 1 and are not currently signed in. No IAM users were created in part 1, so the root user is the only option for signing in at this point):

  - Navigate to the AWS SSO service
  - AWS SSO is a regional service, so make sure the desired region is selected (us-east-1 for me)
  - Click the "Enable AWS SSO" button on the landing page

![Enabling SSO](/post/aws/securing-a-personal-aws-account/images/enable_sso.png)

  - I'd recommend some additional configuration adjustments to AWS SSO next
  - Click on "Settings" in the left-hand navigation
  - Customize the "User portal" by changing the URL to something a little more meaningful
  - Under the "Mutli-factor authentication" heading, click "Configure"

![AWS SSO Settings](/post/aws/securing-a-personal-aws-account/images/aws_sso_mfa_pre_config.png)

  - Under the "Users should be prompted for MFA" make sure the "Only when their sign-in context changes (context-aware)" radio is selected. While I might be a security guy, I also believe that security should be as unobtrusive to the user experience as possible. Using this context aware MFA configuration will reduce some of the friction typically associated with MFA and short-lived access sessions
  - Select whether only hardware backed MFA authenticator devices should be allowed or authenticator apps as well (while AWS CLI v2 does support the use of hardware tokens that don't generate TOTP codes, it could be wise to still allow authenticator apps to make sure all bases are covered. When using the CLI, if users aren't using v2, they will probably run in to usability issues if they are unable to provide an MFA TOTP code to the CLI)
  - Under the "If a user does not yet have a registered MFA device" heading, select the "Require them to register an MFA device at sign in" radio. This will give users the ability to manage their own MFA device, and will ensure that if none is configured at first sign in, that they configure one before they are able to access anything else

![AWS SSO MFA Configuration](/post/aws/securing-a-personal-aws-account/images/aws_sso_mfa_settings.png)

  - Implementing role-based access control (RBAC) can be accomplished by creating groups in AWS SSO, so in the left navigation click "Groups"
  - Click the big blue "Create Group" button
  - Fill in the details (I created an "admin" group here)
  - Click create

![Create SSO Group](/post/aws/securing-a-personal-aws-account/images/aws_sso_groups.png)

  - Create a new AWS SSO user by clicking "Users" in the left side navigation
  - Click the big blue "Add User" button
  - On the next screen, fill in the details and create

![Create SSO User](/post/aws/securing-a-personal-aws-account/images/aws_sso_users.png)

  - To give AWS account level access to an SSO user, click the "AWS accounts" link in the left-hand navigation
  - On the "Permission sets" tab, click the blue "Create permission set" button

![Create SSO Account Level Permission Set](/post/aws/securing-a-personal-aws-account/images/aws_accounts_permission_sets.png)

  - For simplicity in this post, use one of the existing job function policies when prompted

![Create Pre-Configured Policy](/post/aws/securing-a-personal-aws-account/images/aws_sso_permission_set_precanned.png)

  - To get a good balance between account access and least privilege, the PowerUserAccess policy should work well. Given this writeup is focused on creating a set of accounts for personal use, PowerUserAccess will grant access to just about every service that AdministratorAccess does, but does not include access to most IAM features. Users assigned this permission set won't be able to create, read, update or delete any IAM users, groups, etc.
  - Feel free to add tags on the next screen
  - Review the permission set configuration and create

![Select Preexisting Policy](/post/aws/securing-a-personal-aws-account/images/aws_sso_permission_set_policy.png)

  - With the permission set created, click on the "AWS organization" tab
  - Check the boxes next to the AWS accounts that the new SSO user should have access to
  - Click the blue "Assign users" button

![Assign AWS Account Access to User](/post/aws/securing-a-personal-aws-account/images/aws_sso_account_user_assignment.png)

  - To make adminstration easier, rather than assigning individual users, make sure to assign groups. On the "Assign Users" screen, click the "Groups" tab
  - Select the SSO group created earlier, where the SSO user was already added to that group

![Assign SSO Group to Account](/post/aws/securing-a-personal-aws-account/images/aws_sso_assign_group.png)

  - On the next screen, select the permission set created previously. This will associated that permission set with the SSO user group for the accounts that were selected

With that, the SSO user should have everything needed to sign-in and get started with using the AWS accounts that were assigned. Users will be able to access the SSO portal using the user portal URL customized earlier. This can be tested by:

  - Opening an incognito or private browsing window or using a different browser from the one currently signed in to AWS
  - Navigating to the user portal URL
  - Entering username and password (at user creation, an email would have been sent to the new user. If not already done, follow the link in the email to create a password for the user account. Right clicking the link in the email and opening in a private browsing window would be best or copying the link and using a different browser)

![SSO User Sign-In](/post/aws/securing-a-personal-aws-account/images/aws_sso_signin_page.png)
  
  - On first sign-in the user will be prompted to enroll an MFA device
  - Select the desired type of MFA device (the prompt will give the option of authenticator app like Authy, security key like a YubiKey and built-in authenticator when using a compatible device with a browser that has support). I'd recommend the security key or authenticator app to avoid compatibility issues with the built-in authenticator (although multiple options could be enabled later to avoid the compatibility issue)

![Add MFA device](/post/aws/securing-a-personal-aws-account/images/aws_sso_mfa_user_config.png)

And that's it. The SSO user should have a tile of sorts that says "AWS Account (number of accounts they have access to)". Clicking on the tile will expand a list of the accounts they have access to. Clicking on one of those will drop down a sub-menu of sorts with a link to the AWS management console for browser-based access to the AWS account or, clicking the link that says "Command line or programmatic access" will present another screen with an AWS access key, secret access key and session token as well as directions for how to use those depending on the method of access (a *nix based shell or Windows PowerShell).

![AWS SSO Post Sign In Screen](/post/aws/securing-a-personal-aws-account/images/aws_sso_post-sign-in.png)

There we have it. Any AWS accounts associated with the user created in this guide will now be able to access most of the services in AWS with a pretty high level of access. For now, a user with elevated access will be needed to complete tasks in the remainder of this series. Stay tuned for part 3 where AWS account level guardrails are discussed and implemented.

**Update 5/29/2021**: Using the `PowerUserAccess` permission set will prevent users from accessing AWS Organizations in any meaningful way. Keep this in mind given part 3 of the series will be working with SCPs. Consider creating an SSO user with more permissive access but limiting use of this user as much as possible (only use it when needing to perform IAM, AWS SSO and AWS Organization actions for example).

[part-1]: https://dariushall.com/post/aws/securing-a-personal-aws-account/secure-multi-account-setup-part-1/ "Part 1 - AWS For Personal Use/Learning: Secure Multi-Account Setup"
[part-3]: https://dariushall.com/post/aws/securing-a-personal-aws-account/account-level-guardrails-part-3/ "Part 3 - AWS For Personal Use/Learning: Account Level Guardrails"
[part-4]: https://dariushall.com/post/aws/securing-a-personal-aws-account/the-audit-trail-part-4/ "Part 4 - AWS For Personal Use/Learning: The Audit Trail"
[part-5]: https://dariushall.com/post/aws/securing-a-personal-aws-account/intelligent-threat-detection-part-5/ "Part 5 - AWS For Personal Use/Learning: Intelligent Threat Detection"
[aws-cli2]: https://aws.amazon.com/blogs/developer/aws-cli-v2-is-now-generally-available/ "AWS CLI v2 release notes"