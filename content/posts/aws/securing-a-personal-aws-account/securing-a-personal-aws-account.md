---
title: "Securing a Personal AWS Account Set Up"
date: 2021-05-05T06:49:25-06:00
draft: true
toc: false
images:
tags:
  - aws
  - reference
  - cloud security
---

The best way to learn is to do. You can read all you want about how to code in Python, create and run Docker containers, build a bookshelf or work with AWS; until you dig in and actually start experimenting, it's not going to become a persistent skill. AWS is an incredible platform that is growing and innovating as a Cloud Services Provider in amazing ways. There are over 250 services available through AWS, and that list grows bigger every year.

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

_I should point out that, because I have already had my AWS accounts running for several months, this write-up is not going to be a complete step-by-step, walking through account creation for the initial account, to the initial setup of AWS Organizations. As mentioned above, those gaps can be filled by looking at AWS's documentation._

# Account Architecture
As mentioned above, AWS recommends taking a multi-account approach to using AWS. As such, AWS Organizations was introduced some time ago to facilitate easier management of a multi-account architecture. Many of AWS's services integrate with Organizations for easier deployment across multiple accounts (services like GuardDuty, AWS SSO, CloudTrail, etc).

I currently have four active AWS accounts:

  - Organizations Management (I should point out, given the screenshots that will follow, AWS appears to have renamed some AWS Organizations terminology. The organizational root account memberships used to be referred to as master/member. The terminology is now management/member account in their docs. I had named my accounts using the previous terminology, before the change.)
  - Security
  - Shared Services
  - Learning

![Account Architecture](/posts/aws/securing-a-personal-aws-account/images/account_architecture.png)

## Overview of My Account Roles
The org management account is used for almost nothing. It's main purpose is to be the gatekeeper and facilitator of AWS Organizations and the security and governance tools that are applied to the rest of the accounts in the organization. This includes thinks like enabling an org-wide CloudTrail log trail, Service Control Policies, Tagging Policies and being the "identity" account for AWS SSO.

No workloads are executed from this account. No compute, storage, networking or any other services are used for running applications, learning new things (unless they are AWS Organizations related). In my org management account, there are no IAM roles or IAM users.

The intention of the security account is to be the account that runs security tooling. Services like GuardDuty, SecurityHub, Firewall Manager, etc. would be managed from this account. Many of the AWS security services integrate well with AWS Organizations. These security services also work in a management/member model, much like the Organizations service. The security account will be used as the management account for such services.

The shared services account is one that I have created, but not yet utilized for anything. I see this account as being a place to run services and solutions that might apply to all accounts but doesn't necessarily have to. So, things like deploying Infrastructure as Code (CloudFormation/Terraform) to spin up the infrastructure components I might want in other accounts. To me it makes sense to manage all this from a central account, rather than in each account. Using cross account roles and features in CloudFormation like StackSets can facilitate having a single place for these "shared services".

The learning account is what I have for learning new cloud things. The intention here is to separate out the account where the bulk of my learning will take place so that if I inadvertently spin up a bunch of stuff that I lose track of and start getting billed for in surprising ways, I can always blow this learning account away and start over, without affecting the rest of my account architecture.

There are some accounts that I do not yet have, but would like to add soon. One of those would be a centralized logging account where all CloudTrail, GuardDuty, and any other important log that might need longer term storage can go. This account would be locked down and hardened as much as possible to protect the integrity of the logs. I might also look at adding accounts to simulate production and development accounts, accounts that meet other compliance requirements like HIPPA, PCI, etc. But for now, I'm running with the four accounts listed above. As I continue to learn and understand more about AWS and best practices, things will develop and change.

## Adding Accounts
As mentioned above, my accounts have been running for a while, so this does not aim to show how to create the initial management account, nor does it show how to enable AWS Organizations. Following AWS's documentation to accomplish those two steps would be best.

Once the initial management account is created and Organizations enabled, creating a new account within the organization is pretty simple. One can also invite existing accounts to join the organization. From the AWS management console:
  - Click the dropdown in the top right (usually shows the account name/role/username of the currently logged in identity), next to the region and support dropdowns
  - Click My Organization
  - Click the orange "Add an AWS account" button

![Add account to organization](/posts/aws/securing-a-personal-aws-account/images/organizations.png)

