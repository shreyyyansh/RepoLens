# RepoLens — AI-Powered GitHub Repository Explorer

RepoLens is an intelligent web app that analyzes GitHub organizations and provides concise, AI-generated summaries and repository metrics.  
Built using **Flask (Backend)** and **HTML/CSS/JS (Frontend)**, RepoLens integrates with the **GitHub API** and is designed for **AWS Hackathon Deployment** (Lambda + DynamoDB + Bedrock).

---

## Features

- Analyze any **public GitHub organization**
- Generate **AI summaries** of repositories (via Amazon Bedrock / Local fallback)
- Sort and explore repos by **Stars**, **Activity**, or **Update Date**
- Save structured results into AWS **DynamoDB**
- Fully responsive **frontend UI**
- Future-ready for **serverless AWS deployment**

---

## Architecture Overview

Below is the system flow of RepoLens:

```plantuml
@startuml
!theme vibrant
actor User
participant "Frontend (Browser)" as Frontend
participant "Flask API / AWS Lambda" as Backend
participant "GitHub API" as GitHub
participant "Amazon Bedrock" as Bedrock
participant "DynamoDB" as DB

User -> Frontend: Enters organization name
Frontend -> Backend: POST /analyze { org: "vercel" }
Backend -> GitHub: Fetch public repos
loop For each repo
  Backend -> GitHub: Fetch README
  Backend -> Bedrock: Generate AI summary
  Backend -> DB: Save structured data
end
Backend --> Frontend: Return analysis report
Frontend -> User: Display sorted cards
@enduml
