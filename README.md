# 🛡️ ShieldOps — Secure Serverless API

A security-focused serverless REST API built with **Python, AWS Lambda, Amazon API Gateway, and AWS SAM**, with automated security scanning and CI/CD using **GitHub Actions**.

The project demonstrates how a lightweight serverless API can be designed with **secure coding practices, input validation, HTTP security headers, API throttling, automated SAST scanning, unit testing, and automated AWS deployment**.

---

## 🚀 Overview

**ShieldOps Secure Serverless API** is a demonstration project that combines serverless application development with DevSecOps practices.

The API provides a simple **Notes service** where users can:

* Create notes
* List notes
* Retrieve individual notes
* Delete notes

Security and engineering practices are integrated directly into the development pipeline rather than being treated as an afterthought.

---

## ✨ Key Features

### 🔐 Security

* Input validation for API requests
* UUID format validation for note IDs
* Request size restrictions
* Secure HTTP response headers
* `X-Content-Type-Options: nosniff`
* `Cache-Control: no-store`
* Generic internal error responses
* Structured logging
* API Gateway throttling
* Automated **Bandit SAST** scanning

### ⚡ Serverless Architecture

* AWS Lambda
* Amazon API Gateway
* AWS SAM
* Python 3.12
* Stateless serverless execution model

### 🔄 DevSecOps CI/CD

Every change going into `main` can pass through:

1. Dependency installation
2. Static Application Security Testing (SAST)
3. Unit testing
4. AWS SAM build
5. Automated deployment to AWS

The GitHub Actions workflow uses Bandit for SAST and pytest for unit tests before deployment.

---

## 🏗️ Architecture

```text
                    ┌──────────────────┐
                    │      Client      │
                    │ Browser / Postman│
                    └────────┬─────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │   Amazon API Gateway│
                  │                     │
                  │   /notes            │
                  │   /notes/{id}       │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │     AWS Lambda      │
                  │     Python 3.12     │
                  │                     │
                  │  Request Validation │
                  │  CRUD Operations    │
                  │  Error Handling     │
                  │  Security Headers   │
                  └──────────┬──────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ In-Memory Store │
                    │   Demo Data     │
                    └────────────────┘

            ┌───────────────────────────────┐
            │        GitHub Actions         │
            │                               │
            │  Bandit → Pytest → SAM Build │
            │              → Deploy        │
            └───────────────────────────────┘
```

The AWS SAM template configures Python 3.12 Lambda functions, API Gateway, active tracing, and API throttling with a 50-request/sec rate limit and burst limit of 20.

---

## 🧰 Tech Stack

| Technology             | Purpose                      |
| ---------------------- | ---------------------------- |
| **Python 3.12**        | Backend/API logic            |
| **AWS Lambda**         | Serverless compute           |
| **Amazon API Gateway** | REST API gateway             |
| **AWS SAM**            | Infrastructure & deployment  |
| **GitHub Actions**     | CI/CD automation             |
| **Bandit**             | Static security analysis     |
| **Pytest**             | Unit testing                 |
| **AWS IAM**            | Lambda execution permissions |

---

## 📁 Project Structure

```text
shieldops-secure-serverless-api/
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml
│
├── src/
│   └── app.py
│
├── tests/
│   └── test_app.py
│
├── requirements-dev.txt
├── template.yaml
├── .gitignore
└── README.md
```

---

## 🔌 API Endpoints

### Create a Note

```http
POST /notes
```

#### Request

```json
{
  "title": "Learn AWS Lambda",
  "body": "Build a secure serverless API."
}
```

#### Response

```json
{
  "id": "uuid",
  "title": "Learn AWS Lambda",
  "body": "Build a secure serverless API.",
  "created_at": "2026-08-14T00:00:00+00:00"
}
```

Returns:

```text
201 Created
```

---

### List Notes

```http
GET /notes
```

#### Response

```json
{
  "notes": [],
  "count": 0
}
```

Returns:

```text
200 OK
```

---

### Get a Note

```http
GET /notes/{id}
```

Returns the requested note when the UUID exists.

Possible responses:

```text
200 OK
400 Bad Request
404 Not Found
```

---

### Delete a Note

```http
DELETE /notes/{id}
```

#### Response

```json
{
  "message": "Note deleted"
}
```

Returns:

```text
200 OK
```

---

## 🛡️ Security Controls

### 1. Input Validation

The API validates:

* `title` must be a non-empty string
* Maximum title length: **100 characters**
* `body` must be a string
* Maximum body length: **2,000 characters**
* Note IDs must follow UUID format

These controls help prevent malformed requests from reaching application logic.

### 2. Secure HTTP Headers

Responses include:

```text
Content-Type: application/json
X-Content-Type-Options: nosniff
Cache-Control: no-store
```

This reduces unnecessary browser-side content sniffing and prevents response caching for the API.

### 3. API Throttling

API Gateway is configured with:

```text
Rate Limit:     50 requests/second
Burst Limit:    20 requests
```