On the add account screen:

  - Select "create an AWS account"
  - Give the account a name (I'd suggest establishing some kind of naming convention)
  - Provide an email address (for personal accounts, using a personal email address can be tricky. There are a few options, of which the easiest is probably using aliases. If you use Gmail and your address is myaddress@gmail.com, you could use myaddress+aws1@gmail.com, myaddress+aws2, +aws3, etc.)
  - Provide an IAM role name. AWS will create this role in the new account as part of the provisioning process. This role can be assumed from the org management account to perform any desired tasks. Given that the new account will not have an active root user or any IAM principals, this is one way to access the account without having to jump through hoops. I believe it is optional and, if AWS SSO is configured from the org management account, not necessary

![Create organization account](/posts/aws/securing-a-personal-aws-account/images/create_account_org.png)

# Securing the Root User
With AWS Organizations enabled and a new account created, next steps would be to lock down the organization management account and root user. But first, what is the root user?

Every AWS account has a root user. This user, much like the root user in Linux, has completely unrestricted access to everything in the AWS account. Even if an IAM user is granted the most permissive policy possible within an AWS, there are still certain account operations that would require the root user to be the signed in principal. There are no IAM level policies that can be applied to the root user to explicitly deny access to services. Only AWS Organizations Service Control Policies can limit a root user (with some caveats). AWS lists some tasks that [only a root user can execute][only-root].

If the account root user is compromised, it can be extremely difficult to recover the account, and is something that would require AWS intervention to accomplish. For this reason, once the initial account setup and security hardening is complete **avoid using root**! AWS best practice is to make sure the root user has no access keys, that a strong, complex password is used and that MFA is enabled. Let's take a look at how to do that and some other account setup that is useful.

Initially, only the root user has access to account billing information. To make it so IAM principles can access billing information, that feature needs to be enabled in account settings. On the same screen the IAM access to billing can be enabled, there are a few other configurations that would be prudent to validate.

  - Click the dropdown in the top right (usually shows the account name/role/username of the currently logged in identity), next to the region and support dropdowns
  - Click My Account
  - Ensure the account security questions are configure, in the event AWS Support is required and they ask for validating questions. Make sure the answers provided are remembered
  - Under the "IAM User and Role Access to Billing Information" heading, enable access there (my account this was already done prior to taking screen shots)

![Enable IAM user and role billing access](/posts/aws/securing-a-personal-aws-account/images/billing_security_questions.png)

  With those account settings made and validated, locking down the root user is next.

  - Click the dropdown in the top right (usually shows the account name/role/username of the currently logged in identity), next to the region and support dropdowns
  - Click "My security Credentials"
  - Under the "Multi-factor authentication (MFA)" heading, enroll an MFA token of your choice (there are some options here. Root user MFA choices include a virtual MFA device like Authy or Google Authenticator, U2F compatible security key like YubiKeys and hardware MFA devices that AWS support. I use a U2F key for the root user as I don't perform any operations with the root user that would require the CLI and support for an MFA code. [See AWS docs for more details on options][mfa-options])
  - Under the "Access keys (access key ID and secret access key)" heading, make sure that the root user has no associated keys. Just don't ever justify having access keys for the root user. It is too easy to leak those and have your day ruined

![Root user security](/posts/aws/securing-a-personal-aws-account/images/root-MFA.png)

And with that, the account has a reasonably good level of protection. To recap what has been done so far:
  
  - An AWS Org management account has been established
  - A member account(s) has/have been created
    - Optionally, a management account role has been created in any member accounts (not necessarily necessary)
  - Billing access has been enabled for IAM principals
  - MFA has been turned on for the root user
  - Root user access keys have been deleted if they existed
  - No IAM users have been created in the root account

Remember, the AWS Organization management account is not intended to be used for running workloads. This account should be locked down, without IAM users and roles that could get the account compromised. The Org management account can be considered as the weakest link in the multi-account architecture because some of the additional protection that can be added to member accounts do not work on the management account. So, keep it secret, keep it safe!

# Identity and Access Management
With everything locked down in this management account and potentially no AWS Organizations cross account role created, how the heck does the account get used without using the root account!? Well, there are a couple of ways this could be approached. AWS recommends using a central identity store to efficiently manage users. This makes sense, especially in large organizations where there typically more churn in the employee base. Additionally, there are generally two types of identities that might be required in AWS:

  1. **Humans**: Think admins, developers, operators, etc. This is probably one of the most scary types of principals because they can think and often break things while actively looking for ways to make life easier for themselves &#128540;
  2. **Machines**: The applications and workloads running in and dependant on the cloud resources in the various accounts. These are the less scary type of principal because they shut up, do what they're told and get in to far less trouble once they start working

This write up is going to address the human kind of identity and leave the machines alone for now. In my mind, there are two ways to implement the best practice of using a central identity store.

  1. Create IAM roles in the various AWS accounts in the AWS Organization that can be assumed by principals in the org management account. The roles are scoped for least privilege. IAM users are then created in the org management account with only the rights to manage their own IAM properties, like password changes and MFA tokens, and with the ability to assume roles in other accounts. Their ability to assume roles would be limited to only those they need for their job function. Essentially, the management account is the central identity provider (IdP) - when a user leaves the company, there is one place to remove the user and access to all other AWS accounts is terminated with that removal
  2. Use a SAML 2.0 based IdP solution that can integrate with AWS (like Okta, PingIdentity, etc). The great thing here is that AWS provides it's own IdP solution in the form of AWS SSO (in fact, from what I can tell, even using external IdPs would require the use of AWS SSO). The benefit here is AWS SSO integrates tightly with AWS Organizations. Enabling AWS SSO in the org management account will make it a breeze to get working with all other accounts in the organization

Now, I must be honest here, AWS SSO is a new service to me. I started out using option 1 with roles that get assumed by an IAM user in the org management account. But, AWS SSO just makes more sense. Given the updates to the [AWS CLI with the v2 release][aws-cli2] that now supports AWS SSO, and the ease of setup for multi-account access and implementing different types of MFA, it's silly to not use it.

To get started, in the AWS Organizations management account:

  - Navigate to the AWS SSO service
  - AWS SSO is a regional service, so make sure the desired region is selected (us-east-1 for me)
  - Click the "Enable AWS SSO" button on the landing page

![Enabling SSO](/posts/aws/securing-a-personal-aws-account/images/enable_sso.png)

  - I'd recommend some additional configuration adjustments to AWS SSO next
  - Click on "Settings" in the left-hand navigation
  - Customize the "User portal" by changing the URL to something a little more meaningful
  - Under the "Mutli-factor authentication" heading, click "Configure"

![AWS SSO Settings](/posts/aws/securing-a-personal-aws-account/images/aws_sso_mfa_pre_config.png)

  - Under the "Users should be prompted for MFA" make sure the "Only when their sign-in context changes (context-aware)" radio is selected. While I might be a security guy, I also believe that security should be as unobtrusive to the user experience as possible. Using this context aware MFA configuration will reduce some of the friction typically associated with MFA and short-lived access session
  - Select whether only hardware backed MFA authenticator devices should be allowed or authenticator apps as well (while AWS CLI v2 does support the user of hardware tokens that don't generate TOTP codes, it could be wise to still allow authenticator apps to make sure all bases are covered. When using the CLI, if users aren't using v2, they will probably run in to usability issues if they are unable to provide an MFA TOTP code to the CLI)
  - Under the "If a user does not yet have a registered MFA device" heading, select the "Require them to register an MFA device at sign in" radio. This will give users the ability to manage their own MFA device, and will ensure that if none is configured at first sign in, that they configure one before they are able to access anything else

![AWS SSO MFA Configuration](/posts/aws/securing-a-personal-aws-account/images/aws_sso_mfa_settings.png)

  - Implementing role-based access control (RBAC) can be accomplished by creating groups in AWS SSO, so in the left navigation click "Groups"
  - Click the big blue "Create Group" button
  - Fill in the details (I created an "admin" group here)
  - Click create

![Create SSO Group](/posts/aws/securing-a-personal-aws-account/images/aws_sso_groups.png)

  - Create a new AWS SSO user by clicking "Users" in the left side navigation
  - Click the big blue "Add User" button
  - On the next screen, fill in the details and create

![Create SSO User](/posts/aws/securing-a-personal-aws-account/images/aws_sso_users.png)

  - To give AWS account level access to an SSO user, click the "AWS accounts" link in the left-hand navigation
  - On the "Permission sets" tab, click the blue "Create permission set" button

![Create SSO Account Level Permission Set](/posts/aws/securing-a-personal-aws-account/images/aws_accounts_permission_sets.png)

  - For simplicity in this post, use one of the existing job function policies when prompted

![Create Pre-Configured Policy](/posts/aws/securing-a-personal-aws-account/images/aws_sso_permission_set_precanned.png)

  - To get a good balance between account access and least privilege, the PowerUserAccess policy should work well. Given this writeup is focused on creating an set of accounts for personal use, PowerUserAccess will grant access to just about every service that AdministratorAccess does, but does not include access to most IAM features. Users assigned this permission set won't be able to create, read, update or delete any IAM users, groups, etc.
  - Feel free to add tags on the next screen
  - Review the permission set configuration and create

![Select Preexisting Policy](/posts/aws/securing-a-personal-aws-account/images/aws_sso_permission_set_policy.png)

  - With the permission set created, click on the "AWS organization" tab
  - Check the boxes next to the AWS accounts that the new SSO user should have access to
  - Click the blue "Assign users" button

![Assign AWS Account Access to User](/posts/aws/securing-a-personal-aws-account/images/aws_sso_account_user_assignment.png)

  - To make adminstration easier, rather than assigning individual users, make sure to assign groups. On the "Assign Users" screen, click the "Groups" tab
  - Select the SSO group created earlier, where the SSO user was already added to that group

![Assign SSO Group to Account](/posts/aws/securing-a-personal-aws-account/images/aws_sso_assign_group.png)

  - On the next screen, select the permission set created previously. This will associated that permission set with the SSO user group for the accounts that were selected

With that, the SSO user should have everything needed to sign-in and get started with using the AWS accounts that were assigned. Users will be able to access the SSO portal using the user portal URL customized earlier. This can be tested by:

  - Opening an incognito or private browsing window or using a different browser from the one currently signed in to AWS
  - Navigating to the user portal URL
  - Entering username and password (at user creation, an email would have been sent to the new user. If not already done, follow the link in the email to create a password for the user account. Right clicking the link in the email and opening in a private browsing window would be best or copying the link and using a different browser)

![SSO User Sign-In](/posts/aws/securing-a-personal-aws-account/images/aws_sso_signin_page.png)
  
  - On first sign-in the user will be prompted to enroll an MFA device
  - Select the desired type of MFA device (the prompt will give the option of authenticator app like Authy, security key like a YubiKey and built-in authenticator when using a compatible device with a browser that has support). I'd recommend the security key or authenticator app to avoid compatibility issues with the built-in authenticator (although multiple options could be enabled later to avoid the compatibility issue)

![Add MFA device](/posts/aws/securing-a-personal-aws-account/images/aws_sso_mfa_user_config.png)

And that's it. The SSO user should have a tile of sorts that says AWS Account (number of accounts they have access to). Clicking on the tile will expand a list of the accounts they have access to. Clicking on one of those will drop down a sub-menu of sorts with a link to the AWS management console for browser-based access to the AWS account or. Clicking the link that says "Command line or programmatic access" will present another screen with an AWS access key, secret access key and session token as well as directions for how to use those depending on the method of access (a *nix based shell or Windows PowerShell).

![AWS SSO Post Sign In Screen](/posts/aws/securing-a-personal-aws-account/images/aws_sso_post-sign-in.png)

# Account Level Guardrails
As AWS encouraged a multi-account strategy and introduced AWS Organizations, one of the very useful features added to the AWS Organizations service was the ability to add account level guardrails through the user of Service Control Policies (SCP). It would be worth point out at this point that Organizations can be used in one of two ways:

  - Just consolidated billing
  - Full featured which gives access to SCPs, tagging policies, integrations with Organization compatible services, etc.



# The Audit Trail


# Intelligent Threat Detection


[create-account]: https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/ "Create and Activate an AWS Account"
[aws-waf]: https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html "AWS WAF Home Page"
[security-pillar]: https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html "AWS WAF Security Pillar Home Page"
[aws-org]: https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/aws-account-management-and-separation.html "AWS Multi-Account Management and Separation"
[only-root]: https://docs.aws.amazon.com/general/latest/gr/root-vs-iam.html#aws_tasks-that-require-root "Tasks requiring root"
[mfa-options]: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_mfa.html "MFA options for root user"
[aws-cli2]: https://aws.amazon.com/blogs/developer/aws-cli-v2-is-now-generally-available/ "AWS CLI v2 release notes"