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
