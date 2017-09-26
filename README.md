# Udacity Catalog app project
This project is for for Udacity's **Full Stack nanodegree program**.
This is a small web application that provides list of items within a variety of categories and integrates third party user registration and authentication.
Authenticated users can create, edit and delete items, aswell as create new categories.

## Table of contents
* [Setting up](#setting-up)
  * [Setting up the development environment](#1-setting-up-the-development-environment)
  * [Downloading the repository](#2-downloading-the-repository)
  * [Setting up the database](#3-installing-dependencies)
  * [Running the project](#4-running-the-project)
* [Authentication](#authentication)
* [Images](#preview-images)

# Setting up
Follow these steps to successfully run the application.

### 1. Setting up the development environment
To make sure you have all the required dependicies to run this project, you should set up [Udacity's fullstack-nanodegree virtual machine](https://github.com/udacity/fullstack-nanodegree-vm)
using [Vagrant](https://www.vagrantup.com/).
1. Install Vagrant
2. Pick a location to store this VM and run `git clone https://github.com/udacity/fullstack-nanodegree-vm`
3. Navigate to the `fullstack-nanodegree-vm/vagrant` directory
4. Run the VM with `vagrant up`
5. After the setup is done, connect to the VM with `vagrant ssh`

### 2. Downloading the repository
Now it's time to obtain the project files.
1. Navigate to vagrant's shared folder (`fullstack-nanodegree-vm/vagrant`)
2. Clone this repository `git clone https://github.com/raideer/udacity-project-catalog`

### 3. Installing dependencies
This project requires some additional python packages
1. Go to your VM (after running vagrant ssh) and navigate to this repo's location cd /vagrant/udacity-project-catalog
2. Run `pip install -r requirements.txt`

### 4. Running the project
To run the project, just type `python project.py` and python flask will handle the rest

# Authentication
This project implements 3 oAuth providers: twitter, google and facebook. The system is based on Miguel Grinberg's post about implementing multiple
OAuth2 providers with flask using `rauth` package.

# Preview images
![Main page](https://i.imgur.com/CNbIIud.png)
![Item creation](https://i.imgur.com/IHYN58n.png)
![Catalog](https://i.imgur.com/gEscPHB.png)
![Auth options](https://i.imgur.com/QEpH8ME.png)
