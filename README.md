<p align="center">
    <br>
    <img src="images/logo.png" width="400"/>
    <br>
<p>
<p align="center">
    <!-- Going to also have licens, release version, paper doi, twitter, etc. here -->
    <a href="https://square.ukp-lab.de/">
        <img alt="Website" src="https://img.shields.io/website?up_message=online&url=https%3A%2F%2Fsquare.ukp-lab.de%2F">
    </a>
    <a href="https://square.ukp-lab.de/docs/">
        <img alt="Docs" src="https://img.shields.io/badge/docs-available-brightgreen">
    </a>
    <a href="https://github.com/UKP-SQuARE/square-core">
        <img alt="Repo" src="https://badges.frapsoft.com/os/v1/open-source.svg?v=103">
    </a>
</p>


<h3 align="center">
    <p>Flexible and Extensible Question Answering Platform</p>
</h3>

<!-- Introduction of SQuARE -->
SQuARE is a flexible and extensible Question Answering (QA) platform to enable users to easily implement, manage and share their custom QA pipelines (aka Skills in SQuARE).

Two ways are supported to use SQuARE:
1. 🌐 Get access to the existing QA Skills (and even deploy your Skill!) via our [demo page](https://square.ukp-lab.de/);
2. 💾 Or clone and install SQuARE to host services on a local machine.

## Why SQuARE?

Recent advances in NLP and information retrieval have given rise to a diverse set of question answering tasks that are of different formats (e.g., extractive, abstractive), require different model architectures (e.g., generative, discriminative) and setups (e.g., with or without retrieval). Despite having a large number of powerful, specialized QA pipelines (a.k.a., Skills) that consider a single domain, model or setup, there exists no framework where users can easily explore and compare such pipelines and can extend them according to their needs. 

To address this issue, we present SQuARE, an extensible online QA platform for researchers which allows users to query and analyze a large collection of modern Skills via a user-friendly web interface and integrated behavioural tests. In addition, QA researchers can develop, manage and share their custom Skills using our microservices that support a wide range of models (Transformers, Adapters, ONNX), datastores and retrieval techniques (e.g., sparse and dense).

Find out more about the project on [UKPs Website](https://www.informatik.tu-darmstadt.de/ukp/research_ukp/ukp_research_projects/ukp_project_square/ukp_project_square_details.en.jsp).  

## Get Started
👉 If you want to use the SQuARE public service online, you can refer to [Online Service](#Online-Service) for using the existing skills and refer to 
[Add New Skills](#Add-New-Skills) for adding new skills.

👉 If you want to deploy SQuARE locally yourself, please refer to [Local Installation](#Local-Installation).

👉 For illustration of the architecture, please refer to [Architecture](#Architecture).

👉 And welcome to [contact us](#Contact).

## Online Service
Try out the on-the-go skills on the [demo page](https://square.ukp-lab.de/)! The existing skills include span-extraction, abstractive, multi-choice QA with contexts or without contexts (open QA based on retrieval).
<details open>
    <summary>Screenshot</summary>
    <p align="center">
        <br>
        <img src="images/demo-page.png" width="800"/>
        <br>
    <p>
</details>

## Add New Skills

### Step 1: Hosting New Skills
- If you want to add new skills to the [public service](https://square.ukp-lab.de/), please follow the skill-package examples (e.g. [skills/qa-retrieve-span-skill](skills/qa-retrieve-span-skill)) and submit yours via a [pull request](https://github.com/UKP-SQuARE/square-core/pulls). We will make it run after code review;
- It is also OK to host the skill yourself somewhere else. The only thing that matters here is to provide a URL and also match the argument formats.

### Step 2: Register the Skill
Go to your user profile and click on "My Skills" and "New" buttons. Fill out the form and link it to the hosted skills:

<details open>
    <summary>Example: Skill Form Filling</summary>
    <p align="center">
        <br>
        <img src="images/link_skill.png" width="800"/>
        <br>
    <p>
</details>

## Local Installation
### Requirements
For generating the docker-compose file we use [ytt](https://carvel.dev/ytt/) that can installed from [here](https://carvel.dev/ytt/docs/latest/install/) or via brew:
```bash
brew instal ytt
```
### Environment Configuration
Many of the services requires secrets that are set in environment files. Run the `[init_env_file.sh](./init_env_files.sh)` file:
```bash
bash init_env_files.sh
```
Next, we need to setup the authentication. For this we need to run a subset of the services. So first we [generate the docker-compose file](#generate-the-docker-compose-file):

Then we start traefik, keylcoak and postgres:
```bash
docker-compose up -d traefik keycloak postgres
```
Next go to [square.ukp-lab.localhost/auth](https://square.ukp-lab.localhost/auth) and login with the username `admin` and the keycloak password set in `./keycloak/.env`. On the left hand side create a new realm called `square`. Then follow the [instructions in the square-auth package](https://github.com/UKP-SQuARE/square-auth#register-a-client-in-keycloak) to set up clients for the skill-manager, datastores and models. Copy their CLIENT_SECRET and set it in ./skill-manager/.env ./datastore-api./env and ./square-model-inference-api/management_server/.env. Finally bring down the servies again with:
```bash
docker-compose down
```

### Generate the docker-compose file
The docker-compose file is generated using the [ytt](https://carvel.dev/ytt/) templating tool. First, we need to update the [config.yaml](config.yaml) to the target platform.
- Set _environment_ to `local`
- Set _os_ to your operating system, e.g. `linux`, `mac` or `windows`
Now we can generate the docker-compose.yaml file by running:
```bash
ytt -f docker-compose.ytt.yaml -f config.yaml >> docker-compose.yaml  
```
### Get docker images
We now can pull the existing docker images from docker hub by running:
```bash
docker-compose pull
```
In order to inject the updated environment variables in the frontend, we need to rebuild it:
```bash
docker-compose build frontend
```
### Run 
```bash
docker-compose up -d
```
Check with `docker-compose logs -f` if all systems have started successfully. Once they are up and running go to https://square.ukp-lab.localhost.
👉 Accept that the browser cannot verify the certificate.
👉 enable the flag [chrome://flags/#allow-insecure-localhost](chrome://flags/#allow-insecure-localhost) in Chrome.
### Add Skills
Add Skills according to the [Add New Skills](#Add-New-Skills) section. Note that, for open-domain skills the datastore need to created first.

## Architecture
For a whole (open QA) skill pipeline, it requires 6 steps:
1. First a user selects a Skill and issues a query via the user interface;
2. The selected QA Skill forwards the query to the respective Datastore for document retrieval;
3. The Datastore gets the query embedding from the Models, uses it for semantic document retrieval and returns the top documents to the Skill;
4. The Skill sends the query and retrieved documents to the reader model for answer extraction;
5. Finally, the answers are shown to the user;
6. Optionally, the user can view the results of the predefined behavioural tests for the Skill. 
<p align="center">
        <br>
        <img src="images/architecture.png" width="800"/>
        <br>
    <p>

## Contact

<!-- If you find this repository helpful, feel free to cite our publication [UKP-SQUARE: An Online Platform for Question Answering Research]():

```
@inproceedings{
}
``` -->

The main contributors of this repository are:
- [Tim Baumgärtner](https://github.com/timbmg), [Kexin Wang](https://github.com/kwang2049), [Rachneet Singh Sachdeva](https://github.com/Rachneet), [
Max Eichler](https://github.com/maexe), [Gregor Geigle](https://github.com/gregor-ge), [Clifton Poth](https://github.com/calpt), [Hannah Sterz](https://github.com/hSterz)

Contact person: [Tim Baumgärtner](mailto:baumgaertner@ukp.informatik.tu-darmstadt.de) (Skills and general questions), [Kexin Wang](mailto:kexin.wang.2049@gmail.com) (Datastores), [Rachneet Singh Sachdeva](mailto:sachdeva@ukp.informatik.tu-darmstadt.de) (Models)

[https://www.ukp.tu-darmstadt.de/](https://www.ukp.tu-darmstadt.de/)

Don't hesitate to send us an e-mail or report an issue, if something is broken (and it shouldn't be) or if you have further questions.

> This repository contains experimental software and is published for the sole purpose of giving additional background details on the respective publication.
