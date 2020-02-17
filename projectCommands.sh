# Requjirements.txt
pip3 freeze > requirements.txt
# or, only modules used.
pipreqs --force . 

pip3 install -r requirements.txt

# GIT

# Create from a folder
# 1. Create an empty repository on githib
#  i.e. Example
# 2. Run these commands
echo "# Example" >> README.md
git init
git add *
git commit -m "First commit"
git remote add origin https://github.com/scottrsmith/Example.git
git push -u origin master

# Checkin
git commit all
git push 

# Single file
git add file.py
git commit file.py
git push

# PIP8 -- clean up the code and check pip formatting
https://www.tutorialspoint.com/online_python_formatter.htm
http://pep8online.com/


# run Pip8 command line
pycodestyle --show-source --show-pep8 ./backend/src/api.py
pycodestyle --show-source --show-pep8 ./backend/src/database/models.py
pycodestyle --show-source --show-pep8 ./backend/src/auth/auth.py
#
# Documents
#
# Init the sphinx project
sphinx-quickstart

#
cd ..
m2r README.md README.rst --overwrite
cp -R README.rst ./docs/source
cd ./docs
make html
# Make pdf
make latexpdf
cd ..
cp -R ./docs/build/latex/robotclassify.pdf .
#
#
# Requirements.txt file
#
# ALL of the libes
pip3 freeze > requirements.txt
#
# Just what is used....
pipreqs .

#
# Docker
#
# Pull image
docker pull python:stretch

# 
# Run the image
docker run --name python -d python:stretch
#
#
# Example for 
docker pull postgres:latest
docker run --name psql -e POSTGRES_PASSWORD=password! -p 5432:5432 -d postgres:latest
psql -h 0.0.0.0 -p 5432 -U postgres
#
# See running iamges and
docker ps
docker images
docker run <name> -rm  # Remove afger running

#
# stop
docker stop <container id>

# From docker files (The Docker file in current directory)
docker build --tag <name> .

# Port--
docker run -p 80:8080 <name>

#
# Flask Example:
docker pull postgres:latest
docker build --tag jwt-api-test .
# Docker file:
		# Comment
		FROM python:stretch 

		# Copy to working directiry
		COPY . /app
		WORKDIR /app

		# Run shell command
		RUN pip install --upgrade pip
		RUN pip install -r requirements.txt

		ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8080", "main:APP"]

	#
docker run --env-file=env_file -p 80:8080 jwt-api-test 

#awscli: interact with AWS services
#eksctl: This command line tool allows you to run commands against a kubernetes cluster
#kubectl: This tool is used to interact with an existing cluster

#
# AWS Clusters
#
eksctl create cluster --name simple-jwt-api --region us-west-2
#
# Cloud Formation Console https://us-east-2.console.aws.amazon.com/cloudformation/


# Check health of the clustes
kubectl get nodes
# To delete the cluster
eksctl delete cluster --name simple-jwt-api

#
#
# ********** set up IAM role 
# Set account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
#
# Create a role policy document that allows the actions "eks:Describe*" and "ssm:GetParameters". 
TRUST="{ \"Version\": \"2012-10-17\", \"Statement\": [ { \"Effect\": \"Allow\", \"Principal\": { \"AWS\": \"arn:aws:iam::${ACCOUNT_ID}:root\" }, \"Action\": \"sts:AssumeRole\" } ] }"
#
# Create a role named 'UdacityFlaskDeployCBKubectlRole' using the role policy document
aws iam create-role --role-name UdacityFlaskDeployCBKubectlRole --assume-role-policy-document "$TRUST" --output text --query 'Role.Arn'
#
# Create a role policy document that also allows the actions "eks:Describe*" and "ssm:GetParameters".
echo '{ "Version": "2012-10-17", "Statement": [ { "Effect": "Allow", "Action": [ "eks:Describe*", "ssm:GetParameters" ], "Resource": "*" } ] }' > /tmp/iam-role-policy 
#
# Attach the policy to the 'UdacityFlaskDeployCBKubectlRole'. You can do this using awscli:
aws iam put-role-policy --role-name UdacityFlaskDeployCBKubectlRole --policy-name eks-describe --policy-document file:///tmp/iam-role-policy
# 
# You have now created a role named 'UdacityFlaskDeployCBKubectlRole'
#
#
# Grant the role access to the cluster. The 'aws-auth ConfigMap' is used to grant role based 
# access control to your cluster.
#
# Get the current configmap and save it to a file
kubectl get -n kube-system configmap/aws-auth -o yaml > /tmp/aws-auth-patch.yml
#
# In the data/mapRoles section of this document add, replacing <ACCOUNT_ID> with your account id:

		- rolearn: arn:aws:iam::054983937045:role/UdacityFlaskDeployCBKubectlRole
			username: build
			groups:
			- system:masters
