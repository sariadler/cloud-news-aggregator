# Cloud News Aggregator

A cloud-based system for ingesting, processing, and displaying news articles in real time.

## 🚀 Overview
This project implements a scalable microservices architecture for collecting and processing news data.  
It uses message streaming and cloud-based storage to handle large volumes of data efficiently.

## 🧱 Architecture
The system is composed of multiple services:
- **Backend (FastAPI)** – handles API requests and business logic  
- **Consumer (Kafka)** – processes incoming data streams  
- **Frontend (Python UI)** – displays processed news articles  
- **Infrastructure (Docker)** – containerized deployment  

## ⚙️ Technologies
- Python (FastAPI)
- Kafka (message streaming)
- MongoDB Atlas (cloud database)
- Docker (containerization)

## ✨ Features
- Microservices-based architecture  
- Real-time data processing using Kafka  
- Scalable cloud storage with MongoDB Atlas  
- Containerized deployment with Docker  

## 🖥️ Run Locally
```bash
pip install -r frontend/requirements.txt
python -m frontend.app
