## Central Node README

### Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
   - [Central Node](#central-node)
3. [Key Features](#key-features)
4. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Local Setup](#local-setup)
   - [Environment Configuration](#environment-configuration)
   - [Usage](#usage)
5. [Conclusion](#conclusion)

---

### Overview <a name="overview"></a>
The central node is designed to coordinate, monitor, and facilitate the training of machine learning models on various nodes. It bridges communication between the Unity client and the training nodes, ensuring the seamless and efficient orchestration of ML training tasks.

### Architecture <a name="architecture"></a>
#### Central Node <a name="central-node"></a>
- **Role**: Acts as a pivotal point, receiving training job details from the Unity client, storing job data, managing real-time feedback, and handling model storage and retrieval.
- **Components**:
  - **Database**: Uses an AWS-hosted PostgreSQL database to persistently store training job details.
  - **Messaging Queue**: Utilizes RabbitMQ hosted on AWS to manage training tasks and communicate job statuses.
  - **Real-time Connection**: Establishes a WebSocket connection with the client to relay real-time training feedback including metrics, and environmental state for reproducibility.

### Key Features <a name="key-features"></a>
1. **Job Details Management**: Upon receiving the job details from the Unity client:
   - Data is stored in the AWS PostgreSQL database.
   - Training tasks are enqueued in RabbitMQ for processing by the training nodes.

2. **Real-time Feedback**:
   - Training metrics, environmental states, and other feedback are communicated back to the Unity client over the WebSocket connection.

3. **Status Updates**:
   - The server receives training status updates from the training nodes via the RabbitMQ queue and then updates the database with this status.
   - The updated status is also relayed to the Unity client through the WebSocket connection.

4. **Model Storage and Retrieval**:
   - Once a training node completes a training task, the resulting model is stored in an AWS S3 bucket.
   - The model is immediately sent to the Unity client over the WebSocket connection if connected.
   - In cases where the client is not connected, it has the option to fetch the model later via a GET request.

5. **Docker Integration**:
   - The repository includes a `docker-compose` file which spins up instances of RabbitMQ and PostgreSQL. This facilitates easy local testing and development.

### Getting Started <a name="getting-started"></a>
#### Prerequisites <a name="prerequisites"></a>
- Ensure you have Docker and Docker Compose installed.


#### Local Setup <a name="local-setup"></a>
- Clone the repository.
- Navigate to the project root.
- Run `docker-compose up` to initiate the Central node, RabbitMQ, PostgreSQL and PGAdmin services.

#### Environment Configuration <a name="environment-configuration"></a>
- Remove the .sample of the env.smaple, that will be loaded by the docker compose.


### Conclusion <a name="conclusion"></a>
The Train Jobs Coordinator Server provides a robust and scalable architecture to streamline the process of ML model training. While this README focuses on the central node, be sure to check the companion README for details about the training nodes.