#
# Now update your cluster's configmap:
kubectl patch configmap/aws-auth -n kube-system --patch "$(cat /tmp/aws-auth-patch.yml)"
#
# ALTERNATIVE
#
ACCOUNT_ID='054983937045'
ROLE="    - rolearn: arn:aws:iam::054983937045:role/UdacityFlaskDeployCBKubectlRole\n      username: build\n      groups:\n        - system:masters"
kubectl get -n kube-system configmap/aws-auth -o yaml | awk "/mapRoles: \|/{print;print \"$ROLE\";next}1" > /tmp/aws-auth-patch.yml
kubectl patch configmap/aws-auth -n kube-system --patch "$(cat /tmp/aws-auth-patch.yml)"


# Generate a GitHub access token
#

# buildspec.yml instructs CodeBuild. We need a way to pass your jwt secret
		env:
			parameter-store:         
				JWT_SECRET: JWT_SECRET
#
# Put secret into AWS Parameter Store

aws ssm delete-parameter --name JWT_SECRET --region us-west-2
aws ssm put-parameter --name JWT_SECRET --value "52ace7f12f7c56819fe30b97defe66da7ade5e99" --type SecureString --region us-west-2

# Continious delivery
#
#
# Code pipeline : https://us-east-2.console.aws.amazon.com/codesuite/codepipeline/pipelines/

# IP !!!!!!
# a3f1824a02c4711ea84d80e7a7f67a8c-582421803.us-west-2.elb.amazonaws.com
#URL=a3f1824a02c4711ea84d80e7a7f67a8c-582421803.us-west-2.elb.amazonaws.com
URL=a178ffc472dc811ea875a0ef2971c77d-1793567985.us-west-2.elb.amazonaws.com
curl -H "Content-Type: application/json" -X POST ${URL}/
export TOKEN=` | jq -r '.token'`
curl --request GET ${URL}/contents -H "Authorization: Bearer ${TOKEN}" | jq
curl -H "Content-Type: application/json" -X POST ${URL}/
export TTOKEN=`python3 get_credentials.py | jq -r '.token'`

export TUSER=`python3 get_credentials.py | grep 'APP_TESTING_USERID'`
export TTOKEN=`python3 get_credentials.py | grep 'TOKEN'`




#
#!/bin/bash
vpc="vpc-0684ea2d773cbd7c8" 
aws ec2 describe-internet-gateways --filters 'Name=attachment.vpc-id,Values='$vpc --region us-west-2 | grep InternetGatewayId
aws ec2 describe-subnets --filters 'Name=vpc-id,Values='$vpc  --region us-west-2 | grep SubnetId
aws ec2 describe-route-tables --filters 'Name=vpc-id,Values='$vpc --region us-west-2 | grep RouteTableId
aws ec2 describe-network-acls --filters 'Name=vpc-id,Values='$vpc --region us-west-2 | grep NetworkAclId
aws ec2 describe-vpc-peering-connections --filters 'Name=requester-vpc-info.vpc-id,Values='$vpc  --region us-west-2 | grep VpcPeeringConnectionId
aws ec2 describe-vpc-endpoints --filters 'Name=vpc-id,Values='$vpc  --region us-west-2 | grep VpcEndpointId
aws ec2 describe-nat-gateways --filter 'Name=vpc-id,Values='$vpc  --region us-west-2 | grep NatGatewayId
aws ec2 describe-security-groups --filters 'Name=vpc-id,Values='$vpc  --region us-west-2 | grep GroupId
aws ec2 describe-instances --filters 'Name=vpc-id,Values='$vpc  --region us-west-2 | grep InstanceId
aws ec2 describe-vpn-connections --filters 'Name=vpc-id,Values='$vpc  --region us-west-2 | grep VpnConnectionId
aws ec2 describe-vpn-gateways --filters 'Name=attachment.vpc-id,Values='$vpc  --region us-west-2 | grep VpnGatewayId
aws ec2 describe-network-interfaces --filters 'Name=vpc-id,Values='$vpc  --region us-west-2 | grep NetworkInterfaceId


"InternetGatewayId": "igw-00ba194a08e4c5c23",
"SubnetId": "subnet-0e97d21e6ab8f6b93",
"RouteTableId": "rtb-0d9bb8d4cc68c9ee5",
"RouteTableId": "rtb-0d9bb8d4cc68c9ee5",
"NetworkAclId": "acl-0d65777c96c6dfb77",
"NetworkAclId": "acl-0d65777c96c6dfb77",
"GroupId": "sg-0044615e06115ad8a",
"GroupId": "sg-0044615e06115ad8a",
"GroupId": "sg-0e878a4585be83bf5",
"NetworkInterfaceId": "eni-09859dad0b4ba4213",

