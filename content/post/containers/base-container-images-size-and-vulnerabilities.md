---
title: "Base Container Image Size and Vulnerabilities"
date: 2023-01-28T18:35:16-07:00
draft: false
toc: true
images:
tags:
 - containers
 - python
 - distroless
 - reference
---

What do you do when there are constantly vulnerabilities in production? Well, if your product runs heavily in containers, trying to deal with them before they make it into production is an option. In this post, I'm going to look at packaging a small Python code base in images of various sizes and how that can affect vulnerability counts in the end "product".

I'm going to use Python for this because it's a language I'm comfortable with. It will be an extremely simple, FastAPI "Hello, World" application.

## The App
For this post, I'm using a very basic 5-line FastAPI application to illustrate how the base image can play a role in adding to vulnerability counts. Of course, the larger the application and the more Python packages and dependencies, the higher the vuln count is likely to go.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
 return {"message": "Hello, World!"}
```

## A Full-Fat Base Image
This example is intended to have a larger base image. Using the official Python 3 image on Docker Hub, the FastAPI requirements are installed and `main.py` is copied over so the app will run. The Dockerfile to build the image looks like this:

```docker
FROM python:3

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN apt update && apt install -y python3 python3-pip 
RUN pip3 install --no-cache-dir --upgrade -r /app/requirements.txt
COPY ./main.py /app/
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

```

The Dockerfile is pretty straightforward. After copying files in and installing the necessary dependencies, the final line runs `uvicorn`. Uvicorn is an Asynchronous Server Gateway Interface that serves the FastAPI app.

To build the image, the usual build command is executed:

```bash
❯ docker image build -t helloworld:python3 .
```

Looking at the image, it's 930MB in size

```bash
❯ docker images
REPOSITORY TAG IMAGE ID CREATED SIZE
helloworld python3 26a9da5549bd 49 minutes ago 930MB
```

For image scanning, I'm using [Aqua Security's Trivy][trivy]. I'm also omitting low severity vulns as in my experience -- they tend to hang around, even in production, in perpetuity.

Here are the results from Trivy:

```bash
❯ trivy image -s CRITICAL,HIGH,MEDIUM helloworld:python3

helloworld:python3 (debian 11.6)

Total: 511 (MEDIUM: 270, HIGH: 221, CRITICAL: 20)
```
511 vulnerabilities between Python and the base Debian filesystem in a 930MB image. Next up, we'll try a slimmed-down version of the Python 3 image.

## The 2% Base Image
For this test, I'm using the `python:3-slim` image on Docker Hub and building the image as before (just with a different tag on my local system). The resulting image is 18% smaller - let's see how this impacts the vuln count.

```bash
❯ docker images
REPOSITORY TAG IMAGE ID CREATED SIZE
helloworld python3-slim def48f697e11 15 seconds ago 169MB
helloworld python3 26a9da5549bd 10 hours ago 930MB
```

The Trivy scan results are remarkably different too with the vuln count down to just 19 total:

```bash
❯ trivy image -s CRITICAL,HIGH,MEDIUM helloworld:python3-slim

helloworld:python3-slim (debian 11.6)

Total: 19 (MEDIUM: 6, HIGH: 12, CRITICAL: 1)
```

## Distroless - the 1% Base Image
For this image, I'm going to build it a little differently. Using a [multi-stage image][multi], the FastAPI dependencies will be downloaded and installed. Then, everything required to make the Hello World app run will be copied to the Python3 [distroless image][distroless] (which has a starting size of just 50.2MB).

The Dockerfile looks like this:

```docker
FROM python:3-slim AS build-env

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt && cp $(which uvicorn) /app
COPY ./main.py /app/main.py

FROM gcr.io/distroless/python3
COPY --from=build-env /app /app
COPY --from=build-env /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages
WORKDIR /app
CMD ["./uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
```

Using `python:3-slim`, the requirements file is copied to the container, and `pip` is invoked to install everything needed by FastAPI to work. Additionally, `uvicorn` is copied to the `/app` directory so that it can be easily executed as the container entry point later on.

Next, everything we need to make the app work is copied from the build environment image to the distroless `python3` image, including Python packages installed from the requirements.txt file (the packages in site-packages). The environment variable `PYTHONPATH` is set to make sure the distroless image knows where our user modules/packages are located.

Finally, [`uvicorn`][uvi] is invoked as in previous images, except this time from the working directory as it's not in the environment path.

After all this setup, I was surprised that the distroless image wasn't as small as I thought it would be. 

```bash
❯ docker images
REPOSITORY TAG IMAGE ID CREATED SIZE
helloworld distroless d7b4d7200051 15 seconds ago 103MB
helloworld python3-slim def48f697e11 18 minutes ago 169MB
helloworld python3 26a9da5549bd 11 hours ago 930MB
gcr.io/distroless/python3 latest 2ebdeb07019d 4 days ago 50.2MB
```

The image size has basically doubled from the base distroless image. It will be interesting to see what the vuln scan comes back with.

```bash
❯ trivy image -s CRITICAL,HIGH,MEDIUM helloworld:distroless

helloworld:distroless (debian 11.6)

Total: 16 (MEDIUM: 5, HIGH: 9, CRITICAL: 2)
```

While the total vuln count is down by 3, the interesting thing is we've increased our count of critical severity vulnerabilities from 1 to 2. Also of interest is that a number of the vulnerabilities in the distroless image are as a result of Python. Upon investigation, it appears the distroless Python 3 image is running on Python 3.9.2 while the first two examples are currently Python 3.11.

## Conclusion

While I could go back and rebuild images using Python 3.9.2 (assuming image tags saying 3.9.2 can be trusted to be what they say they are), I think the point is made. It tends to be that the larger the image size, the greater the number of vulnerabilities. Were the distroless Python image running a more up-to-date version of Python, 10 of the vulnerabilities detected would likely not exist, bringing the count down to 6 total with only 1 critical and 3 highs.

Are distroless images a panacea to help reduce attack surface? Maybe, maybe not. Are they the solution to curbing time spent on vulnerability management efforts across multiple teams? Again, maybe and maybe not. What I get out of this exercise is that if there are options to reduce the count of components in a product deployment (such as minimal/slim or distroless images), it is worth putting in some time to investigate this with your product teams.

Vulnerability management is not just about plugging holes so attackers don't get in. Many times, CVEs have no known exploit. Sometimes, even if a PoC exploit exists, it only works in perfect conditions. Remote code execution type vulns are also not always that common, particularly when you throw the need of authentication in to the mix. But, internal vulnerability management policy often doesn't care about any of that. More often than not, policy just cares about CRITICAL, HIGH and MEDIUM and resolving those within their alloted time. 

Internal policy is typically set by the most concerned customer (an your contractual obligations to them), or the most "secure" compliance regulations we're bound by. Vulnerability management, I think, is often more about maintaining customer trust and holding on to compliance certifications when auditors come around. Let's face it - no one likes to do vulnerability management (especially security teams, contrary to popular belief 😉), but it takes a village to comply with what our customers expect. Minimal container images are one way to reduce the burden of toil on security, infrastructure, and product engineering teams.

[trivy]: https://www.aquasec.com/products/trivy/ "Trivy Product Page on aquasec.com"
[multi]: https://docs.docker.com/build/building/multi-stage/ "Docker Documentation on Multi-Stage Build"
[distroless]: https://github.com/GoogleContainerTools/distroless "GitHub Page for Distroless Images"
[uvi]: https://www.uvicorn.org/ "uvicorn Documentation"