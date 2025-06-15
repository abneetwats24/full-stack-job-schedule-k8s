# Async Processing Stack on Kubernetes

This repo holds **Helm charts** plus minimal service code implementing the architecture we discussed:

* FastAPI micro-services (`api`, `consumer`, `notification`)
* RabbitMQ + Redis + Postgres
* Official Apache Airflow chart (KubernetesExecutor)
* Vue 3 frontend
* Single umbrella Helm chart: `charts/stack`

Quick install (kind/minikube):
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add apache-airflow https://airflow.apache.org
helm dependency update charts/stack
helm install stack charts/stack -n async-stack --create-namespace \
  --set ingress.host=demo.local
```

Endpoints (after DNS / hosts entry):
* `https://demo.local/api/process` – submit job
* `https://demo.local/webhook`   – notification target
* `https://demo.local/airflow`   – Airflow UI (admin / admin)
```
helm uninstall stack -n async-stack  # cleanup
```

## Architecture Diagram

```mermaid
graph TD
    subgraph "Frontend (E)"
        E_Browser[User Browser / Mobile App]
    end

    subgraph "Kubernetes Cluster"
        subgraph "API Layer"
            Ingress[Kubernetes Ingress / LoadBalancer]
            A[API Server (A) - Pods]
        end

        subgraph "Messaging Layer"
            Q1[RabbitMQ Q1: Airflow Requests]
            Q2[RabbitMQ Q2: Airflow Results]
            C[Consumer Service (C) - Pods]
        end

        subgraph "Workflow Layer"
            Airflow_Scheduler[Airflow Scheduler]
            Airflow_Worker["Airflow Worker Pods (Kubernetes Executor)"]
            D_Processing[Airflow DAG Logic]
            D_FinalTask["Airflow DAG (D) - Final Task"]
        end

        subgraph "Notification Layer"
            N["Notification Service (N) - Pods"]
            Ingress_Frontend["Frontend's Webhook Endpoint"]
        end

        subgraph "Data Layer"
            DB[Database (Processed Data)]
        end

        Redis[Redis / Cache]
    end

    %% Connections outside subgraphs
    E_Browser --> Ingress
    Ingress --> A
    A -- "Stores correlation_id→callback_url" --> Redis
    A -- "Publishes Request" --> Q1
    Q1 --> C
    C -- "Triggers DAG with correlation_id" --> Airflow_Scheduler
    Airflow_Scheduler --> Airflow_Worker
    Airflow_Worker --> D_Processing
    D_Processing -- "Stores Processed Data" --> DB
    D_FinalTask -- "Publishes Result" --> Q2
    Q2 --> N
    N --> Redis
    N --> Ingress_Frontend
    N --> E_Browser
    E_Browser --> DB

    %% Styling
    style E_Browser fill:#ADD8E6,stroke:#333,stroke-width:2px
    style A fill:#DDA0DD,stroke:#333,stroke-width:2px
    style Redis fill:#FFDDC1,stroke:#333,stroke-width:2px
    style Q1 fill:#90EE90,stroke:#333,stroke-width:2px
    style C fill:#FFE4B5,stroke:#333,stroke-width:2px
    style Airflow_Scheduler fill:#ADD8E6,stroke:#333,stroke-width:2px
    style Airflow_Worker fill:#ADD8E6,stroke:#333,stroke-width:2px
    style D_Processing fill:#ADD8E6,stroke:#333,stroke-width:2px
    style D_FinalTask fill:#ADD8E6,stroke:#333,stroke-width:2px
    style Q2 fill:#90EE90,stroke:#333,stroke-width:2px
    style N fill:#BAE1FF,stroke:#333,stroke-width:2px
    style DB fill:#FAFAD2,stroke:#333,stroke-width:2px
    style Ingress fill:#F0FFF0,stroke:#333,stroke-width:2px
    style Ingress_Frontend fill:#F0FFF0,stroke:#333,stroke-width:2px

```