This provides a basic layer of protection against excessive request volume.

### 4. Error Handling

Unexpected application exceptions are logged internally while the API returns a generic:

```json
{
  "error": "Internal server error"
}
```

This avoids exposing internal implementation details to clients.

---

## 🔍 DevSecOps Pipeline

The project uses GitHub Actions to automate security and deployment.

```text
       Git Push / Pull Request
                 │
                 ▼
        ┌─────────────────┐
        │ Checkout Source │
        └────────┬────────┘
                 ▼
        ┌─────────────────┐
        │ Setup Python 3.12│
        └────────┬────────┘
                 ▼
        ┌─────────────────┐
        │ Install Deps    │
        └────────┬────────┘
                 ▼
        ┌─────────────────┐
        │ Bandit SAST     │
        └────────┬────────┘
                 ▼
        ┌─────────────────┐
        │ Pytest          │
        └────────┬────────┘
                 ▼
          Tests Passed?
             /     \
           No       Yes
           │         │
         Stop        ▼
              ┌──────────────┐
              │ AWS SAM Build│
              └──────┬───────┘
                     ▼
              ┌──────────────┐
              │ AWS SAM Deploy│
              └──────────────┘
```

The deployment job runs only after the security-and-tests job succeeds and only for pushes to `main`. AWS credentials are supplied through GitHub repository secrets.

---

## 🧪 Running Tests

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run unit tests:

```bash
pytest tests/ -v
```

Run the security scan:

```bash
bandit -r src/ -f screen
```

The repository currently pins `pytest==8.3.3` and `bandit==1.7.9`.

---

## 💻 Run Locally

### Prerequisites

Install:

* Python 3.12
* AWS CLI
* AWS SAM CLI
* Git

Clone the repository:

```bash
git clone https://github.com/arjunpanwar963/shieldops-secure-serverless-api.git
cd shieldops-secure-serverless-api
```

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run tests:

```bash
pytest tests/ -v
```

Run the security scan:

```bash
bandit -r src/ -f screen
```

Build the SAM application:

```bash
sam build
```

Start the API locally:

```bash
sam local start-api
```

The API can then be tested through the local SAM endpoint.

---

## ☁️ Deploy to AWS

Build the application:

```bash
sam build
```

Deploy interactively:

```bash
sam deploy --guided
```

For automated CI/CD deployment, configure these GitHub repository secrets:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION
```

The existing workflow uses AWS SAM to build and deploy the stack with the `prod` stage.

---

## 📊 Serverless Configuration

The application uses:

```text
Runtime:        Python 3.12
Memory:         128 MB
Timeout:        10 seconds
Tracing:        Active
Stage:          prod
```

The API exposes:

```text
POST   /notes
GET    /notes
GET    /notes/{id}
DELETE /notes/{id}
```

The configuration is defined through AWS SAM in `template.yaml`.

---

## ⚠️ Current Storage Model

This project intentionally uses an **in-memory dictionary** as its storage layer.

```python
_NOTES_STORE = {}
```

This makes the project simple and suitable for demonstrating serverless API security and DevSecOps concepts.

However, in-memory Lambda storage is **not persistent** and may be lost when the Lambda execution environment is recycled.

### Production Upgrade

For a production implementation, the storage layer could be replaced with:

* Amazon DynamoDB
* Amazon Aurora Serverless
* Amazon RDS
* Another managed persistent datastore

A natural next step would be **DynamoDB + IAM least-privilege access**.

---

## 🔮 Future Improvements

* [ ] Integrate AWS WAF with API Gateway
* [ ] Add Amazon DynamoDB persistence
* [ ] Add authentication and authorization
* [ ] Implement JWT-based access control
* [ ] Add API Gateway access logging
* [ ] Add CloudWatch dashboards and alarms
* [ ] Add AWS X-Ray tracing analysis
* [ ] Add dependency vulnerability scanning
* [ ] Add secret detection
* [ ] Add rate-based WAF rules
* [ ] Add OpenAPI/Swagger documentation
* [ ] Add production-grade observability
* [ ] Add infrastructure security checks

---

## 🎯 Project Goals

This project was built to demonstrate practical understanding of:

**Cloud Security + Serverless Architecture + DevSecOps + CI/CD**

Rather than treating security as a separate final-stage activity, the project integrates security checks directly into the development pipeline.

> **Build fast. Deploy serverless. Secure everything.**

---

## 📚 What This Project Demonstrates

* Serverless REST API development
* AWS Lambda architecture
* API Gateway configuration
* AWS SAM infrastructure as code
* Secure API input validation
* Security-focused HTTP headers
* Automated AWS deployment
* Basic cloud security engineering
* API throttling
* Python exception handling
* Static Application Security Testing
* Automated unit testing
* GitHub Actions CI/CD

---

## 📄 License

This project is intended for educational and demonstration purposes.

--------------------------------------------------------------------------

⭐  If you found this project useful, consider giving the repository a star.
