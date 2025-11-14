# Cloud Architecture

```mermaid
flowchart TB
    subgraph Account[Gov Cloud Account]
      direction LR
      subgraph Net[VPC Private Subnets]
        Fargate[ECS Fargate Tasks\nsg-tax-pipeline]
        SFN[Step Functions\nOrchestrator]
      end
      S3[(S3 Data Lake\nlanding/raw/curated)]
      Glue[Glue Data Catalog + Crawler]
      Athena[Athena Workgroup]
      LF[Lake Formation]
      KMS[KMS Keys]
      CW[CloudWatch Logs]
      EB[EventBridge Scheduler]
      IAM[IAM Roles]
    end

    EB --> SFN --> Fargate
    Fargate --> S3
    Fargate --> CW
    S3 --> Glue --> Athena
    LF --> Athena
    LF --> Glue
    KMS --> S3
```

- **S3** hosts landing/raw/curated data (encrypted with KMS, versioned).
- **Step Functions** orchestrates retries around an **ECS Fargate** task running the Dockerized pipeline.
- **Glue + Athena + Lake Formation** provide SQL and secure analytics for downstream consumers.
- Logs go to **CloudWatch Logs**, with JSON formatting in container environments.