InternetGateway, VPC, SubnetPublicUSWEST2B, VPCGatewayAttachment

# Heroku
# https://robotclassify.herokuapp.com/ | https://git.heroku.com/robotclassify.git
#
# 
keroku create robotclassify
# Returns:  https://robotclassify.herokuapp.com/ | https://git.heroku.com/robotclassify.git
git remote add heroku https://git.heroku.com/robotclassify.git
heroku addons:create heroku-postgresql:hobby-dev --app robotclassify
heroku config --app robotclassify
# DATABASE_URL: postgres://qvkifkfipufjnh:718a3891226432160f9b4e82ae25eec0af091e3594cde17db016548d74e55045@ec2-174-129-32-212.compute-1.amazonaws.com:5432/d8k8ns1lsffrjs

git push heroku master
heroku run python manage.py db upgrade --app robotclassify


#
# MIGTRATIONS 
#  1. Add code to config: migrate = Migrate(app, db)
# Create flask migrtations folder
flask db init
# 
# Create version in version folder
flask db migrate
#
# run the upgrade
flask db upgrade



curl --request POST --url 'http://127.0.0.1:5000/venues/1/edit' --header 'content-type: application/json' 



https://dev-p35ewo73.auth0.com/authorize?audience=robotclassify&response_type=token&client_id=924mOUHAkgolmjZN1hT30dpkUYQl8EU9&redirect_uri=http://127.0.0.1:5000/callback

https://127.0.0.1:8080/login-results#access_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Ik1rUkdRalkyUVRNNU56UTVNemt4UkRZM09UQTFOREU1UXpBeVJUTTNSVGxFUlVZNU9URkZOQSJ9.eyJpc3MiOiJodHRwczovL2Rldi1wMzVld283My5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWRlNWIyYjc3NjlhMmQwZWQzYWY4ZGU1IiwiYXVkIjoiY29mZmVlIiwiaWF0IjoxNTc1MzQwMTMwLCJleHAiOjE1NzUzNDczMzAsImF6cCI6Iks3OWlkTnkwZ1YwQnpKVUQ2UWhka3FDUm4wWnVuZTB5Iiwic2NvcGUiOiIifQ.NDWOPrVxAmLc7tKsoIf5uwWJwZmBPRhtM9tDxnNvl3_-qr1piBhXR_a6VPEzJc2pJmXf5uCIHRPlSLtLDD8E-LPKj4-g86YK-VFE9zAbEir1fCrE5-xrL-JhHeKHN65Lx9zxbFBeOM76DLeT_JiVB-gpk317K2YypV_T_ojEskiHVodJ9jJRqQU89Is-cnwfG-

http://127.0.0.1:5000/callback#access_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Ik1rUkdRalkyUVRNNU56UTVNemt4UkRZM09UQTFOREU1UXpBeVJUTTNSVGxFUlVZNU9URkZOQSJ9.eyJpc3MiOiJodHRwczovL2Rldi1wMzVld283My5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMDE3NzkyNTg3OTY1NTcwMjg3MTciLCJhdWQiOlsicm9ib3RjbGFzc2lmeSIsImh0dHBzOi8vZGV2LXAzNWV3bzczLmF1dGgwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE1Nzg0MzgzMDksImV4cCI6MTU3ODQ0NTUwOSwiYXpwIjoiOTI0bU9VSEFrZ29sbWpaTjFoVDMwZHBrVVlRbDhFVTkiLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFkbWluIiwicG9zdDphZG1pbiJdfQ.qxx11RPME29HQwcb4Xpdwl-AL9LQRF8jDrz2pFRHdQ7MnoQP_ZqeALY9M8p3RszjcWtdQRTPKpwWKzxhmWVGor0Vs-ks2GJgyhfEIhVcd_2MHFSxxXsXiDNByxcHe5KObCYa6TsA0LhxE5PWmBqdlSBvbLaq6o0WzTJCnj9hHD5_bJeNYTthoIccHlq5iQ2T4f6abvViopen_Wonnu5mu3yhCRwlNcoWhHxYZxAjKJcHpoBJa3YEx5SzKrRlhXR6Jqq2lXsqtL58Gf8-phLYPY2G8TANqmPtR-UjW6jNgKazAKsQLJPtCC9D6cGjQZpD4ugS-POTQDKjPoc0hnFfYA&scope=openid%20profile%20email&expires_in=7200&token_type=Bearer&state=g6Fo2SBxSV83M3ZGa1NxdW16aHdRbmU5NW9lcUY2a0p1WnBxT6N0aWTZIHZXalp1SE1yYVA4REEtcnFGbmVCcXJFb3UwbkZubHl0o2NpZNkgOTI0bU9VSEFrZ29sbWpaTjFoVDMwZHBrVVlRbDhFVTk