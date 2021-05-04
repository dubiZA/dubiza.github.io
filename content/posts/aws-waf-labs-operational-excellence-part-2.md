---
title: "AWS WAF Labs - Part 2: Operational Excellence"
date: 2021-04-16T06:32:16-06:00
draft: true
toc: false
images:
tags:
  - aws
  - aws labs
  - well architected
  - operational excellence
---

This is part 2 of a multi-part series of posts as I progress through the AWS WAF Labs available [here](https://wellarchitectedlabs.com "AWS Well-Architected Labs").

The AWS Well-Architected Framework (WAF) provides a prescriptive set of guiding principles that solutions architects, cloud engineers, developers, etc. can use to implement what AWS recommends as best practice for operating workloads in the AWS Cloud. The AWS WAF is broken down in to five pillars:

  1. [Operational Excellence](https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/welcome.html "Operational Excellence")
  2. Security
  3. Reliability
  4. Performance Efficiency
  5. Cost Optimization

The Operational Excellence pillar is the focus of this post. Operational Excellence includes five design principles:

  - Perform operations as code
  - Make frequent, small, reversible changes
  - Refine operations procedures frequently
  - Anticipate failure
  - Learn from all operational failures

The AWS WAF Labs, Operational Excellence pillar lab aims to address several of these design principles by introducing AWS services like CloudFormation, tagging and other tools.

# Infrastructure as Code
As I have gone through the labs, CloudFormation (CFN) certainly address the the design principle of performing operations as code. Additionally, by deploying infrastructure as code, it enables engineers to make those frequent, small and reversible changes suggested by the pillar. Given that the same CFN template can be used in multiple stacks, I can see how CloudFormation could enable teams to anticipate failure as well.

In the scenario I'm thinking of, teams can use "green/blue" deployments to run identical environments in parallel. When changes are required, those small changes can be made to the which ever deployment is not the currently active or production deployment. If failure is introduced, the failure has been "anticipated" in a sense by having the non-active deployment (which would match the original state) ready to roll back to with little downtime and impact.

I shared some additional thoughts on CloudFormation in my part 1 post in this series.

# Systems Manager
An interesting service introduced here in the Operational Excellence pillar lab is the Systems Manager (SSM) service. Systems Manager is an agent based tool that, I would say, falls under the Configuration Management family of tools. It also aims to bring together a unified view of operational data from many AWS services across AWS accounts. The data and services provided by SSM allows teams to automate operational elements like inventory (hardware and software) collection, patching and compliance.

One of the major benefits to Systems Manager is that much of the functionality it provides is at no additional cost and the agent is pre-installed across the majority of AWS provided AMIs available for use with EC2. This makes it almost silly to not use the service, especially if an organization is all-in with AWS.

SSM provides paths to the design principles of learn from all operational failures, anticipate failure and performing operations as code at the least. The data and insights that can be gathered by using the service all work towards helping teams refine operations procedures frequently as well.

## Inventory Management
Systems Manager inventory gathering functionality is exceptionally helpful for organizations and security programs. If you are familiar with the [Center for Internet Security](https://www.cisecurity.org/ "CIS Homepage") (CIS) 20 Critical Controls, you'll know the first two are:

  1. Inventory and Control of Hardware Assets
  2. Inventory and Control of Software Assets

At the very least, SSM inventory assists in the collection of inventory data, however, with the use of SSM State Manager, there is also some degree of control of those assets.

 Inventory gathering can be configured in several ways, allowing Cloud Engineers to target things like capturing inventory on all assets, specific assets by tag or manually specifying instances. Additionally, the type of asset data to collect can also be fine tuned with options including:

  - Applications
  - AWS components
  - Network and system metadata
  - Files
  - Custom inventory elements you define
  - Windows specific:
    - Running services
    - Roles
    - Registry
  - etc

This can information collection can be an extremely helpful tool in understanding workloads in EC2 and meeting compliance requirements for asset inventory collection for both hardware and software.

Inventory collection (like many other System Manger features) relies on SSM State Manager to execute the tasks required for gathering inventory.

## State Manager
State Manager works with "associations" which are configuration information defining the desired state of an instance, bound (associated) to the target instance(s). The information defines what state the instances should be in, when and how often the state should association should execute for EC2 instances (and even on-prem instances in a hybrid environment) to ensure everything is in a consistent state.

Inventory collection is managed and achieved through State Manager and is essentially made up of four components in State Manager:
  
  1. State document
  2. Target instances
  3. A schedule
  4. Parameters

The fourth component is an optional component for State Manager, depending on the association or state document being used. In the case of inventory collection, it defines which inventory elements should be collected (see the list of inventory types above).

## Patch Manager
Patch Manager is another tool in the Systems Manager tool belt. Patch manager can be used to automate the application of security patches in both Windows and Linux. On Linux hosts, it can be used to apply non-security patches as well.
